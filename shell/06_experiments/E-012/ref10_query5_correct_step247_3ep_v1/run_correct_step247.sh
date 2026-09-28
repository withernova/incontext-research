#!/usr/bin/env bash
set -euo pipefail
cd /defaultShare/archive/liuwenchu/projects/IPLoc
test "$(pwd -P)" = /defaultShare/archive/liuwenchu/projects/IPLoc
cd mechanism/iploc-szy
# Direct script entrypoints put tools/ rather than the repository root on
# sys.path.  Give the parent and every torchrun worker the package root.
export PYTHONPATH="$(pwd -P)"
exec /defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python -u - "$@" <<'PY'
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import time

from iploc_szy.branching import load_experiment_config
from iploc_szy.registry import DATASETS

parser = argparse.ArgumentParser()
parser.add_argument('--inspect', action='store_true')
args = parser.parse_args()
project = Path('/defaultShare/archive/liuwenchu/projects/IPLoc')
root = project/'experiments/E-012/ref10-query5-correct-step247-3ep-v1'
root.mkdir(parents=True, exist_ok=True)
lock = (root/'execution.lock').open('a')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
checkpoint = project/'experiments/E-012/checkpoints/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/samples_00015801_step_000247'
source = project/'experiments/E-012/checkpoint-spatial-stability-e009-v1'
selections = {}
for role in ('reference', 'query'):
    path = source/f'step_1153_{role}'/'summary.json'
    value = json.loads(path.read_text())
    assert value['status'] == 'completed' and value['parameters']['role'] == role
    selections[role] = value
teacher_heads = selections['reference']['selected_heads'][:10]
student_heads = selections['query']['selected_heads'][:5]
assert len(teacher_heads) == 10 and len(student_heads) == 5
manifest = project/'experiments/E-009/E009-real-focus-data/manifests/train_only_1shot_focus_valid10522.json'
assert hashlib.sha256(manifest.read_bytes()).hexdigest() == 'bd7037325096cc99097333090ec5d02f64dd9ce2922f04e0e4409d1d635bd6e7'
teacher_root = root/'teacher_step247'
config = 'configs/sft/qwen3vl_8b_lora_focus_1shot_ddp4_4bit.py'
auxiliary = dict(type='ReferenceQueryAttentionDistillation', treatment='correct',
    teacher_manifest=str(teacher_root/'manifest.json'), teacher_heads=teacher_heads,
    student_heads=student_heads, coefficient=0.1, cyclic_roll_seed=20260901,
    allow_variable_head_counts=True)
common = {
    'named_run': {},
    'work_dir': str(root/'training'),
    'model.gradient_checkpointing_kwargs': {'use_reentrant': False},
    'train_dataloader.dataset.ann_file': str(manifest),
    'runner.max_epochs': 3,
    'runner.max_steps': None,
    'runner.optimizer.lr': 1e-4,
    'runner.initialize_from': str(checkpoint),
    'runner.resume_from': None,
    'runner.pipeline': None,
    'runner.seed': 20260901,
    'runner.auxiliary_loss': auxiliary,
    'teacher_precompute': dict(output_dir=str(teacher_root), checkpoint=str(checkpoint),
        source_manifest=str(manifest), teacher_heads=teacher_heads, allow_variable_head_counts=True),
}

def options(values):
    return [f'{key}={value!r}' for key, value in values.items()]

resolved = load_experiment_config(config, options(common))
assert not resolved.get('branch') and not resolved.get('named_run')
assert resolved['runner']['max_epochs'] == 3 and resolved['runner']['optimizer']['lr'] == 1e-4
assert resolved['runner']['initialize_from'] == str(checkpoint) and resolved['runner']['resume_from'] is None
assert resolved['runner']['auxiliary_loss']['treatment'] == 'correct'
dataset = DATASETS.build(resolved['train_dataloader']['dataset'])
assert len(dataset) == 10522
assert (checkpoint/'adapter/adapter_model.safetensors').is_file()
plan = dict(status='validated', checkpoint=str(checkpoint), epochs=3, learning_rate=1e-4,
    treatment='correct', coefficient=0.1, teacher_heads=teacher_heads, student_heads=student_heads,
    train_samples=len(dataset), seed=20260901, optimizer_and_epoch_counters='reset',
    attention_edge='bbox prediction rows p-1 -> reference image tokens for both teacher and student',
    train_model=resolved['model'], runner=resolved['runner'], options=options(common),
    teacher_checkpoint_sha256=hashlib.sha256((checkpoint/'adapter/adapter_model.safetensors').read_bytes()).hexdigest(),
    limitation='Latest reference Top10 showed weaker spatial GT overlap than the legacy teacher on the same eval population; training tests this selection, not an established improvement.')
(root/'resolved_plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({k:plan[k] for k in ('status','checkpoint','epochs','learning_rate','treatment','teacher_heads','student_heads','train_samples')}, ensure_ascii=False), flush=True)
if args.inspect:
    raise SystemExit(0)
if (root/'completed.json').exists() or (root/'training').exists():
    raise FileExistsError('training output already exists; refusing an accidental restart')

def status(phase, **extra):
    temporary = root/'status.tmp.json'
    temporary.write_text(json.dumps(dict(phase=phase, **extra), ensure_ascii=False, indent=2)+'\n')
    temporary.replace(root/'status.json')
    print(phase, flush=True)

torchrun = '/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/torchrun'
try:
    status('waiting_for_gpus')
    while True:
        used = subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'], text=True)
        memory = [int(v.strip()) for v in used.splitlines() if v.strip()]
        if len(memory) == 4 and all(v < 1000 for v in memory):
            break
        time.sleep(30)
    status('precomputing_fixed_teacher')
    if not (teacher_root/'manifest.json').exists():
        teacher = dict(common)
        teacher['work_dir'] = str(root/'teacher_runtime')
        teacher['runner.auxiliary_loss'] = dict(auxiliary, treatment='baseline')
        with (root/'teacher_precompute.log').open('a') as log:
            subprocess.run([torchrun,'--standalone','--nproc_per_node=4',
                'tools/precompute_e009_reference_teacher.py',config,'--cfg-options',*options(teacher)],
                stdout=log, stderr=subprocess.STDOUT, check=True)
    status('training')
    with (root/'train.log').open('x') as log:
        subprocess.run([torchrun,'--standalone','--nproc_per_node=4','tools/train.py',config,
            '--cfg-options',*options(common)], stdout=log, stderr=subprocess.STDOUT, check=True)
    status('completed')
    (root/'completed.json').write_text('{"status":"completed","epochs":3,"learning_rate":0.0001}\n')
except BaseException as error:
    status('failed', exception=type(error).__name__, reason=str(error))
    raise
PY
