#!/usr/bin/env bash
set -euo pipefail
export PYTHONNOUSERSITE=1
RUN=/home/featurize/work/mechanism/explog/E-003/runs/E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140
python3 "$RUN/config/analyze.py"  --source /home/featurize/work/mechanism/explog/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128/results/LASOT_local_1shot_T2_n140_v2/generated_texts/e003_r004b_joint_n140.json  --source-summary /home/featurize/work/mechanism/explog/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128/analysis/joint_f1_iou.json  --out "$RUN" --seed 20260721 --replicates 10000
