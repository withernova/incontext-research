#!/usr/bin/env bash
# Four-GPU, four-rank DDP 1-shot NF4 QLoRA SFT.
set -euo pipefail

ROOT=/defaultShare/archive/liuwenchu/projects/IPLoc
PROJECT="$ROOT/mechanism/iploc-szy"
PYTHON=/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python
TORCHRUN=/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/torchrun
CONFIG="$PROJECT/configs/sft/qwen3vl_8b_lora_focus_1shot_ddp4_4bit.py"
WORK_DIR="$ROOT/experiments/E-009/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4"

cd "$PROJECT"
test -x "$PYTHON"
test -x "$TORCHRUN"
test -f "$CONFIG"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1,2,3}"
export PYTHONPATH="$PROJECT${PYTHONPATH:+:$PYTHONPATH}"
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"
LOG_DIR="$WORK_DIR/logs"
LOG_FILE="$LOG_DIR/train.log"
mkdir -p "$LOG_DIR"

# Keep SDPA: the host's FlashAttention binary is not GLIBC-compatible.
{
    printf '[LAUNCH] %s config=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$CONFIG"
    "$TORCHRUN" --standalone --nproc_per_node=4 \
        tools/train.py "$CONFIG" --cfg-options "$@"
} 2>&1 | tee -a "$LOG_FILE"
