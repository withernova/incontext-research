#!/usr/bin/env bash
# 兼容旧的 FOCUS 入口；默认仍使用原 FOCUS tasks config。
set -euo pipefail
PROJECT=/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy
if (( $# > 0 )) && [[ "$1" == *.py ]]; then
    exec bash "$PROJECT/tools/run/run_branch.sh" "$@"
fi
exec bash "$PROJECT/tools/run/run_branch.sh" \
    configs/sft/qwen3vl_8b_focus_tasks.py "$@"
