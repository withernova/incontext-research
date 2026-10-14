#!/usr/bin/env bash
set -euo pipefail

PROJECT=/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy
CONFIG=configs/sft/qwen3vl_8b_focus_branch.py
CHECKPOINT=/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/ref10-query5-correct-step247-3ep-v1/training/checkpoints/samples_00031566_step_000494

cd "$PROJECT"
test "$(pwd -P)" = "$PROJECT"
test -f "$CHECKPOINT/adapter/adapter_model.safetensors"
test -f "$CHECKPOINT/trainer_state.pt"

# Reuse the established branch evaluator and named-run logging. This evaluates
# the latest complete checkpoint (step 494), not the adapter-only final step 495.
exec bash tools/run/run_branch.sh "$CONFIG" \
  branch.action=evaluate \
  branch.source=e012_correct_step0494 \
  branch.source_profiles.e012_correct_step0494.kind=checkpoint \
  branch.source_profiles.e012_correct_step0494.experiment_id=E-012 \
  branch.source_profiles.e012_correct_step0494.parent_checkpoint="$CHECKPOINT" \
  named_run.run_name=ref10-query5-correct-step0494-eval \
  named_run.run_kind=branch-evaluate \
  named_run.notes='E-012 correct训练最近完整checkpoint step494的标准FOCUS自回归评测；final step495仅有adapter，不在本run中冒充完整checkpoint。' \
  "$@"
