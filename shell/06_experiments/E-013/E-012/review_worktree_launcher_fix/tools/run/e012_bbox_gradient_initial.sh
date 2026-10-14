#!/usr/bin/env bash
set -euo pipefail
cd /defaultShare/archive/liuwenchu/projects/IPLoc
test "$(pwd -P)" = /defaultShare/archive/liuwenchu/projects/IPLoc
cd mechanism/iploc-szy
# --check-only：只核对清单、checkpoint文件与processor输入，不加载8B权重做筛查。
# checkpoint、已有manifest和抽样配额统一在下方指定的Python config中修改。
if [[ $# -gt 0 ]]; then
  exec /defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python -u \
    -m iploc_szy.head_screening.bbox_gradient \
    configs/head_screening/e012_bbox_gradient_initial.py "$@"
fi
# 无参数时执行config中的正式筛查；日志追加保存，保留上次失败信息。
mkdir -p /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/logs
/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python -u \
  -m iploc_szy.head_screening.bbox_gradient \
  configs/head_screening/e012_bbox_gradient_initial.py 2>&1 | \
  tee -a /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/logs/R-001-bbox-gradient-initial.log
