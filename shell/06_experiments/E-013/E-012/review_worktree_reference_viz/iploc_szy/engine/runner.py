"""Bounded LoRA SFT runner supporting legacy model sharding and optional DDP."""

import math
import random
import time
from contextlib import nullcontext
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import torch

from ..checkpointing import load_adapter_checkpoint, validate_checkpoint
from ..evaluation.bbox import box_iou
from ..prompting.coordinates import parse_box
from ..registry import AUXILIARY_LOSSES, HOOKS, RUNNERS
from ..utils.distributed import barrier, gather_objects, mean_scalar
from .pipeline import TrainingPipeline


@RUNNERS.register_module()
class SFTLoRARunner:
    """Run LoRA SFT with per-rank batches and rank-aware artifact handling."""

    def __init__(
        self,
        model: Any,
        dataset: Any,
        collator: Any,
        work_dir: str,
        max_steps: Optional[int] = None,
        max_epochs: Optional[float] = None,
        batch_size: int = 1,
        gradient_accumulation_steps: int = 1,
        warmup_ratio: float = 0.0,
        max_grad_norm: Optional[float] = None,
        checkpoint_interval_epochs: Optional[float] = None,
        initialize_from: Optional[str] = None,
        resume_from: Optional[str] = None,
        assistant_only_logits: bool = False,
        localization_iou_thresholds: Sequence[float] = (0.25, 0.5, 0.75),
        optimizer: Optional[Mapping[str, float]] = None,
        hooks: Optional[Sequence[Mapping[str, Any]]] = None,
        auxiliary_loss: Optional[Mapping[str, Any]] = None,
        pipeline: Optional[Mapping[str, Any]] = None,
        seed: int = 20260825,
    ) -> None:
        if batch_size < 1 or gradient_accumulation_steps < 1:
            raise ValueError("batch_size and gradient_accumulation_steps must be positive")
        if max_steps is None and max_epochs is None:
            raise ValueError("one of max_steps or max_epochs must be specified")
        if max_steps is not None and max_steps < 1:
            raise ValueError("max_steps must be positive when specified")
        if max_epochs is not None and max_epochs <= 0.0:
            raise ValueError("max_epochs must be positive when specified")
        if not 0.0 <= warmup_ratio < 1.0:
            raise ValueError("warmup_ratio must be in [0, 1)")
        if max_grad_norm is not None and max_grad_norm <= 0.0:
            raise ValueError("max_grad_norm must be positive when specified")
        if checkpoint_interval_epochs is not None and checkpoint_interval_epochs <= 0.0:
            raise ValueError("checkpoint_interval_epochs must be positive when specified")
        thresholds = tuple(float(value) for value in localization_iou_thresholds)
        if not thresholds or any(not 0.0 < value <= 1.0 for value in thresholds):
            raise ValueError("localization_iou_thresholds must contain values in (0, 1]")
        if len(set(thresholds)) != len(thresholds):
            raise ValueError("localization_iou_thresholds must not contain duplicates")
        self.wrapper = model
        self.model = model.model
        self.context = getattr(model, "context", None)
        self.rank = self.context.rank if self.context else 0
        self.world_size = self.context.world_size if self.context else 1
        self.is_main_process = self.rank == 0
        self.dataset = dataset
        self.collator = collator
        self.work_dir = Path(work_dir)
        if self.is_main_process:
            self.work_dir.mkdir(parents=True, exist_ok=True)
        if self.context:
            barrier(self.context)

        self.batch_size = batch_size
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.samples_per_update = (
            self.batch_size * self.world_size * self.gradient_accumulation_steps
        )
        self.updates_per_epoch = math.ceil(len(self.dataset) / self.samples_per_update)
        self.max_epochs = max_epochs
        self.max_steps = (
            math.ceil(max_epochs * self.updates_per_epoch)
            if max_epochs is not None
            else int(max_steps)
        )
        self.warmup_ratio = warmup_ratio
        self.warmup_steps = math.ceil(self.max_steps * warmup_ratio)
        self.max_grad_norm = max_grad_norm
        self.checkpoint_interval_epochs = checkpoint_interval_epochs
        self.checkpoint_interval_samples = (
            checkpoint_interval_epochs * len(self.dataset)
            if checkpoint_interval_epochs is not None
            else None
        )
        self.next_checkpoint_samples = self.checkpoint_interval_samples
        if initialize_from and resume_from:
            raise ValueError("initialize_from and resume_from are mutually exclusive")
        self.initialize_from = Path(initialize_from) if initialize_from else None
        self.resume_from = Path(resume_from) if resume_from else None
        self.initialized_from = ""
        self.resumed_from = ""
        self.assistant_only_logits = assistant_only_logits
        self.localization_iou_thresholds = thresholds
        self.seed = seed
        self.step = 0
        self.samples_seen = 0
        # Set again after a possible checkpoint restore at run start. Hooks use
        # these values to keep resumed progress/throughput records coherent.
        self.run_start_step = 0
        self.run_start_samples_seen = 0
        self.history: List[float] = []
        self.localization_history: List[Dict[str, float]] = []
        self.latest_localization_metrics = self._empty_localization_metrics()
        self.auxiliary_history: List[Dict[str, float]] = []
        self.latest_auxiliary_metrics: Dict[str, float] = {}
        if pipeline is not None and auxiliary_loss is not None:
            raise ValueError("use pipeline stages or a static auxiliary_loss, not both")
        self.pipeline = TrainingPipeline(**dict(pipeline)) if pipeline is not None else None
        self.pipeline_metrics = {}
        self.auxiliary_loss = AUXILIARY_LOSSES.build(
            dict(auxiliary_loss) if auxiliary_loss is not None else None,
            wrapper=model,
            dataset=dataset,
            collator=collator,
        )
        self.metrics: Dict[str, Any] = {}
        self.finite_grad_fraction = 0.0
        self.training_started_at: Optional[float] = None
        self.step_duration_seconds = 0.0
        self.current_learning_rate = 0.0
        optimizer_cfg = dict(optimizer or {})
        self.parameters = list(model.trainable_parameters())
        self.optimizer = torch.optim.AdamW(
            self.parameters,
            lr=optimizer_cfg.get("lr", 1e-3),
            weight_decay=optimizer_cfg.get("weight_decay", 0.0),
        )
        self.scheduler = torch.optim.lr_scheduler.LambdaLR(
            self.optimizer,
            lr_lambda=lambda step: (
                min((step + 1) / self.warmup_steps, 1.0)
                if self.warmup_steps
                else 1.0
            ),
        )
        self.hooks = sorted(
            [HOOKS.build(config) for config in (hooks or [])],
            key=lambda hook: hook.priority,
        )

    def call(self, method_name: str) -> None:
        """Call hooks; hooks decide whether only rank zero should act."""
        for hook in self.hooks:
            getattr(hook, method_name)(self)

    def batch(self, micro_step: int = 0) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Build a disjoint per-rank batch using deterministic strided indices."""
        global_start = micro_step * self.batch_size * self.world_size
        rank_start = global_start + self.rank * self.batch_size
        samples = [
            self.dataset[(rank_start + offset) % len(self.dataset)]
            for offset in range(self.batch_size)
        ]
        encoded = self.collator(samples)
        metadata = encoded.pop("metadata")
        batch = {
            key: value.to(self.wrapper.input_device)
            for key, value in encoded.items()
        }
        return batch, metadata

    def run(self) -> Dict[str, Any]:
        """Optimize LoRA parameters and aggregate bounded metrics over ranks."""
        self._set_seed()
        self._initialize_or_restore_checkpoint()
        self.run_start_step = self.step
        self.run_start_samples_seen = self.samples_seen
        self.call("before_run")
        if self.pipeline is not None:
            self.pipeline.prepare(self, self.step)
        evaluation_batch, evaluation_metadata = self.batch(0)
        initial_parameters = [
            parameter.detach().float().cpu().clone() for parameter in self.parameters
        ]
        local_loss_before = self._evaluate_loss(
            evaluation_batch, None if self.pipeline else evaluation_metadata
        )
        loss_before = self._mean(local_loss_before)

        started = time.time()
        samples_seen_at_start = self.samples_seen
        learning_rates: List[float] = []
        self.model.train()
        self.training_started_at = time.perf_counter()
        for self.step in range(self.step + 1, self.max_steps + 1):
            step_started_at = time.perf_counter()
            self.optimizer.zero_grad(set_to_none=True)
            if self.pipeline is not None:
                self.pipeline.prepare(self, self.step - 1)
            local_micro_losses = []
            localization_counts = []
            local_auxiliary_metrics: List[Dict[str, float]] = []
            for accumulation in range(self.gradient_accumulation_steps):
                micro_step = (
                    (self.step - 1) * self.gradient_accumulation_steps + accumulation
                )
                batch, metadata = self.batch(micro_step)
                synchronization = self._gradient_sync_context(accumulation)
                with synchronization:
                    output, forward_batch, loss, auxiliary_metrics = (
                        self._loss_forward(batch, metadata)
                    )
                    (loss / self.gradient_accumulation_steps).backward()
                local_micro_losses.append(float(loss.detach().float().item()))
                local_auxiliary_metrics.append(auxiliary_metrics)
                localization_counts.append(
                    self._localization_metric_counts(output.logits, forward_batch["labels"])
                )
            self.finite_grad_fraction = self._finite_gradient_fraction()
            if self.max_grad_norm is not None:
                torch.nn.utils.clip_grad_norm_(self.parameters, self.max_grad_norm)
            self.current_learning_rate = float(self.optimizer.param_groups[0]["lr"])
            learning_rates.append(self.current_learning_rate)
            self.optimizer.step()
            self.scheduler.step()
            local_step_loss = sum(local_micro_losses) / len(local_micro_losses)
            self.history.append(self._mean(local_step_loss))
            self.latest_localization_metrics = self._aggregate_localization_counts(
                localization_counts
            )
            self.localization_history.append(
                {"step": float(self.step), **self.latest_localization_metrics}
            )
            self.latest_auxiliary_metrics = self._aggregate_auxiliary_metrics(
                local_auxiliary_metrics
            )
            self.auxiliary_history.append(
                {"step": float(self.step), **self.latest_auxiliary_metrics}
            )
            self.samples_seen += self.samples_per_update
            self.step_duration_seconds = time.perf_counter() - step_started_at
            self.call("after_train_step")
            self._save_due_checkpoints()

        elapsed = time.time() - started
        # Compare the same CE objective across stages with different auxiliary weights.
        local_loss_after = self._evaluate_loss(
            evaluation_batch, None if self.pipeline else evaluation_metadata
        )
        loss_after = self._mean(local_loss_after)
        adapter_delta_norm = self._parameter_delta_norm(initial_parameters)
        self.wrapper.save_adapter(self.work_dir / "adapter")
        if self.context:
            barrier(self.context)

        session_examples_seen = self.samples_seen - samples_seen_at_start
        evaluation_rows = self._gather(evaluation_metadata)
        passed = (
            loss_after < loss_before
            and adapter_delta_norm > 0
            and self.finite_grad_fraction == 1.0
        )
        self.metrics = {
            "status": "passed" if passed else "gate_failed",
            "distributed": self.world_size > 1,
            "world_size": self.world_size,
            "per_device_batch_size": self.batch_size,
            "global_physical_batch_size": self.batch_size * self.world_size,
            "gradient_accumulation_steps": self.gradient_accumulation_steps,
            "updates_per_epoch": self.updates_per_epoch,
            "configured_max_epochs": self.max_epochs,
            "checkpoint_interval_epochs": self.checkpoint_interval_epochs,
            "checkpoint_interval_samples": self.checkpoint_interval_samples,
            "initialized_from": self.initialized_from,
            "resumed_from": self.resumed_from,
            "warmup_ratio": self.warmup_ratio,
            "warmup_steps": self.warmup_steps,
            "max_grad_norm": self.max_grad_norm,
            "learning_rates": learning_rates,
            "assistant_only_logits": self.assistant_only_logits,
            "logits_to_keep": self._logits_to_keep(evaluation_batch),
            "effective_global_batch_size": (
                self.batch_size
                * self.world_size
                * self.gradient_accumulation_steps
            ),
            "steps": self.step,
            "examples_seen": self.samples_seen,
            "session_examples_seen": session_examples_seen,
            "train_seconds": elapsed,
            "examples_per_second": session_examples_seen / elapsed if elapsed else 0.0,
            "loss_before": loss_before,
            "step_losses": self.history,
            "loss_after": loss_after,
            "teacher_forced_localization": {
                "iou_thresholds": list(self.localization_iou_thresholds),
                "step_metrics": self.localization_history,
            },
            "auxiliary_loss": {
                "enabled": self.auxiliary_loss is not None,
                "step_metrics": self.auxiliary_history,
            },
            "training_pipeline": self.pipeline.state_dict() if self.pipeline else None,
            "loss_comparison_objective": "sft_ce" if self.pipeline else "configured_loss",
            "adapter_delta_norm": adapter_delta_norm,
            "finite_grad_fraction": self.finite_grad_fraction,
            "trainable_parameter_count": sum(p.numel() for p in self.parameters),
            "dataset_size": len(self.dataset),
            "seed": self.seed,
            "eval_sample_ids_by_rank": [
                [row["id"] for row in rank_rows] for rank_rows in evaluation_rows
            ],
        }
        self.call("after_run")
        return self.metrics

    def _save_due_checkpoints(self) -> None:
        """Persist adapter plus optimizer/scheduler state at epoch-based boundaries."""
        if self.next_checkpoint_samples is None:
            return
        while self.samples_seen >= self.next_checkpoint_samples:
            target_samples = self.next_checkpoint_samples
            self.next_checkpoint_samples += self.checkpoint_interval_samples
            self._save_checkpoint(target_samples)

    def _save_checkpoint(self, target_samples: float) -> None:
        """Save a resumable checkpoint once, with rank zero owning shared files."""
        checkpoint_dir = self.work_dir / "checkpoints" / (
            f"samples_{int(target_samples):08d}_step_{self.step:06d}"
        )
        if checkpoint_dir.exists():
            raise FileExistsError(
                "refusing to overwrite an existing checkpoint directory: "
                f"{checkpoint_dir}"
            )
        if self.is_main_process:
            checkpoint_dir.mkdir(parents=True, exist_ok=False)
            self.wrapper.save_adapter(checkpoint_dir / "adapter")
            torch.save(
                {
                    "format_version": 1,
                    "step": self.step,
                    "samples_seen": self.samples_seen,
                    "next_checkpoint_samples": self.next_checkpoint_samples,
                    "history": self.history,
                    "localization_history": self.localization_history,
                    "auxiliary_history": self.auxiliary_history,
                    "pipeline_state": self.pipeline.state_dict() if self.pipeline else None,
                    "optimizer": self.optimizer.state_dict(),
                    "scheduler": self.scheduler.state_dict(),
                    "max_steps": self.max_steps,
                    "seed": self.seed,
                },
                checkpoint_dir / "trainer_state.pt",
            )
        if self.context:
            barrier(self.context)

    def _initialize_or_restore_checkpoint(self) -> None:
        """Initialize a new branch or restore an interrupted run, never both."""
        if self.initialize_from is not None:
            checkpoint_dir = validate_checkpoint(self.initialize_from)
            load_adapter_checkpoint(self.wrapper, checkpoint_dir)
            self.initialized_from = str(checkpoint_dir)
            if self.context:
                barrier(self.context)
            return
        self._restore_checkpoint_if_requested()

    def _restore_checkpoint_if_requested(self) -> None:
        """Restore the adapter and complete optimizer state before the next update."""
        if self.resume_from is None:
            return
        checkpoint_dir = validate_checkpoint(self.resume_from)
        load_adapter_checkpoint(self.wrapper, checkpoint_dir)
        state = torch.load(checkpoint_dir / "trainer_state.pt", map_location="cpu")
        if state.get("format_version") != 1:
            raise ValueError(f"unsupported trainer checkpoint format: {state.get('format_version')}")
        self.optimizer.load_state_dict(state["optimizer"])
        self._move_optimizer_state_to_parameter_devices()
        self.scheduler.load_state_dict(state["scheduler"])
        self.step = int(state["step"])
        self.samples_seen = int(state["samples_seen"])
        self.next_checkpoint_samples = state.get(
            "next_checkpoint_samples", self.checkpoint_interval_samples
        )
        self.history = list(state.get("history", []))
        self.localization_history = list(state.get("localization_history", []))
        self.auxiliary_history = list(state.get("auxiliary_history", []))
        pipeline_state = state.get("pipeline_state")
        if self.pipeline is not None:
            if pipeline_state is None:
                raise ValueError("resume checkpoint has no pipeline state; use initialize_from for a new branch")
            self.pipeline.load_state_dict(pipeline_state)
        elif pipeline_state is not None:
            raise ValueError("resume checkpoint requires its configured training pipeline")
        if self.auxiliary_history:
            self.latest_auxiliary_metrics = {
                key: value
                for key, value in self.auxiliary_history[-1].items()
                if key != "step"
            }
        if self.localization_history:
            self.latest_localization_metrics = {
                key: value
                for key, value in self.localization_history[-1].items()
                if key != "step"
            }
        if self.step > self.max_steps:
            raise ValueError(
                f"checkpoint step {self.step} exceeds configured max_steps {self.max_steps}"
            )
        self.resumed_from = str(checkpoint_dir)
        if self.context:
            barrier(self.context)

    def _move_optimizer_state_to_parameter_devices(self) -> None:
        """Match restored Adam moments to each LoRA parameter's actual device."""
        for parameter, state in self.optimizer.state.items():
            for key, value in state.items():
                if torch.is_tensor(value):
                    state[key] = value.to(parameter.device)

    def _gradient_sync_context(self, accumulation: int):
        """Avoid redundant DDP all-reduce before the final accumulation microstep."""
        is_final = accumulation == self.gradient_accumulation_steps - 1
        if self.world_size > 1 and not is_final:
            return self.model.no_sync()
        return nullcontext()

    def _logits_to_keep(self, batch: Dict[str, Any]) -> int:
        """Return the minimal common suffix covering every supervised target.

        Causal LM position ``t - 1`` predicts label ``t``, so the suffix starts
        one position before the earliest non-ignored label in the batch.
        """
        if not self.assistant_only_logits:
            return 0
        labels = batch["labels"]
        supervised = labels.ne(-100)
        if not bool(supervised.any()):
            raise ValueError("assistant-only logits require at least one supervised label")
        first_target = int(supervised.nonzero(as_tuple=False)[:, 1].min().item())
        if first_target == 0:
            raise ValueError("cannot preserve causal shift for a target at position zero")
        return labels.shape[1] - (first_target - 1)

    def _forward_batch(self, batch: Dict[str, Any]) -> Dict[str, Any]:
        """Slice only lm-head logits/labels while retaining the full model input."""
        keep = self._logits_to_keep(batch)
        if keep == 0:
            return batch
        forwarded = dict(batch)
        forwarded["labels"] = batch["labels"][:, -keep:]
        forwarded["logits_to_keep"] = keep
        return forwarded

    def _loss_forward(
        self,
        batch: Dict[str, Any],
        metadata: Sequence[Mapping[str, Any]],
    ):
        """Run SFT plus one optional generic auxiliary loss in the same graph."""
        forward_batch = self._forward_batch(batch)
        if self.auxiliary_loss is not None:
            self.auxiliary_loss.begin_batch(batch, metadata)
        output = self.model(**forward_batch)
        loss = output.loss
        values: Dict[str, float] = {
            "sft_loss": float(output.loss.detach().float().item())
        }
        values.update(getattr(self, "pipeline_metrics", {}))
        if self.auxiliary_loss is not None:
            auxiliary = self.auxiliary_loss.compute(output, batch, metadata)
            loss = loss + auxiliary.loss
            values.update(
                {
                    key: float(value.detach().float().item())
                    for key, value in auxiliary.metrics.items()
                }
            )
        values["total_loss"] = float(loss.detach().float().item())
        return output, forward_batch, loss, values

    def _aggregate_auxiliary_metrics(
        self, rows: Sequence[Mapping[str, float]]
    ) -> Dict[str, float]:
        if not rows:
            return {}
        keys = sorted({key for row in rows for key in row})
        return {
            key: self._mean(sum(float(row[key]) for row in rows) / len(rows))
            for key in keys
        }

    def _evaluate_loss(
        self,
        batch: Dict[str, Any],
        metadata: Optional[Sequence[Mapping[str, Any]]] = None,
    ) -> float:
        self.model.eval()
        with torch.no_grad():
            if metadata is None:
                value = float(
                    self.model(**self._forward_batch(batch)).loss.float().item()
                )
            else:
                _, _, loss, _ = self._loss_forward(batch, metadata)
                value = float(loss.float().item())
        self.model.train()
        return value

    def _empty_localization_metrics(self) -> Dict[str, float]:
        """Return an explicit empty metric row for a supervised update."""
        values = {
            "teacher_forced_bbox_parse_rate": 0.0,
            "teacher_forced_mean_iou": 0.0,
        }
        values.update(
            {
                f"teacher_forced_iou_at_{threshold:g}": 0.0
                for threshold in self.localization_iou_thresholds
            }
        )
        return values

    def _localization_metric_counts(
        self, logits: torch.Tensor, labels: torch.Tensor
    ) -> Dict[str, float]:
        """Measure boxes from greedy teacher-forced answer tokens.

        This is deliberately *not* a free-generation evaluation: each answer
        token is predicted while preceding gold answer tokens remain in the
        context.  It is cheap enough to log every optimizer step, and is kept
        separately named so it cannot be confused with an autoregressive
        validation IoU.
        """
        if logits is None:
            raise RuntimeError("model did not return logits for localization metrics")
        if logits.shape[:2] != labels.shape:
            raise ValueError(
                "logits and labels must share batch/sequence dimensions for IoU metrics"
            )
        if labels.shape[1] < 2:
            raise ValueError("need at least two positions for causal localization metrics")

        predicted_ids = logits[:, :-1].detach().argmax(dim=-1).cpu()
        target_ids = labels[:, 1:].detach().cpu()
        counts: Dict[str, float] = {
            "samples": 0.0,
            "parsed": 0.0,
            "iou_sum": 0.0,
        }
        counts.update(
            {f"iou_at_{threshold:g}": 0.0 for threshold in self.localization_iou_thresholds}
        )
        for predicted_row, target_row in zip(predicted_ids, target_ids):
            mask = target_row.ne(-100)
            if not bool(mask.any()):
                continue
            prediction = self._decode_answer_tokens(predicted_row[mask].tolist())
            target = self._decode_answer_tokens(target_row[mask].tolist())
            target_box = parse_box(target)
            if target_box is None:
                raise RuntimeError("supervised localization answer does not contain a box")
            prediction_box = parse_box(prediction)
            iou = box_iou(prediction_box, target_box)
            counts["samples"] += 1.0
            counts["parsed"] += float(prediction_box is not None)
            counts["iou_sum"] += iou
            for threshold in self.localization_iou_thresholds:
                counts[f"iou_at_{threshold:g}"] += float(iou >= threshold)
        return counts

    def _decode_answer_tokens(self, token_ids: List[int]) -> str:
        processor = self.collator.processor
        tokenizer = getattr(processor, "tokenizer", processor)
        return tokenizer.decode(token_ids, skip_special_tokens=True)

    def _aggregate_localization_counts(
        self, local_counts: Sequence[Mapping[str, float]]
    ) -> Dict[str, float]:
        """Globally reduce microbatch box statistics without averaging rates."""
        local_total: Dict[str, float] = {
            "samples": 0.0,
            "parsed": 0.0,
            "iou_sum": 0.0,
        }
        local_total.update(
            {f"iou_at_{threshold:g}": 0.0 for threshold in self.localization_iou_thresholds}
        )
        for row in local_counts:
            for key in local_total:
                local_total[key] += float(row.get(key, 0.0))
        totals = {key: 0.0 for key in local_total}
        for rank_totals in self._gather(local_total):
            for key in totals:
                totals[key] += float(rank_totals.get(key, 0.0))

        sample_count = totals["samples"]
        if sample_count == 0.0:
            return self._empty_localization_metrics()
        metrics = {
            "teacher_forced_bbox_parse_rate": totals["parsed"] / sample_count,
            "teacher_forced_mean_iou": totals["iou_sum"] / sample_count,
        }
        metrics.update(
            {
                f"teacher_forced_iou_at_{threshold:g}": (
                    totals[f"iou_at_{threshold:g}"] / sample_count
                )
                for threshold in self.localization_iou_thresholds
            }
        )
        return metrics

    def _finite_gradient_fraction(self) -> float:
        gradients = [p.grad for p in self.parameters if p.grad is not None]
        local_fraction = (
            sum(bool(torch.isfinite(gradient).all()) for gradient in gradients)
            / len(gradients)
            if gradients
            else 0.0
        )
        return self._mean(local_fraction)

    def _parameter_delta_norm(self, initial: Sequence[torch.Tensor]) -> float:
        local_squared_norm = sum(
            float(
                (parameter.detach().float().cpu() - initial_value)
                .square()
                .sum()
                .item()
            )
            for parameter, initial_value in zip(self.parameters, initial)
        )
        # DDP replicas should be identical. Average squared norms instead of
        # summing them so this remains the norm of one adapter, not all replicas.
        return math.sqrt(self._mean(local_squared_norm))

    def _mean(self, value: float) -> float:
        return mean_scalar(value, self.context) if self.context else value

    def _gather(self, value: Any) -> List[Any]:
        return gather_objects(value, self.context) if self.context else [value]

    def _set_seed(self) -> None:
        # Shared seeds keep dropout and initialization reproducible; disjoint
        # dataset indices, rather than different RNG seeds, separate rank data.
        random.seed(self.seed)
        torch.manual_seed(self.seed)
        torch.cuda.manual_seed_all(self.seed)
