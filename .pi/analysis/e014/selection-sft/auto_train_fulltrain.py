"""Pinned one-Run sequence: event wait, artifact gate, approved 5-epoch training."""
import collections
import ctypes
import hashlib
import json
import os
from pathlib import Path
import select
import subprocess
import time

ROOT = Path('/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014')
DATA = ROOT / 'e014-selection-fulltrain-step200-gtaugment-20261018'
RUN = ROOT / 'e014-selection-fulltrain-gt-lora5epoch-20261019'
REPO = Path('/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/iploc-szy')
PYTHON = '/songzhengyue/miniconda3/envs/IPLoc/bin/python'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load(p):
    return json.loads(Path(p).read_text())

def lines(p):
    return [json.loads(x) for x in Path(p).read_text().splitlines()]

def save(p, obj):
    with Path(p).open('x') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)

# No timed polling or automatic restart. The deadline only bounds failure waiting.
exit_file = DATA / '.selection-render-exit-code'
lib = ctypes.CDLL(None, use_errno=True)
fd = lib.inotify_init1(os.O_NONBLOCK)
if fd < 0:
    raise OSError(ctypes.get_errno(), 'inotify_init1')
if lib.inotify_add_watch(fd, str(DATA).encode(), 0x8 | 0x80 | 0x100) < 0:
    raise OSError(ctypes.get_errno(), 'inotify_add_watch')
print('AUTO_STAGE waiting_for_existing_render; event-driven, no polling', flush=True)
deadline = time.monotonic() + 21600
try:
    while True:
        text = exit_file.read_text().strip() if exit_file.exists() else ''
        if text:
            assert text == '0', 'Data rendering failed; training prohibited'
            break
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('Existing rendering did not finish within 6 hours')
        ready, _, _ = select.select([fd], [], [], remaining)
        if ready:
            os.read(fd, 65536)
finally:
    os.close(fd)

print('AUTO_STAGE auditing_data', flush=True)
a = DATA / 'payload/augmentation'
d = DATA / 'payload/selection_data'
s = load(a / 'summary.json')
expected = {
    'combined_manifest.json': '0b5a5b613efcee3d576de9e59847226d3002680cfa6b7d7cef545e7f463cd834',
    'combined_predictions.jsonl': '66abf85db3550cff665e92755ba79b507097ab30ce46a9b6574a75c2d6309397',
    'augmentation_audit.json': 'bd91752e02879a8a1c34b75e59d3e21c427adac9058aa977550cf4d67fa8f33f',
}
for name, digest in expected.items():
    assert sha(a / name) == digest
assert sha(DATA / 'payload/generation/evaluation/predictions.jsonl') == '973c0503b562dcca84b6ec67b0ffebf60049c1ca36dab4e8ddbb0e2f3fb7b412'
assert sha(DATA / 'metrics.json') == 'c9c91cb3cdf37399c4dc3c5adb394e4206fc9b11c67fcb1d30e7cc04215d39f5'
records = load(a / 'combined_manifest.json')
predictions = lines(a / 'combined_predictions.jsonl')
original = lines(DATA / 'payload/generation/evaluation/predictions.jsonl')
original.sort(key=lambda x: x['dataset_index'])
assert len(records) == len(predictions) == 8701 and len(original) == 8367
inserted = 0
for i, row in enumerate(original):
    p = predictions[i]
    assert row['id'] == p['id'] == f'{i}-1'
    inject = bool(row['candidates']) and row['oracle_iou'] < .5
    assert p['candidates'][:len(row['candidates'])] == row['candidates']
    assert len(p['candidates']) == len(row['candidates']) + int(inject)
    assert p['target'] == row['target'] and p['selected_candidate_index'] == row['selected_candidate_index']
    if inject:
        gt = p['candidates'][-1]
        assert gt['origin'] == 'gt_injected' and gt['box'] == json.loads(row['target']) and gt['iou'] == 1
        inserted += 1
assert inserted == 729
old = ROOT / 'e014-selection-sft-data-step200-20261018/payload/selection_data'
assert sha(old / 'validation_manifest.json') == '65fa13a466f819b5c25a2d641c8996c280be107c1229970bba670efa8987454c'
assert sha(old / 'validation_predictions.jsonl') == '7064e524fc57a66243329e7d5bfd8489544d4338e0f7b90cdc02bb47cbf648c1'
assert records[8367:] == load(old / 'validation_manifest.json')
for j, row in enumerate(lines(old / 'validation_predictions.jsonl')):
    p = predictions[8367+j]
    assert p['id'] == f'{8367+j}-1' and p['dataset_index'] == 8367+j
    for key, value in row.items():
        if key not in {'id', 'dataset_index'}:
            assert p[key] == value
assert not ({x['metadata']['source_group'] for x in records[:8367]} & {x['metadata']['source_group'] for x in records[8367:]})
m = load(d / 'metrics.json')
assert m['status'] == 'completed' and m['examples']['train'] == 8379 and m['eligible_sources']['train'] == 3571
assert m['min_oracle'] == .5 and m['min_gap'] == .05 and m['seed'] == 20260901
assert m['source_manifest_sha256'] == expected['combined_manifest.json'] and m['source_predictions_sha256'] == expected['combined_predictions.jsonl']
assert m['validation_samples'] == 334 and m['validation_multi'] == 123
rendered = 0
counts = collections.Counter()
for split in ['train', 'validation']:
    items = load(d / (split + '.json'))
    assert sha(d / (split + '.json')) == m['manifest_hashes'][split]
    assert len(items) == m['examples'][split] and len({x['id'] for x in items}) == len(items)
    groups = collections.defaultdict(list)
    for x in items:
        i = x['source_index']; p = predictions[i]; record = records[i]
        assert x['source_split'] == record['metadata']['selection_split'] == split
        assert x['group'] == record['metadata']['source_group'] and x['source_id'] == p['id']
        order = x['original_candidate_order']; cs = p['candidates']
        assert sorted(order) == list(range(len(cs))) and len(cs) >= 2
        best = max(range(len(cs)), key=lambda k: cs[k]['iou'])
        ranked = sorted([q['iou'] for q in cs], reverse=True)
        assert ranked[0] >= .5 and ranked[0] - ranked[1] > .05
        assert x['original_best_index'] == best and x['answer'] == str(order.index(best)+1)
        assert x['messages'][-1]['content'] == x['answer']
        assert x['candidate_boxes'] == [cs[k]['box'] for k in order]
        assert len(x['image_paths']) == len(x['image_sha256']) == 2
        render = load(Path(x['image_paths'][0]).parent / 'rendering.json')
        assert render[1]['boxes_normalized'] == x['candidate_boxes']
        assert render[0]['boxes_normalized'] == [json.loads(x['reference_answers'][0])]
        assert render[0]['labels'] == ['REF'] and render[1]['labels'] == [str(k+1) for k in range(len(cs))]
        for path, digest, meta in zip(x['image_paths'], x['image_sha256'], render):
            assert Path(path).resolve().is_relative_to(d.resolve())
            assert meta['rendered'] == path and meta['rendered_sha256'] == digest and sha(path) == digest
            rendered += 1
        groups[i].append(x)
        counts[split + ':' + record['dataset']] += 1
    assert len(groups) == m['eligible_sources'][split]
    for i, variants in groups.items():
        n = len(predictions[i]['candidates'])
        assert len(variants) == (n if split == 'train' else 1)
        if split == 'train':
            assert sorted(int(v['answer']) for v in variants) == list(range(1,n+1))

# Never steal a GPU from an unrelated job at the delayed start boundary.
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
assert head == '53ab7653602f62ffc1d5c9dadfbefccf7ad67474'
assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=REPO, text=True).strip()
assert not subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader'], text=True).strip(), 'GPU occupied; stop, no retry'
train_sha = sha(d / 'train.json')
save(RUN / 'data_acceptance.json', dict(status='passed', train_sha256=train_sha, train_examples=8379, unique_train_sources=3571, gt_injected_sources=729, rendered_images_verified=rendered, dataset_examples=dict(counts), source_hashes=expected, validation_groups_disjoint=True))
print('AUTO_STAGE data_accepted', train_sha, flush=True)
(RUN / 'payload').mkdir(exist_ok=False)
command = ['bash','tools/run.sh','configs/sft/candidate_selection_lora.py','--cfg-options',f'work_dir={RUN}/payload/training','model.model_path=/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct',f'train_dataloader.dataset.ann_file={d}/train.json',f'train_dataloader.dataset.ann_file_sha256={train_sha}','runner.max_epochs=5','runner.resume_from=None','runner.initialize_from=None']
save(RUN / 'actual_training_command.json', command)
print('AUTO_STAGE training_started', flush=True)
result = subprocess.run(command, cwd=REPO, env=dict(os.environ, PYTHONPATH='.', OMP_NUM_THREADS='1', IPLOC_PYTHON=PYTHON))
if result.returncode:
    raise SystemExit(result.returncode)
full = load(RUN / 'payload/training/metrics.json')
assert full['status'] == 'passed' and full['configured_max_epochs'] == 5
# Full history remains untouched. A bounded summary avoids the management reader's 64KiB limit.
summary = {k:v for k,v in full.items() if isinstance(v,(str,int,float,bool)) or v is None}
summary['full_metrics_path'] = str(RUN / 'payload/training/metrics.json')
summary['full_metrics_sha256'] = sha(RUN / 'payload/training/metrics.json')
save(RUN / 'metrics.json', summary)
print('SURVEY_TOOL_RUN_COMPLETE', flush=True)
