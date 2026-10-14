#!/usr/bin/env bash
# One-GPU, one-rank DDP-style 1-shot NF4 QLoRA SFT.
set -euo pipefail

ROOT=/defaultShare/archive/liuwenchu/projects/IPLoc
PROJECT="$ROOT/mechanism/iploc-szy"
PYTHON=/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python
TORCHRUN=/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/torchrun
CONFIG="$PROJECT/configs/sft/qwen3vl_8b_lora_focus_1shot_single_4bit.py"

cd "$PROJECT"
test -x "$PYTHON"
test -x "$TORCHRUN"
test -f "$CONFIG"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
export PYTHONPATH="$PROJECT${PYTHONPATH:+:$PYTHONPATH}"
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"

# Keep SDPA: the host's FlashAttention binary is not GLIBC-compatible.
exec "$TORCHRUN" --standalone --nproc_per_node=1 \
    tools/train.py "$CONFIG" --cfg-options "$@"
