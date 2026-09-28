#!/usr/bin/env bash
set -euo pipefail

PROJECT=/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy
CONFIG=configs/sft/e012_ref10_query5_correct_final_eval.py

cd "$PROJECT"
test "$(pwd -P)" = "$PROJECT"
exec bash tools/run/run_branch.sh "$CONFIG" "$@"
