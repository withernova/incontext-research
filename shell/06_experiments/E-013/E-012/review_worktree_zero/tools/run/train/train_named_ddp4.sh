#!/usr/bin/env bash
set -euo pipefail

PROJECT=/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy
PYTHON_BIN=/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python
TORCHRUN_BIN=/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/torchrun

if [[ $# -lt 1 ]]; then
  echo "Usage: bash tools/run/train/train_named_ddp4.sh CONFIG [key=value ...]" >&2
  exit 64
fi

CONFIG=$1
shift
if [[ "$CONFIG" != /* ]]; then
  CONFIG="$PROJECT/$CONFIG"
fi

cd "$PROJECT"
test -x "$PYTHON_BIN"
test -x "$TORCHRUN_BIN"
test -f "$CONFIG"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1,2,3}"
export PYTHONPATH="$PROJECT${PYTHONPATH:+:$PYTHONPATH}"
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"

RUN_INFO=$("$PYTHON_BIN" tools/named_run.py prepare "$CONFIG" \
  --cfg-options "$@" --format tsv)
IFS=$'\t' read -r RUN_ID WORK_DIR RESUME_CHECKPOINT <<< "$RUN_INFO"
if [[ -z "$RUN_ID" || -z "$WORK_DIR" || -z "$RESUME_CHECKPOINT" ]]; then
  echo "named-run preparation returned incomplete output" >&2
  exit 70
fi

RUN_OPTIONS=(
  "$@"
  "work_dir=$WORK_DIR"
  "named_run.resolved_run_id=$RUN_ID"
  "named_run.resolved_resume_checkpoint=$RESUME_CHECKPOINT"
)
if [[ "$RESUME_CHECKPOINT" == "-" ]]; then
  RUN_OPTIONS+=("runner.resume_from=None")
else
  RUN_OPTIONS+=("runner.resume_from=$RESUME_CHECKPOINT")
fi

mkdir -p "$WORK_DIR/logs"
echo "[NAMED_RUN] run_id=$RUN_ID"
echo "[NAMED_RUN] work_dir=$WORK_DIR"
echo "[NAMED_RUN] resume_from=$RESUME_CHECKPOINT"
printf '[LAUNCH] %s config=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$CONFIG"

"$TORCHRUN_BIN" --standalone --nproc_per_node=4 tools/train.py "$CONFIG" \
  --cfg-options "${RUN_OPTIONS[@]}" 2>&1 | tee -a "$WORK_DIR/logs/train.log"
