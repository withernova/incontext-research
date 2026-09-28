#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
exec python -u -m iploc_szy.head_screening.head_circuit \
  configs/head_screening/e012_head_circuit_zero_attention.py "$@"
