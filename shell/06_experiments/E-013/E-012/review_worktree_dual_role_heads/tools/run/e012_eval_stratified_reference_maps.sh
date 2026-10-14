#!/usr/bin/env bash
set -euo pipefail
PROJECT=/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy
cd "$PROJECT"
test "$(pwd -P)" = "$PROJECT"
export PYTHONPATH="$PROJECT${PYTHONPATH:+:$PYTHONPATH}"
exec /defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python -u \
  -m iploc_szy.head_screening.eval_stratified_reference_maps \
  configs/head_screening/e012_eval_stratified_reference_maps.py "$@"
