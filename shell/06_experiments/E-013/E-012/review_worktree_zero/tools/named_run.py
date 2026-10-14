#!/usr/bin/env python3
"""Prepare and inspect timestamped named runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from iploc_szy.branching import load_experiment_config
from iploc_szy.run_management import latest_index_rows, prepare_named_run


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="allocate one isolated run")
    prepare.add_argument("config")
    prepare.add_argument("--cfg-options", nargs="*", default=[])
    prepare.add_argument("--format", choices=("tsv", "json"), default="tsv")

    for command in ("list", "tree"):
        inspect = subparsers.add_parser(command, help=f"{command} indexed runs")
        inspect.add_argument("--experiment-dir", required=True)
        inspect.add_argument("--json", action="store_true")
    return parser


def _tree(rows: Dict[str, Dict[str, object]]) -> List[str]:
    children: Dict[Optional[str], List[str]] = {}
    for run_id, row in rows.items():
        parent = row.get("parent_run_id")
        parent_id = str(parent) if parent else None
        children.setdefault(parent_id, []).append(run_id)
    for values in children.values():
        values.sort()

    lines: List[str] = []
    visited = set()

    def visit(run_id: str, prefix: str) -> None:
        if run_id in visited:
            lines.append(f"{prefix}{run_id} [cycle]")
            return
        visited.add(run_id)
        row = rows[run_id]
        lines.append(
            f"{prefix}{run_id} [{row.get('run_kind')} | {row.get('status')}]"
        )
        for child in children.get(run_id, []):
            visit(child, prefix + "  ")

    roots = sorted(
        run_id
        for run_id, row in rows.items()
        if not row.get("parent_run_id") or row.get("parent_run_id") not in rows
    )
    for root in roots:
        parent = rows[root].get("parent_run_id")
        if parent and parent not in rows:
            lines.append(f"{parent} [legacy/unindexed parent]")
            visit(root, "  ")
        else:
            visit(root, "")
    for run_id in sorted(set(rows) - visited):
        visit(run_id, "")
    return lines


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "prepare":
        config_path = Path(args.config)
        config = load_experiment_config(config_path, args.cfg_options)
        result = prepare_named_run(config, config_path, args.cfg_options)
        if args.format == "json":
            print(json.dumps(result, ensure_ascii=False))
        else:
            resume = result["resume_checkpoint"] or "-"
            print(f"{result['run_id']}\t{result['work_dir']}\t{resume}")
        return 0

    rows = latest_index_rows(Path(args.experiment_dir))
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    elif args.command == "list":
        for run_id in sorted(rows):
            row = rows[run_id]
            print(
                "\t".join(
                    (
                        run_id,
                        str(row.get("run_kind")),
                        str(row.get("status")),
                        str(row.get("parent_run_id") or "-"),
                        str(row.get("work_dir")),
                    )
                )
            )
    else:
        print("\n".join(_tree(rows)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
