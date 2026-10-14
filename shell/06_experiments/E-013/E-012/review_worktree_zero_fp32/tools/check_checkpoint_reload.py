#!/usr/bin/env python3
"""Verify that an E-009 LoRA checkpoint can be restored without SFT data work."""

from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

import torch

from iploc_szy import Config
from iploc_szy.builder import build_training


def _adapter_state(runner: Any) -> Dict[str, torch.Tensor]:
    model = runner.model.module if hasattr(runner.model, "module") else runner.model
    return {
        name: parameter.detach().float().cpu().clone()
        for name, parameter in model.named_parameters()
        if "lora_" in name
    }


def _optimizer_state_size(runner: Any) -> int:
    return sum(len(state) for state in runner.optimizer.state.values())


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--cfg-options", nargs="*", default=[])
    return parser.parse_args(argv)


def _config(args: argparse.Namespace, resume_from: Optional[Path] = None) -> Config:
    options = list(args.cfg_options) + [
        "model.attn_implementation=sdpa",
        f"work_dir={args.work_dir}",
        "runner.max_steps=1",
    ]
    if resume_from is not None:
        options.append(f"runner.resume_from={resume_from}")
    return Config.fromfile(args.config).merge_options(options)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    work_dir = Path(args.work_dir)
    first = build_training(_config(args))
    try:
        # This is intentionally not an SFT forward/backward pass. It creates a
        # non-empty Adam state so resume verifies more than adapter weights.
        first.optimizer.zero_grad(set_to_none=True)
        for parameter in first.parameters:
            parameter.grad = torch.full_like(parameter, 1e-5)
        first.optimizer.step()
        first.scheduler.step()
        first.step = 1
        first.samples_seen = first.samples_per_update
        expected_adapter = _adapter_state(first)
        expected_scheduler = first.scheduler.state_dict()
        expected_optimizer_entries = _optimizer_state_size(first)
        first._save_checkpoint(0.0)
        checkpoint = work_dir / "checkpoints" / "samples_00000000_step_000001"
    finally:
        del first
        gc.collect()
        torch.cuda.empty_cache()

    restored = build_training(_config(args, checkpoint))
    try:
        restored._restore_checkpoint_if_requested()
        actual_adapter = _adapter_state(restored)
        exact_adapter = (
            actual_adapter.keys() == expected_adapter.keys()
            and all(torch.equal(actual_adapter[name], expected_adapter[name]) for name in expected_adapter)
        )
        scheduler_match = restored.scheduler.state_dict() == expected_scheduler
        passed = (
            exact_adapter
            and _optimizer_state_size(restored) == expected_optimizer_entries
            and scheduler_match
            and restored.step == 1
            and restored.samples_seen == restored.samples_per_update
        )
        print(json.dumps({
            "status": "passed" if passed else "gate_failed",
            "adapter_exact_match": exact_adapter,
            "optimizer_entries": _optimizer_state_size(restored),
            "scheduler_exact_match": scheduler_match,
            "restored_step": restored.step,
            "restored_samples_seen": restored.samples_seen,
        }, ensure_ascii=False), flush=True)
        return 0 if passed else 2
    finally:
        del restored
        gc.collect()
        torch.cuda.empty_cache()


if __name__ == "__main__":
    raise SystemExit(main())
