#!/usr/bin/env bash
# One Qwen3-VL replica model-sharded across the selected GPUs.
set -euo pipefail

ROOT=/defaultShare/archive/liuwenchu/projects/IPLoc
PROJECT="$ROOT/mechanism/iploc-szy"
PYTHON=/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python
CONFIG="$PROJECT/configs/sft/qwen3vl_8b_lora_focus_bs16.py"

cd "$PROJECT"
test -x "$PYTHON"
test -f "$CONFIG"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1,2,3}"
export PYTHONPATH="$PROJECT${PYTHONPATH:+:$PYTHONPATH}"
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1

# Examples: runner.max_steps=100 train_dataloader.batch_size=4
exec "$PYTHON" tools/train.py "$CONFIG" --cfg-options "$@"
