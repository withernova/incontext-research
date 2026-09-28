#!/usr/bin/env python3
"""Train a configured iploc-szy model."""

import argparse
import json
import os
from typing import Optional, Sequence

from iploc_szy.run_snapshot import save_snapshot, save_prompt_example
from iploc_szy.branching import load_experiment_config
from iploc_szy.builder import build_training
from iploc_szy.run_management import mark_run_event, validate_prepared_run
from iploc_szy.utils.distributed import shutdown_distributed


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse the config path and optional dotted overrides."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", help="Path to a Python experiment config")
    parser.add_argument(
        "--cfg-options",
        nargs="*",
        default=[],
        help="Dotted key=value overrides, for example runner.max_steps=10",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Build and run training, returning a process-compatible status code."""
    args = parse_args(argv)
    config = load_experiment_config(args.config, args.cfg_options)
    validate_prepared_run(config)
    launcher_rank_zero = int(os.environ.get("RANK", "0")) == 0
    snapshot = save_snapshot(config, args.config, "train") if launcher_rank_zero else None
    runner = None
    try:
        if launcher_rank_zero:
            mark_run_event(config, "training_started", "running")
        runner = build_training(config)
        if snapshot is not None:
            save_prompt_example(snapshot, runner.dataset[0])
        metrics = runner.run()
        if runner.is_main_process:
            mark_run_event(
                config,
                "training_finished",
                str(metrics["status"]),
                {"step": metrics.get("steps")},
            )
            print("[DONE]", json.dumps(metrics, ensure_ascii=False), flush=True)
        return 0 if metrics["status"] == "passed" else 2
    except BaseException as error:
        if launcher_rank_zero:
            try:
                mark_run_event(
                    config,
                    "training_failed",
                    "failed",
                    {"exception_type": type(error).__name__},
                )
            except Exception as marker_error:
                print(
                    f"[NAMED_RUN_WARNING] failed to record failure event: "
                    f"{type(marker_error).__name__}",
                    flush=True,
                )
        raise
    finally:
        if runner is not None and runner.context:
            shutdown_distributed(runner.context)


if __name__ == "__main__":
    raise SystemExit(main())
