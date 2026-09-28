#!/usr/bin/env bash
set -euo pipefail
cd /defaultShare/archive/liuwenchu/projects/IPLoc
test "$(pwd -P)" = /defaultShare/archive/liuwenchu/projects/IPLoc
cd mechanism/iploc-szy
exec /defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python -u \
  -m iploc_szy.head_screening.gradient_attention_maps \
  configs/head_screening/e012_gradient_top10_attention_maps.py "$@"
