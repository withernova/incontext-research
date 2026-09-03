"""Safety gate for E010-R-008 while its canonical protocol is undefined.

The current Run is in ``research_design`` with changes requested.  It has no
approved dataset, attention rows, head sets, metrics, or launch command, so
this module intentionally cannot run an experiment.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMA = "iplocid.e010.r008.unconfigured/v1"
MESSAGE = (
    "E010-R-008 has no current executable protocol: complete its new canonical "
    "research design and obtain review/authorization before implementing or running it."
)


def load_unconfigured_config(path: str) -> dict:
    config = json.loads(Path(path).read_text())
    if config != {"schema": SCHEMA, "state": "unconfigured"}:
        raise ValueError("E010-R-008 config must remain the unconfigured safety contract")
    return config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    load_unconfigured_config(args.config)
    raise SystemExit(MESSAGE)


if __name__ == "__main__":
    main()
