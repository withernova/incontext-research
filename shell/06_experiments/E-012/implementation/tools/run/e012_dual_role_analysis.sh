#!/usr/bin/env bash
# Unified launcher for E-012 R-004--R-010 analysis runs.
set -euo pipefail

PROJECT=/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy
PYTHON_BIN=/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python
DEFAULT_CONFIG=configs/head_screening/e012_contribution_calculation_check.py

if (( $# > 2 )); then
    echo "Usage: $0 [config.py] [--inspect]" >&2
    exit 64
fi
CONFIG="$DEFAULT_CONFIG"
MODE=""
for argument in "$@"; do
    if [[ "$argument" == "--inspect" ]]; then
        MODE="--inspect"
    elif [[ "$CONFIG" == "$DEFAULT_CONFIG" ]]; then
        CONFIG="$argument"
    else
        echo "Only one config path is accepted; put all parameters in the Python config." >&2
        exit 64
    fi
done

cd "$PROJECT"
test "$(pwd -P)" = "$PROJECT"
export PYTHONPATH="$PROJECT"
COMMAND=("$PYTHON_BIN" tools/launch.py "$CONFIG")
if [[ -n "$MODE" ]]; then COMMAND+=("$MODE"); fi
exec "${COMMAND[@]}"
