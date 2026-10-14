#!/usr/bin/env bash
# Two DDP ranks; every rank loads a complete, unsharded Qwen3-VL replica.
set -euo pipefail

ROOT=/defaultShare/archive/liuwenchu/projects/IPLoc
PROJECT="$ROOT/mechanism/iploc-szy"
PYTHON=/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python
TORCHRUN=/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/torchrun
CONFIG="$PROJECT/configs/sft/qwen3vl_8b_lora_focus_ddp.py"
ATTENTION_IMPLEMENTATION=sdpa

if [[ "${1:-}" == "--flash-attn" ]]; then
    ATTENTION_IMPLEMENTATION=flash_attention_2
    shift
fi

cd "$PROJECT"
test -x "$PYTHON"
test -x "$TORCHRUN"
test -f "$CONFIG"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-2,3}"
if [[ "$ATTENTION_IMPLEMENTATION" == "flash_attention_2" ]]; then
    RUNTIME_SITE="$ROOT/mechanism/build/flash-attn-2.8.3.post1/runtime-site"
    test -d "$RUNTIME_SITE" || {
        echo "ERROR: compatible FlashAttention runtime is missing: $RUNTIME_SITE" >&2
        exit 2
    }
    export PYTHONPATH="$RUNTIME_SITE:$PROJECT${PYTHONPATH:+:$PYTHONPATH}"
else
    export PYTHONPATH="$PROJECT${PYTHONPATH:+:$PYTHONPATH}"
fi
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"

# Examples: runner.max_steps=100 train_dataloader.batch_size=1
# To request FlashAttention-2: tools/train_focus_ddp.sh --flash-attn ...
exec "$TORCHRUN" --standalone --nproc_per_node=2 \
    tools/train.py "$CONFIG" --cfg-options \
    "model.attn_implementation=$ATTENTION_IMPLEMENTATION" "$@"
