#!/usr/bin/env bash
set -euo pipefail
cd /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy
exec /defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python -u \
  -m iploc_szy.head_screening.reference_gradient_gated_spatial_frequency \
  configs/head_screening/e012_reference_spatial_iou050.py "$@"
