#!/usr/bin/env bash
set -euo pipefail

PROJECT=/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy
PYTHON_BIN=/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python
CONFIG=configs/sft/qwen3vl_8b_reference_query_alignment.py

cd "$PROJECT"
export PYTHONPATH="$PROJECT${PYTHONPATH:+:$PYTHONPATH}"
export TOKENIZERS_PARALLELISM=false

# Exploratory dynamic arm: fixed Reference/Query head IDs, current-model online
# Reference target with stop-gradient.  It intentionally does not precompute or
# read the fixed step1729 teacher artifacts used by the preregistered four arms.
"$PYTHON_BIN" tools/run_branch.py "$CONFIG" \
    runtime.runner.auxiliary_loss.treatment=dynamic_teacher \
    runtime.runner.auxiliary_loss.teacher_manifest=None \
    runtime.runner.optimizer.lr=4e-5 \
    named_run.run_name=E009-dynamic-reference-top3-query-top5-online-distill \
    named_run.run_kind=reference-query-online-attention-distillation
