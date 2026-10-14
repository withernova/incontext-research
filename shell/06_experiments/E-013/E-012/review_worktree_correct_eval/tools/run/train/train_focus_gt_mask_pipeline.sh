#!/usr/bin/env bash
set -euo pipefail
PROJECT=/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy
cd "$PROJECT"
test "$(pwd -P)" = "$PROJECT"
exec bash tools/run/train/train_named_ddp4.sh \
  configs/sft/qwen3vl_8b_focus_gt_mask_pipeline.py "$@"
