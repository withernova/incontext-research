#!/usr/bin/env bash
set -euo pipefail
cd /defaultShare/archive/liuwenchu/projects/IPLoc
test "$(pwd -P)" = /defaultShare/archive/liuwenchu/projects/IPLoc
task_root=/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/checkpoint-spatial-stability-e009-v1
python_bin=/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python

"$python_bin" - <<'PY'
from pathlib import Path
import hashlib, json, shutil
root = Path.cwd()
task = root / 'experiments/E-012/checkpoint-spatial-stability-e009-v1'
source = root / 'experiments/E-009/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/checkpoints'
destination = root / 'experiments/E-012/checkpoints/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4'
rows = []
for step in (83, 577, 1153, 1729):
    matches = list(source.glob(f'*step_{step:06d}'))
    assert len(matches) == 1
    src = matches[0]
    dst = destination / src.name
    if dst.exists():
        raise FileExistsError(f'refusing to overwrite {dst}')
    shutil.copytree(src, dst)
    source_files = sorted(p.relative_to(src) for p in src.rglob('*') if p.is_file())
    assert source_files == sorted(p.relative_to(dst) for p in dst.rglob('*') if p.is_file())
    for relative in source_files:
        a, b = src / relative, dst / relative
        sha = hashlib.sha256(a.read_bytes()).hexdigest()
        assert sha == hashlib.sha256(b.read_bytes()).hexdigest(), str(relative)
        rows.append(dict(step=step, source=str(a), destination=str(b), bytes=a.stat().st_size, sha256=sha))
(task/'checkpoint_copy_manifest.json').write_text(json.dumps(dict(status='verified', files=rows),indent=2)+'\n')
print(f'CHECKPOINT_COPY_VERIFIED checkpoints=4 files={len(rows)} bytes={sum(r["bytes"] for r in rows)}',flush=True)
PY

cd mechanism/iploc-szy
"$python_bin" - <<'PY'
from pathlib import Path
import hashlib, json, tempfile
from iploc_szy.head_screening.reference_gradient_gated_spatial_frequency import source_from_selection_summary
task=Path('/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/checkpoint-spatial-stability-e009-v1')
with tempfile.TemporaryDirectory(dir=task) as temporary:
    root=Path(temporary)
    manifest=root/'manifest.json';manifest.write_text('[]')
    summary=root/'summary.json'
    payload=dict(status='completed',source_samples=2,parameters={},source=dict(root=str(root/'forbidden-ancestor'),selected_indices=[0,1],manifest=str(manifest),manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),config={}))
    summary.write_text(json.dumps(payload))
    digest=hashlib.sha256(summary.read_bytes()).hexdigest()
    source_from_selection_summary(summary,digest)
    try: source_from_selection_summary(summary,'0'*64)
    except ValueError: pass
    else: raise AssertionError('bad summary hash accepted')
    manifest.write_text('[1]')
    try: source_from_selection_summary(summary,digest)
    except ValueError: pass
    else: raise AssertionError('changed manifest accepted')
print('SOURCE_CHECKS_PASSED no_ancestor_reads, summary_hash, manifest_hash',flush=True)
PY

run_selection() {
  local step="$1" role="$2" suffix="$3"
  shift 3
  local checkpoint
  case "$step" in
    83) checkpoint=samples_00005267_step_000083 ;;
    577) checkpoint=samples_00036869_step_000577 ;;
    1153) checkpoint=samples_00073738_step_001153 ;;
    1729) checkpoint=samples_00110607_step_001729 ;;
    *) return 2 ;;
  esac
  local reference hash
  if [[ "$role" == query ]]; then
    reference=gradient-gated-spatial-frequency-r001-v2
    hash=cc76ff624e85382ee300f75082ff6c0f0fa894ea7697ecc3b743d92008b9e99a
  else
    reference=reference-gradient-gated-spatial-frequency-r001-v1
    hash=b835bf0a05d49c88d7766381baa848d2bcf5120cb71f171d78919391e7a2a2bf
  fi
  "$python_bin" -u -m iploc_szy.head_screening.reference_gradient_gated_spatial_frequency \
    configs/head_screening/e012_reference_gradient_gated_spatial_frequency.py \
    --source-summary "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/$reference/summary.json" \
    --source-summary-sha256 "$hash" \
    --checkpoint "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/checkpoints/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/$checkpoint" \
    --role "$role" --output-dir "$task_root/step_${step}_${role}${suffix}" --device-map balanced "$@"
}

for step in 83 577 1153 1729; do
  for role in query reference; do
    run_selection "$step" "$role" '' --check-only
  done
done
CUDA_VISIBLE_DEVICES=0,1 run_selection 83 query _smoke --samples-per-dataset 2 > "$task_root/smoke_query.log" 2>&1 &
smoke_a=$!
CUDA_VISIBLE_DEVICES=2,3 run_selection 1729 reference _smoke --samples-per-dataset 2 > "$task_root/smoke_reference.log" 2>&1 &
smoke_b=$!
wait "$smoke_a"
wait "$smoke_b"
echo SMOKE_BOTH_ROLES_PASSED

worker() {
  for step in "$@"; do
    for role in query reference; do
      run_selection "$step" "$role" '' > "$task_root/step_${step}_${role}.log" 2>&1
    done
  done
}
CUDA_VISIBLE_DEVICES=0,1 worker 83 577 &
worker_a=$!
CUDA_VISIBLE_DEVICES=2,3 worker 1153 1729 &
worker_b=$!
wait "$worker_a"
wait "$worker_b"
echo ALL_EIGHT_SELECTIONS_COMPLETED
