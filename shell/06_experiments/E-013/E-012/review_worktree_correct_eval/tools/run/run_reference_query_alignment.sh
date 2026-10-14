#!/usr/bin/env bash
set -euo pipefail

PROJECT=/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy
PYTHON_BIN=/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python
TORCHRUN=/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/torchrun
CONFIG=configs/sft/qwen3vl_8b_reference_query_alignment.py
TEACHER_ROOT=/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-R-008-reference-top3-query-top5-ensemble-distill/teacher_step1729
PRECOMPUTE_LOG="$TEACHER_ROOT/precompute.log"

cd "$PROJECT"
export PYTHONPATH="$PROJECT${PYTHONPATH:+:$PYTHONPATH}"
export TOKENIZERS_PARALLELISM=false

if [[ ! -f "$TEACHER_ROOT/manifest.json" ]]; then
    mkdir -p "$TEACHER_ROOT"
    echo "[TEACHER_START] resumable precompute; log=$PRECOMPUTE_LOG"
    "$TORCHRUN" --standalone --nproc_per_node=4 \
        tools/precompute_e009_reference_teacher.py "$CONFIG" \
        2>&1 | tee -a "$PRECOMPUTE_LOG"
fi

for treatment in gt_mask; do
    run_name="E009-R-008-reference-top3-query-top5-ensemble-distill-${treatment}"
    "$PYTHON_BIN" tools/run_branch.py "$CONFIG" \
        "runtime.runner.auxiliary_loss.treatment=${treatment}" \
        "named_run.run_name=${run_name}"
done
