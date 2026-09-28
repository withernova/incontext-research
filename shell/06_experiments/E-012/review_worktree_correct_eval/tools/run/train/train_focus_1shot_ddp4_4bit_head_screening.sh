#!/usr/bin/env bash
set -euo pipefail

PROJECT=/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy
CONFIG=configs/sft/qwen3vl_8b_lora_focus_1shot_ddp4_4bit_head_screening.py

exec bash "$PROJECT/tools/run/train/train_named_ddp4.sh" "$CONFIG" "$@"
