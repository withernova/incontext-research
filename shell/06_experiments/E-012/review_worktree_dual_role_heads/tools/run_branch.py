#!/usr/bin/env python3
"""Prepare and launch one isolated train/evaluate/head-screen branch."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence

from iploc_szy.branching import branch_summary, load_experiment_config
from iploc_szy.run_management import prepare_named_run

PROJECT = Path("/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy")
TORCHRUN = Path("/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/torchrun")
WORKERS = {
    "train": "tools/train.py",
    "evaluate": "tools/evaluate.py",
    "head_screen": "tools/screen_heads.py",
    "attention_intervene": "tools/evaluate.py",
}


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    parser.add_argument("overrides", nargs="*", help="branch/runtime key=value")
    parser.add_argument(
        "--inspect",
        action="store_true",
        help="resolve and print the action without allocating a run",
    )
    return parser.parse_intermixed_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = PROJECT / config_path
    config_path = config_path.resolve()
    config = load_experiment_config(config_path, args.overrides)
    summary = dict(branch_summary(config))
    if args.inspect:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    if summary["action"] == "attention_intervene":
        from iploc_szy.evaluation.query_attention import validate_run_config
        validate_run_config(config)
    prepared = prepare_named_run(config, config_path, args.overrides)
    action = str(summary["action"])
    nproc = int(summary["nproc_per_node"])
    checkpoint = prepared["resume_checkpoint"] or "-"
    is_branch = "branch" in config
    work_dir_key = "runtime.work_dir" if is_branch else "work_dir"
    internal_options = [
        *args.overrides,
        f"{work_dir_key}={prepared['work_dir']}",
        f"named_run.resolved_run_id={prepared['run_id']}",
        f"named_run.resolved_resume_checkpoint={checkpoint}",
    ]
    command = [
        str(TORCHRUN),
        "--standalone",
        f"--nproc_per_node={nproc}",
        str(PROJECT / WORKERS[action]),
        str(config_path),
        "--cfg-options",
        *internal_options,
    ]
    environment = dict(os.environ)
    environment.setdefault("CUDA_VISIBLE_DEVICES", ",".join(map(str, range(nproc))))
    environment["PYTHONPATH"] = str(PROJECT) + (
        os.pathsep + environment["PYTHONPATH"]
        if environment.get("PYTHONPATH")
        else ""
    )
    environment.setdefault("TOKENIZERS_PARALLELISM", "false")
    environment.setdefault("PYTHONUNBUFFERED", "1")
    environment.setdefault("OMP_NUM_THREADS", "4")

    log_path = Path(prepared["manifest"]["artifacts"]["log"])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[NAMED_RUN] action={action}", flush=True)
    print(f"[NAMED_RUN] run_id={prepared['run_id']}", flush=True)
    print(f"[NAMED_RUN] work_dir={prepared['work_dir']}", flush=True)
    print(f"[NAMED_RUN] parent_checkpoint={checkpoint}", flush=True)
    try:
        with log_path.open("a", encoding="utf-8") as log:
            process = subprocess.Popen(
                command,
                cwd=PROJECT,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            assert process.stdout is not None
            for line in process.stdout:
                sys.stdout.write(line)
                sys.stdout.flush()
                log.write(line)
                log.flush()
            return process.wait()
    except BaseException as error:
        print(f"[LAUNCH_FAILED] {type(error).__name__}", flush=True)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
