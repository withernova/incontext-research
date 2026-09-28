#!/usr/bin/env bash
# Compatibility alias; canonical launcher is tools/run/train/train_grounding_ddp4.sh.
set -euo pipefail
exec bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy/tools/run/train/train_grounding_ddp4.sh "$@"
