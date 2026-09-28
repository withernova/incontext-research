#!/usr/bin/env python3
"""Compatibility alias for the inference/evaluation entry point."""

from infer import main


if __name__ == "__main__":
    raise SystemExit(main())
