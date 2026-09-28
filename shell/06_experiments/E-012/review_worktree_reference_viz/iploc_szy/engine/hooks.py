"""Runner hooks for integrity checks, logging, and artifact publication."""

import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from .messages import ConsoleTrainingMessageBus, TrainingProgressMessage
from ..registry import HOOKS
from ..utils.distributed import gather_objects

if TYPE_CHECKING:
    from .runner import SFTLoRARunner


class Hook:
    """Base hook with no-op lifecycle methods."""

    priority = 50

    def before_run(self, runner: "SFTLoRARunner") -> None:
        """Run before baseline evaluation and optimization."""

    def after_train_step(self, runner: "SFTLoRARunner") -> None:
        """Run after each optimizer step."""

    def after_run(self, runner: "SFTLoRARunner") -> None:
        """Run after final metrics have been assembled."""


@HOOKS.register_module()
class FiniteHook(Hook):
    """Abort immediately when loss or LoRA gradients become non-finite."""

    priority = 10

    def after_train_step(self, runner: "SFTLoRARunner") -> None:
        """Validate the latest loss and all available LoRA gradients."""
        loss = runner.history[-1]
        if not math.isfinite(loss):
            raise RuntimeError(f"non-finite loss at step {runner.step}: {loss}")
        if runner.finite_grad_fraction != 1.0:
            raise RuntimeError(
                f"non-finite LoRA gradients at step {runner.step}: "
                f"finite_fraction={runner.finite_grad_fraction}"
            )


@HOOKS.register_module()
class LoggerHook(Hook):
    """Emit rank-zero, human-readable training progress after every step."""

    def __init__(self) -> None:
        self.messages = ConsoleTrainingMessageBus()

    def after_train_step(self, runner: "SFTLoRARunner") -> None:
        """Print loss, ETA, throughput, learning rate, and peak memory."""
        if not runner.is_main_process:
            return
        elapsed = max(
            time.perf_counter() - (runner.training_started_at or time.perf_counter()),
            1e-9,
        )
        session_steps = max(1, runner.step - runner.run_start_step)
        samples_seen = runner.samples_seen
        session_samples_seen = samples_seen - runner.run_start_samples_seen
        import torch

        self.messages.emit(
            TrainingProgressMessage(
                step=runner.step,
                total_steps=runner.max_steps,
                loss=runner.history[-1],
                learning_rate=runner.current_learning_rate,
                step_seconds=runner.step_duration_seconds,
                mean_step_seconds=elapsed / session_steps,
                samples_seen=samples_seen,
                examples_per_second=session_samples_seen / elapsed,
                peak_memory_gib=torch.cuda.max_memory_allocated() / 2**30,
                localization_metrics=runner.latest_localization_metrics,
            )
        )


@HOOKS.register_module()
class TrainingHistoryHook(Hook):
    """Append durable rank-zero step records for loss-curve analysis."""

    priority = 60

    def before_run(self, runner: "SFTLoRARunner") -> None:
        if not runner.is_main_process:
            return
        self._append(
            runner,
            {
                "event": "run_start",
                "initialized_from": runner.initialized_from or None,
                "resumed_from": runner.resumed_from or None,
                "start_step": runner.run_start_step,
                "start_samples_seen": runner.run_start_samples_seen,
                "total_steps": runner.max_steps,
                "dataset_size": len(runner.dataset),
                "updates_per_epoch": runner.updates_per_epoch,
                "effective_global_batch_size": runner.samples_per_update,
                "world_size": runner.world_size,
                "per_device_batch_size": runner.batch_size,
                "gradient_accumulation_steps": runner.gradient_accumulation_steps,
                "warmup_ratio": runner.warmup_ratio,
                "max_grad_norm": runner.max_grad_norm,
                "seed": runner.seed,
            },
        )

    def after_train_step(self, runner: "SFTLoRARunner") -> None:
        if not runner.is_main_process:
            return
        import torch

        elapsed = max(
            time.perf_counter() - (runner.training_started_at or time.perf_counter()),
            1e-9,
        )
        session_steps = max(1, runner.step - runner.run_start_step)
        session_samples = runner.samples_seen - runner.run_start_samples_seen
        mean_step_seconds = elapsed / session_steps
        self._append(
            runner,
            {
                "event": "train_step",
                "step": runner.step,
                "total_steps": runner.max_steps,
                "nominal_epoch": runner.samples_seen / len(runner.dataset),
                "loss": runner.history[-1],
                "learning_rate": runner.current_learning_rate,
                "step_seconds": runner.step_duration_seconds,
                "mean_step_seconds": mean_step_seconds,
                "eta_seconds": max(0, runner.max_steps - runner.step) * mean_step_seconds,
                "samples_seen": runner.samples_seen,
                "session_samples_seen": session_samples,
                "examples_per_second": session_samples / elapsed,
                "finite_grad_fraction": runner.finite_grad_fraction,
                "peak_memory_gib_rank0": torch.cuda.max_memory_allocated() / 2**30,
                "next_checkpoint_samples": runner.next_checkpoint_samples,
                **runner.latest_localization_metrics,
                **runner.latest_auxiliary_metrics,
            },
        )

    def after_run(self, runner: "SFTLoRARunner") -> None:
        if runner.is_main_process:
            self._append(
                runner,
                {
                    "event": "run_complete",
                    "step": runner.step,
                    "samples_seen": runner.samples_seen,
                    "status": runner.metrics.get("status"),
                    "loss_before": runner.metrics.get("loss_before"),
                    "loss_after": runner.metrics.get("loss_after"),
                    "train_seconds": runner.metrics.get("train_seconds"),
                },
            )

    @staticmethod
    def _append(runner: "SFTLoRARunner", payload: dict) -> None:
        log_path = Path(runner.work_dir) / "logs" / "train_steps.jsonl"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            **payload,
        }
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())


@HOOKS.register_module()
class GpuMemoryHook(Hook):
    """Record peak allocated memory for model-parallel or DDP execution."""

    def after_run(self, runner: "SFTLoRARunner") -> None:
        """Gather one local peak per DDP rank, or all visible-device peaks."""
        import torch

        if runner.world_size > 1:
            local_peak = torch.cuda.max_memory_allocated() / 2**30
            peaks = gather_objects(local_peak, runner.context)
            runner.metrics["peak_gpu_memory_gib_by_rank"] = peaks
        else:
            runner.metrics["peak_gpu_memory_gib"] = [
                torch.cuda.max_memory_allocated(device) / 2**30
                for device in range(torch.cuda.device_count())
            ]


@HOOKS.register_module()
class MetricsWriterHook(Hook):
    """Atomically publish bounded metrics on rank zero only."""

    priority = 90

    def after_run(self, runner: "SFTLoRARunner") -> None:
        """Write final metrics through a same-directory atomic rename."""
        if not runner.is_main_process:
            return
        metrics_path = Path(runner.work_dir) / "metrics.json"
        temporary_path = metrics_path.with_suffix(".json.tmp")
        temporary_path.write_text(
            json.dumps(runner.metrics, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary_path, metrics_path)
