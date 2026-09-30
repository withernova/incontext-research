"""Read-only held-out E-013 first-score intervention; emit one JSON line per case."""

import hashlib
import json
import math
import re
import sys
from pathlib import Path

PROJECT = Path('/defaultShare/archive/songzhengyue/projects/IPLoc')
E013 = PROJECT / 'experiments/E-013'
PREDICTIONS = E013 / ('focus-confidence-sft/branches/'
    '20260929T055808Z--multi3-rank-cf-latest-eval/evaluation/predictions.jsonl')
MANIFEST = PROJECT / ('experiments/E-009/E009-real-focus-data/manifests/'
    'test_combined_lasot600_gotval_taoval_1shot_focus.json')
MANIFEST_SHA = '48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b'
ADAPTER = E013 / ('focus-confidence-sft/branches/'
    '20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep/'
    'grpo/checkpoints/step_000450/adapter/policy')
MODEL = PROJECT / 'mechanism/models/Qwen3-VL-8B-Instruct'
SCORE = re.compile(r'<score>(0\.[0-9]{2}|1\.00)</score>')
SECOND = re.compile(r'^\s*<answer>(\[[^\]]+\])</answer>\s*<score>(0\.[0-9]{2}|1\.00)</score>')


def cases():
    rows = [json.loads(line) for line in PREDICTIONS.open() if line.strip()]
    if len(rows) != 1766 or len({row['id'] for row in rows}) != len(rows):
        raise ValueError('Unexpected validation prediction count or duplicate IDs')
    chosen = []
    for row in rows:
        cs = row['candidates']
        if len(cs) != 3 or row['selected_candidate_index'] != 0:
            continue
        ious = [c['iou'] for c in cs]
        scores = [c['score'] for c in cs]
        if not all(isinstance(v, (float, int)) and math.isfinite(v)
                   for v in ious + scores):
            continue
        if ious.index(max(ious)) == 1 and ious.count(max(ious)) == 1:
            if len(SCORE.findall(row['raw_prediction'])) != 3:
                raise ValueError('Malformed selected validation prediction')
            chosen.append(row)
    if len(chosen) != 115:
        raise ValueError(f'Unexpected selected count: {len(chosen)}')
    return sorted(chosen, key=lambda r: r['dataset_index'])


def variants(raw, middle=False):
    m = SCORE.search(raw)
    second_start = raw.find('<answer>', m.end())
    if second_start < 0 or raw[m.end():second_start].strip():
        raise ValueError('Unexpected candidate separator')
    prefix = raw[:second_start]
    settings = ([('original', m.group(1)), ('mid_050', '0.50')] if middle else
                [('original', m.group(1)), ('low_001', '0.01'), ('high_099', '0.99')])
    return {name: prefix[:m.start(1)] + value + prefix[m.end(1):]
            for name, value in settings}


def append_prefix(base, prefix, tokenizer):
    import torch
    ids = tokenizer(prefix, add_special_tokens=False)['input_ids']
    if tokenizer.decode(ids, skip_special_tokens=False) != prefix:
        raise ValueError('Prefix tokenizer round-trip failed')
    added = torch.tensor([ids], device=base.input_ids.device,
                         dtype=base.input_ids.dtype)
    result = dict(base)
    result['input_ids'] = torch.cat((base.input_ids, added), dim=1)
    result['attention_mask'] = torch.cat((base.attention_mask,
                                          torch.ones_like(added)), dim=1)
    return result


def main(middle=False):
    import torch
    from PIL import Image
    from iploc_szy.compat import ensure_torchvision_nms_schema
    ensure_torchvision_nms_schema()
    from peft import PeftModel
    from transformers import (AutoProcessor, BitsAndBytesConfig,
                              Qwen3VLForConditionalGeneration,
                              StoppingCriteria, StoppingCriteriaList)
    from iploc_szy.evaluation.bbox import box_iou
    from iploc_szy.evaluation.multi_candidate import MultiCandidateLocalizationDataset

    if not torch.cuda.is_available():
        raise RuntimeError('CUDA unavailable')
    raw_manifest = MANIFEST.read_bytes()
    if hashlib.sha256(raw_manifest).hexdigest() != MANIFEST_SHA:
        raise ValueError('Validation manifest hash mismatch')
    manifest = json.loads(raw_manifest)
    if len(manifest) != 1766:
        raise ValueError('Validation manifest length mismatch')
    selected = cases()
    print(json.dumps({'validation_total': len(manifest), 'eligible': len(selected),
                      'score_above_001': sum(r['candidates'][0]['score'] > 0.01
                                             for r in selected)}), file=sys.stderr, flush=True)

    processor = AutoProcessor.from_pretrained(str(MODEL), local_files_only=True)
    patch_size = processor.image_processor.patch_size
    processor.image_processor.size['longest_edge'] = 4096 * patch_size * patch_size
    quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
        bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16)
    base_model = Qwen3VLForConditionalGeneration.from_pretrained(str(MODEL),
        dtype=torch.bfloat16, device_map={'': 0}, attn_implementation='sdpa',
        quantization_config=quant, local_files_only=True)
    model = PeftModel.from_pretrained(base_model, str(ADAPTER),
                                     is_trainable=False, local_files_only=True)
    model.eval()
    device = model.get_input_embeddings().weight.device
    builder = object.__new__(MultiCandidateLocalizationDataset)
    builder.max_candidates = 3
    builder.instance_search = True
    builder.spatial_order = False
    builder.prompt_protocol = 'focus_confidence'
    builder.prompt_version = 'focus-multi3-instances-v1'
    builder.prompt_options = {}

    for position, row in enumerate(selected):
        builder.rows = []
        builder._append_record(row['dataset_index'], manifest[row['dataset_index']],
                               target_role='positive-image', normalized_scale=1000)
        if len(builder.rows) != 1:
            raise ValueError('Expected one target per validation record')
        sample = builder.rows[0]
        if sample['id'] != row['id'] or sample['answer'] != row['target']:
            raise ValueError('Validation sample ID or target mismatch')
        prompt = processor.apply_chat_template(sample['messages'][:-1],
                                                tokenize=False, add_generation_prompt=True)
        images = []
        for path in sample['image_paths']:
            with Image.open(path) as im:
                images.append(im.convert('RGB'))
        base = processor(text=[prompt], images=images,
                         return_tensors='pt').to(device)
        conditions = {}
        for name, prefix in variants(row['raw_prediction'], middle).items():
            inputs = append_prefix(base, prefix, processor.tokenizer)
            start = inputs['input_ids'].shape[1]

            class StopSecondScore(StoppingCriteria):
                def __call__(self, input_ids, scores, **kwargs):
                    text = processor.batch_decode(input_ids[:, start:],
                                                  skip_special_tokens=True)[0]
                    return '</score>' in text

            with torch.inference_mode():
                output = model.generate(**inputs, do_sample=False,
                    max_new_tokens=96, pad_token_id=processor.tokenizer.eos_token_id,
                    stopping_criteria=StoppingCriteriaList([StopSecondScore()]))
            continuation = processor.batch_decode(output[:, start:],
                                                    skip_special_tokens=True)[0]
            match = SECOND.search(continuation)
            box = None
            score = None
            iou = None
            if match:
                try:
                    box = json.loads(match.group(1))
                    iou = box_iou(box, sample['answer'])
                    score = float(match.group(2))
                except (ValueError, TypeError):
                    pass
            conditions[name] = {'second_box': box, 'second_score': score,
                                'second_iou': iou, 'continuation': continuation[:220]}
        output_row = {'dataset_index': row['dataset_index'], 'id': row['id'],
            'dataset': row['dataset'], 'baseline_scores': [c['score'] for c in row['candidates']],
            'baseline_ious': [c['iou'] for c in row['candidates']],
            'target': row['target'], 'conditions': conditions}
        print(json.dumps(output_row, ensure_ascii=False, allow_nan=False), flush=True)
        if (position + 1) % 10 == 0:
            print(f'completed {position+1}/{len(selected)}', file=sys.stderr, flush=True)


if __name__ == '__main__':
    if sys.argv[1:] not in ([], ['--score-050']):
        raise SystemExit('Usage: python intervene_first_score_validation.py [--score-050]')
    main(middle=sys.argv[1:] == ['--score-050'])
