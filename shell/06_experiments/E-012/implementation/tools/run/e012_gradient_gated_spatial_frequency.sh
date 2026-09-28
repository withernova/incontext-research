#!/usr/bin/env bash
set -euo pipefail
cd /defaultShare/archive/liuwenchu/projects/IPLoc
test "$(pwd -P)" = /defaultShare/archive/liuwenchu/projects/IPLoc
cd mechanism/iploc-szy
exec /defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python -u \
  -m iploc_szy.head_screening.gradient_gated_spatial_frequency \
  configs/head_screening/e012_gradient_gated_spatial_frequency.py "$@"
