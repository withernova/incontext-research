#!/usr/bin/env bash
# Authorized data rendering only: no model inference or optimizer updates.
set -euo pipefail
ssh -o BatchMode=yes -o ClearAllForwardings=yes SZY-3090 'cd /defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/iploc-szy && PYTHONPATH=. /songzhengyue/miniconda3/envs/IPLoc/bin/python -' <<'PY'
import hashlib
import json
import os
from pathlib import Path
import subprocess
r = Path('/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018')
a = r / 'payload/augmentation'
s = json.loads((a / 'summary.json').read_text())
for name, expected in s['hashes'].items():
    assert hashlib.sha256((a / name).read_bytes()).hexdigest() == expected
assert not (r / 'payload/selection_data').exists()
assert hashlib.sha256((r / 'metrics.json').read_bytes()).hexdigest() == s['original_metrics_sha256']
command = ['/songzhengyue/miniconda3/envs/IPLoc/bin/python', 'tools/prepare_candidate_selection.py', 'sft', '--manifest', str(a / 'combined_manifest.json'), '--manifest-sha256', s['hashes']['combined_manifest.json'], '--predictions', str(a / 'combined_predictions.jsonl'), '--predictions-sha256', s['hashes']['combined_predictions.jsonl'], '--seed', '20260901', '--min-oracle', '0.5', '--min-gap', '0.05', '--output', str(r / 'payload/selection_data')]
with (r / 'selection_render_command.json').open('x') as f:
    json.dump(command, f, indent=2)
with (r / 'selection_render.log').open('x') as f:
    result = subprocess.run(command, env=dict(os.environ, PYTHONPATH='.'), stdout=f, stderr=subprocess.STDOUT)
with (r / '.selection-render-exit-code').open('x') as f:
    f.write(str(result.returncode) + '\n')
print('Selection data rendering exit:', result.returncode, flush=True)
raise SystemExit(result.returncode)
PY
