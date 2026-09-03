#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"
exec "${PYTHON_BIN:-/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python3}" \
  -m iplocid.pipelines.full_lasot_role_audit \
  --config "$ROOT/configs/e010_r008.json" "$@"
