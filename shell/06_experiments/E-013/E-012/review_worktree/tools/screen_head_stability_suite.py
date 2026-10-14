#!/usr/bin/env python3
"""Screen an ordered checkpoint suite and summarize head-set stability."""

from __future__ import annotations

import argparse
import json
import torch
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

from analyze_head_stability import analyze, load_screens, write_json
from iploc_szy.branching import load_experiment_config
from iploc_szy.builder import build_training
from iploc_szy.checkpointing import (
    load_adapter_checkpoint,
    load_trainer_progress,
    validate_checkpoint,
)
from iploc_szy.head_screening.hooks import HeadScreeningHook
from iploc_szy.utils.distributed import barrier, shutdown_distributed


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    parser.add_argument("--cfg-options", nargs="*", default=[])
    parser.add_argument(
        "--checkpoints",
        nargs="+",
        metavar="LABEL",
        help="optional checkpoint labels from checkpoint_suite.checkpoints",
    )
    return parser.parse_args(argv)


def suite_entries(config: Mapping[str, Any]) -> Tuple[Path, Sequence[Dict[str, Any]]]:
    raw = config.get("checkpoint_suite")
    if not isinstance(raw, Mapping):
        raise ValueError("checkpoint_suite config is required")
    work_dir = Path(str(raw.get("work_dir") or "")).resolve()
    if not str(raw.get("work_dir") or "").strip():
        raise ValueError("checkpoint_suite.work_dir is required")
    entries = []
    labels = set()
    paths = set()
    for index, item in enumerate(raw.get("checkpoints") or ()):
        if not isinstance(item, Mapping):
            raise ValueError(f"checkpoint_suite.checkpoints[{index}] must be a mapping")
        label = str(item.get("label") or "").strip()
        kind = str(item.get("kind", "adapter")).strip()
        path = str(item.get("path") or "").strip()
        if not label or kind not in {"adapter", "base_model"}:
            raise ValueError(
                f"checkpoint_suite.checkpoints[{index}] needs a label and kind adapter/base_model"
            )
        if kind == "adapter" and not path:
            raise ValueError(f"checkpoint_suite.checkpoints[{index}] adapter needs path")
        if kind == "base_model" and path:
            raise ValueError("base_model entries must omit path; model.model_path is used")
        if label in labels or (kind == "adapter" and path in paths):
            raise ValueError("checkpoint_suite labels and adapter paths must be unique")
        labels.add(label)
        if kind == "adapter":
            paths.add(path)
        entries.append(
            {
                "label": label,
                "kind": kind,
                "path": str(Path(path).resolve()) if path else None,
            }
        )
    if len(entries) < 2:
        raise ValueError("checkpoint_suite requires at least two checkpoints")
    return work_dir, entries


def select_checkpoints(
    entries: Sequence[Mapping[str, Any]], labels: Optional[Sequence[str]]
) -> Sequence[Mapping[str, Any]]:
    """Select configured entries in caller order without editing the config."""
    if labels is None:
        return entries
    available = {str(entry["label"]): entry for entry in entries}
    selected = []
    seen = set()
    for label in labels:
        if label in seen:
            raise ValueError(f"duplicate checkpoint selection: {label}")
        if label not in available:
            raise ValueError(
                f"unknown checkpoint selection: {label}; choices={sorted(available)}"
            )
        seen.add(label)
        selected.append(available[label])
    if len(selected) < 2:
        raise ValueError("head-stability suite requires at least two selected checkpoints")
    return selected


def _peft_target(wrapper: Any) -> Any:
    target = getattr(wrapper, "peft_model", None)
    return target or (wrapper.model.module if hasattr(wrapper.model, "module") else wrapper.model)


def capture_initial_adapter_state(wrapper: Any) -> Dict[str, Any]:
    """Capture the newly initialized (therefore untrained) adapter tensors."""
    state = {
        name: parameter.detach().cpu().clone()
        for name, parameter in _peft_target(wrapper).named_parameters()
        if "lora_" in name
    }
    if not state:
        raise RuntimeError("base-model screening requires initialized LoRA parameters")
    return state


def restore_initial_adapter_state(wrapper: Any, state: Mapping[str, Any]) -> None:
    """Restore untouched adapter tensors before a base-model screen."""
    parameters = {
        name: parameter
        for name, parameter in _peft_target(wrapper).named_parameters()
        if "lora_" in name
    }
    if set(parameters) != set(state):
        raise RuntimeError("could not restore the initial adapter state")
    with torch.no_grad():
        for name, parameter in parameters.items():
            parameter.copy_(state[name].to(device=parameter.device, dtype=parameter.dtype))


def checkpoint_log_payload(
    label: str,
    checkpoint: str,
    checkpoint_kind: str,
    latest_path: Path,
    result: Mapping[str, Any],
) -> Dict[str, Any]:
    sets = result["selected_sets"]
    return {
        "checkpoint": label,
        "checkpoint_kind": checkpoint_kind,
        "checkpoint_path": checkpoint,
        "records": int(result["records"]),
        "query_top3": list(sets["query"]["3"]),
        "query_top5": list(sets["query"]["5"]),
        "reference_top3": list(sets["reference"]["3"]),
        "reference_top5": list(sets["reference"]["5"]),
        "result_json": str(latest_path),
    }


def aggregate_log_payloads(summary: Mapping[str, Any]):
    for role, counts in summary["roles"].items():
        for count, values in counts.items():
            yield {
                "role": role,
                "top_k": int(count),
                "adjacent_jaccard_min": values["adjacent_jaccard_min"],
                "adjacent_jaccard_mean": values["adjacent_jaccard_mean"],
                "all_checkpoint_intersection": values[
                    "all_checkpoint_intersection"
                ],
                "all_checkpoint_union": values["all_checkpoint_union"],
            }


def publish_manifest(path: Path, payload: Mapping[str, Any]) -> None:
    write_json(
        path,
        {
            "schema": "iploc-szy.head-stability-suite/v1",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            **payload,
        },
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    config = load_experiment_config(args.config, args.cfg_options)
    suite_root, checkpoints = suite_entries(config)
    checkpoints = select_checkpoints(checkpoints, args.checkpoints)
    config["work_dir"] = str(suite_root)
    runner = None
    manifest_path = suite_root / "suite_manifest.json"
    screens = []
    try:
        runner = build_training(config)
        initial_adapter_state = capture_initial_adapter_state(runner.wrapper)
        if runner.is_main_process:
            suite_root.mkdir(parents=True, exist_ok=True)
            publish_manifest(
                manifest_path,
                {
                    "status": "running",
                    "checkpoints": checkpoints,
                    "completed": [],
                },
            )
        if runner.context:
            barrier(runner.context)

        completed = []
        for entry in checkpoints:
            label = entry["label"]
            checkpoint_kind = entry["kind"]
            if checkpoint_kind == "base_model":
                restore_initial_adapter_state(runner.wrapper, initial_adapter_state)
                checkpoint = str(config["model"]["model_path"])
                progress = {"step": 0, "samples_seen": 0}
            else:
                checkpoint = str(validate_checkpoint(entry["path"]))
                load_adapter_checkpoint(runner.wrapper, checkpoint)
                progress = load_trainer_progress(checkpoint)
            screen_work_dir = suite_root / "screens" / label
            latest_path = screen_work_dir / "head_screening" / "latest.json"
            if latest_path.exists():
                raise FileExistsError(
                    f"suite refuses to overwrite an existing screen: {latest_path}"
                )
            runner.work_dir = screen_work_dir
            runner.step = progress["step"]
            runner.samples_seen = progress["samples_seen"]
            hook = HeadScreeningHook(**dict(config["head_screening"]))
            result = hook.run_once(runner)
            screens.append(f"{label}={latest_path}")
            if runner.is_main_process:
                log_payload = checkpoint_log_payload(
                    label, checkpoint, checkpoint_kind, latest_path, result
                )
                completed.append(log_payload)
                print(
                    "[HEAD_STABILITY_CHECKPOINT] "
                    + json.dumps(log_payload, ensure_ascii=False, allow_nan=False),
                    flush=True,
                )
                publish_manifest(
                    manifest_path,
                    {
                        "status": "running",
                        "checkpoints": checkpoints,
                        "completed": completed,
                    },
                )

        if runner.is_main_process:
            summary = analyze(load_screens(screens))
            summary_path = suite_root / "head_stability_summary.json"
            write_json(summary_path, summary)
            for payload in aggregate_log_payloads(summary):
                print(
                    "[HEAD_STABILITY_AGGREGATE] "
                    + json.dumps(payload, ensure_ascii=False, allow_nan=False),
                    flush=True,
                )
            publish_manifest(
                manifest_path,
                {
                    "status": "completed",
                    "checkpoints": checkpoints,
                    "completed": completed,
                    "summary": str(summary_path),
                },
            )
            print(
                "[HEAD_STABILITY_DONE] "
                + json.dumps(
                    {
                        "checkpoints": len(checkpoints),
                        "summary": str(summary_path),
                        "manifest": str(manifest_path),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
        if runner.context:
            barrier(runner.context)
        return 0
    except BaseException as error:
        if runner is not None and runner.is_main_process:
            suite_root.mkdir(parents=True, exist_ok=True)
            publish_manifest(
                manifest_path,
                {
                    "status": "failed",
                    "checkpoints": checkpoints,
                    "completed": completed if "completed" in locals() else [],
                    "exception_type": type(error).__name__,
                },
            )
            print(
                "[HEAD_STABILITY_FAILED] "
                + json.dumps(
                    {
                        "exception_type": type(error).__name__,
                        "manifest": str(manifest_path),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
        raise
    finally:
        if runner is not None and runner.context:
            shutdown_distributed(runner.context)


if __name__ == "__main__":
    raise SystemExit(main())
