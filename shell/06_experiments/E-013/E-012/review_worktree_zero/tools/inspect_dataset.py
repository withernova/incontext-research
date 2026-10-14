#!/usr/bin/env python3
"""Inspect samples produced by a configured training dataset."""

import argparse
import json
from typing import Optional, Sequence

from iploc_szy import Config, DATASETS


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse dataset config and inspection limit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    parser.add_argument("--limit", type=int, default=3)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Build the dataset and print a bounded JSON preview."""
    args = parse_args(argv)
    config = Config.fromfile(args.config)
    dataset = DATASETS.build(config["train_dataloader"]["dataset"])
    output = {
        "length": len(dataset),
        "samples": [dataset[index] for index in range(min(args.limit, len(dataset)))],
    }
    print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
