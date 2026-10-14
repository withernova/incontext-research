#!/usr/bin/env bash
# 兼容旧入口；新的通用入口是 tools/run/run_branch.sh。
set -euo pipefail
exec bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy/tools/run/run_branch.sh "$@"
