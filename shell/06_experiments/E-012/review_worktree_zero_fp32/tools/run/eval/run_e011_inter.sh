#!/usr/bin/env bash
# 通用 branch 启动器：实验来源、任务类型和运行参数全部由 config 决定。
set -euo pipefail

PROJECT=/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy
PYTHON_BIN=/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python
DEFAULT_CONFIG=configs/sft/qwen3vl_8b_focus_branch.py
# 都作为 --inspect 或 key=value override 继续传给 tools/run_branch.py。
CONFIG="$DEFAULT_CONFIG"
if (( $# > 0 )) && [[ "$1" == *.py ]]; then
    CONFIG="$1"
    shift
fi

cd "$PROJECT"
test "$(pwd -P)" = "$PROJECT"
export PYTHONPATH="$PROJECT"
exec "$PYTHON_BIN" tools/run_branch.py "$CONFIG" branch.action=attention_intervene "$@"
