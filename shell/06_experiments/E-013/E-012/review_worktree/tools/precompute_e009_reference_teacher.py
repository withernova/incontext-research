#!/usr/bin/env python3
"""Precompute the immutable E009 Reference Top-3 teacher artifacts."""

from __future__ import annotations

import argparse
from typing import Optional, Sequence

from iploc_szy.attention_distillation.precompute import precompute_fixed_teacher
from iploc_szy.branching import load_experiment_config
from iploc_szy.builder import build_training
from iploc_szy.utils.distributed import shutdown_distributed


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", help="E009 distillation config")
    parser.add_argument(
        "--cfg-options", nargs="*", default=[], help="Dotted config overrides"
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    config = load_experiment_config(args.config, args.cfg_options)
    runner = build_training(config)
    try:
        precompute_fixed_teacher(runner, config["teacher_precompute"])
        return 0
    finally:
        if runner.context:
            shutdown_distributed(runner.context)


if __name__ == "__main__":
    raise SystemExit(main())

