#!/usr/bin/env bash
set -euo pipefail

PROJECT=/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy
PYTHON_BIN=/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python
CONFIG=configs/head_screening/e012_r004_real_chain_rule.py

cd "$PROJECT"
test "$(pwd -P)" = "$PROJECT"
test -x "$PYTHON_BIN"
export PYTHONPATH="$PROJECT"
exec "$PYTHON_BIN" -u -m iploc_szy.head_screening.r004_real_chain_rule "$CONFIG"
