"""E-014 step800: original 1766 queries, shared evaluator, eight replicas."""
import json
from pathlib import Path

_base_ = '../../../sft/qwen3vl_8b_lora_focus_1shot_single_4bit.py'
_root = Path('/defaultShare/archive/songzhengyue/projects/IPLoc')
_checkpoint = _root / 'experiments/E-014/e014-variable-symmetric-sft659-puregrpo-seed11451/resume-100/grpo/checkpoints/step_000800'
_work = _root / 'experiments/E-014/e014-step800-variable-candidates-eval1766-8gpu/payload'
# The shell pins and checks these metadata files before torchrun. No model is
# loaded by this config; no query GT enters E-014's generation conversation.
_adapter = json.loads((_checkpoint / 'adapter/policy/adapter_config.json').read_text())
_inputs = json.loads((_work / 'inputs.json').read_text())
model = dict(model_path=str(_root / 'mechanism/models/Qwen3-VL-8B-Instruct'),
             lora=dict(r=_adapter['r'], alpha=_adapter['lora_alpha'],
                       dropout=_adapter['lora_dropout'], target_modules=_adapter['target_modules']))
work_dir = str(_work)
test_dataloader = dict(dataset=dict(
    type='E014VariableCandidateLocalizationDataset', ann_file=str(_work / 'manifest.json'),
    ann_file_sha256=_inputs['derived_manifest_sha256'], target_role='positive-image', normalized_scale=1000))
evaluator = dict(type='E014VariableCandidateLocalizationEvaluator', iou_thresholds=(0.25, 0.5, 0.75))
evaluation = dict(dataloader='test_dataloader', checkpoint=str(_checkpoint), adapter_subdir='adapter/policy',
                  max_new_tokens=192, do_sample=False, vision_max_patch_tokens=4096, seed=20260901)
launch = dict(action='evaluate', nproc_per_node=8)
del json, Path, _root, _checkpoint, _work, _adapter, _inputs
