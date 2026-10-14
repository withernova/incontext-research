#!/usr/bin/env bash
set -euo pipefail
PROJECT=/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy
PYTHON_BIN=/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python
CONFIG=configs/eval/qwen3vl_8b_native_grounding.py
if (( $# > 1 )); then
    echo "Usage: $0 [config.py]; edit experiment parameters in config" >&2
    exit 64
fi
if (( $# == 1 )); then CONFIG="$1"; fi
cd "$PROJECT"
test "$(pwd -P)" = "$PROJECT"
export PYTHONPATH="$PROJECT"
exec "$PYTHON_BIN" tools/launch.py "$CONFIG"
