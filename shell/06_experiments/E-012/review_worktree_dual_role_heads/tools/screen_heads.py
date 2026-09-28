#!/usr/bin/env python3
"""Run one standalone teacher-forced head screen on a named checkpoint."""

from __future__ import annotations

import argparse
import json
import os
from typing import Optional, Sequence

from iploc_szy.branching import load_experiment_config
from iploc_szy.builder import build_training
from iploc_szy.checkpointing import (
    load_adapter_checkpoint,
    load_trainer_progress,
)
from iploc_szy.head_screening.hooks import HeadScreeningHook
from iploc_szy.run_management import mark_run_event, validate_prepared_run
from iploc_szy.utils.distributed import shutdown_distributed


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    parser.add_argument("--cfg-options", nargs="*", default=[])
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    config = load_experiment_config(args.config, args.cfg_options)
    validate_prepared_run(config)
    launcher_rank_zero = int(os.environ.get("RANK", "0")) == 0
    runner = None
    try:
        if launcher_rank_zero:
            mark_run_event(config, "head_screen_started", "running")
        runner = build_training(config)
        checkpoint = config["named_run"]["resolved_resume_checkpoint"]
        load_adapter_checkpoint(runner.wrapper, checkpoint)
        progress = load_trainer_progress(checkpoint)
        runner.step = progress["step"]
        runner.samples_seen = progress["samples_seen"]
        hook = HeadScreeningHook(**dict(config["head_screening"]))
        result = hook.run_once(runner)
        if runner.is_main_process:
            mark_run_event(
                config,
                "head_screen_finished",
                "completed",
                {
                    "records": result.get("records"),
                    "summary": str(hook.root / "latest.json"),
                    "stable_candidate": result.get("stability", {}).get(
                        "stable_candidate"
                    ),
                },
            )
            print("[HEAD_SCREEN_DONE]", json.dumps(result, ensure_ascii=False), flush=True)
        return 0
    except BaseException as error:
        if launcher_rank_zero:
            try:
                mark_run_event(
                    config,
                    "head_screen_failed",
                    "failed",
                    {"exception_type": type(error).__name__},
                )
            except Exception:
                pass
        raise
    finally:
        if runner is not None and runner.context:
            shutdown_distributed(runner.context)


if __name__ == "__main__":
    raise SystemExit(main())
