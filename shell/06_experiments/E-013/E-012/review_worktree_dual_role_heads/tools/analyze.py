#!/usr/bin/env python3
"""Run one config-driven analysis with shared snapshots and status records."""

from __future__ import annotations

import argparse
import importlib
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from iploc_szy.branching import load_experiment_config
from iploc_szy.run_snapshot import save_snapshot


STATUS_SCHEMA = "iploc-szy.analysis-status/v1"


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    parser.add_argument("--cfg-options", nargs="*", default=[])
    return parser.parse_args(argv)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(dict(payload), ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def resolve_entrypoint(value: Any):
    text = str(value or "")
    if text.count(":") != 1:
        raise ValueError("analysis.entrypoint must be 'python.module:function'")
    module_name, function_name = text.split(":", 1)
    if not module_name or not function_name:
        raise ValueError("analysis.entrypoint must name a module and function")
    function = getattr(importlib.import_module(module_name), function_name, None)
    if not callable(function):
        raise ValueError(f"analysis entrypoint is not callable: {text}")
    return function


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    config = load_experiment_config(args.config, args.cfg_options)
    settings = dict(config.get("analysis") or {})
    run_id = str(settings.get("run_id") or "")
    if not run_id:
        raise ValueError("analysis.run_id is required")
    work_dir = Path(config["work_dir"]).resolve()
    snapshot = save_snapshot(config, args.config, "analyze")
    status_path = work_dir / "status.json"
    base = {
        "schema": STATUS_SCHEMA,
        "run_id": run_id,
        "work_dir": str(work_dir),
        "config_snapshot": str(snapshot),
    }
    _write_json(status_path, {**base, "status": "running", "started_at_utc": datetime.now(timezone.utc).isoformat()})
    try:
        entrypoint = resolve_entrypoint(settings.get("entrypoint"))
        result = entrypoint(config=config, snapshot_dir=snapshot)
        if result is None:
            result = {}
        if not isinstance(result, Mapping):
            raise TypeError("analysis entrypoint must return a mapping or None")
        finished = {**base, "status": "completed", "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                    "result": dict(result)}
        _write_json(status_path, finished)
        print(f"[ANALYSIS_DONE] run_id={run_id} status={status_path}", flush=True)
        return 0
    except BaseException as error:
        failure = {**base, "status": "failed", "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                   "exception": type(error).__name__, "reason": str(error),
                   "traceback": traceback.format_exc()}
        _write_json(status_path, failure)
        print(f"[ANALYSIS_FAILED] run_id={run_id} status={status_path}", flush=True)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
