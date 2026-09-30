"""Small read-only E-013 first-score intervention with paired model continuations.

Run on the registered server in its IPLoc Python environment. All input paths
must resolve inside the registered project root. Prints one JSON result line.
"""

import json
import math
import re
import sys
from pathlib import Path


PROJECT = Path("/defaultShare/archive/songzhengyue/projects/IPLoc").resolve()
ALLOWED_GOT10K = Path("/defaultShare/pubdata/GOT10k")
LEGACY_PREFIX = "/defaultShare/archive/liuwenchu/projects/IPLoc/"
TRAIN = PROJECT / "experiments/E-013/focus-confidence-sft/branches/20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep"
MANIFEST = PROJECT / "experiments/E-013/overnight-train-2k/trainable_pairs.json"
CHECKPOINT = TRAIN / "grpo/checkpoints/step_000450/adapter/policy"
MODEL = PROJECT / "mechanism/models/Qwen3-VL-8B-Instruct"
SCORE = re.compile(r"<score>(0\.[0-9]{2}|1\.00)</score>")
SECOND_SCORE = re.compile(r"^\s*(0\.[0-9]{2}|1\.00)</score>")
FREE_SECOND = re.compile(
    r"<answer>(\[[^\]]+\])</answer>\s*<score>(0\.[0-9]{2}|1\.00)</score>")


def inside_project(path):
    resolved = Path(path).resolve()
    try:
        resolved.relative_to(PROJECT)
    except ValueError as exc:
        raise ValueError("input resolves outside registered project root")
    return resolved


def map_image(path):
    if path.startswith(LEGACY_PREFIX):
        path = str(PROJECT / path[len(LEGACY_PREFIX):])
    alias = Path(path)
    resolved = alias.resolve()
    try:
        resolved.relative_to(PROJECT)
    except ValueError:
        try:
            resolved.relative_to(ALLOWED_GOT10K)
            alias.relative_to(PROJECT / "mechanism/dataset/GOT10k")
        except ValueError as exc:
            raise ValueError("image resolves outside approved GOT10k or project roots") from exc
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    return str(resolved)


def select_cases():
    records = []
    for path in sorted((TRAIN / "grpo").glob("rollouts-rank*.jsonl")):
        inside_project(path)
        for line in path.open():
            if not line.strip():
                continue
            row = json.loads(line)
            reward = row.get("reward")
            if not isinstance(reward, dict) or row.get("target_present") is not True:
                continue
            scores, ious = reward.get("scores"), reward.get("candidate_ious")
            if (reward.get("valid") is not True or reward.get("candidate_count") != 3
                    or not isinstance(scores, list) or not isinstance(ious, list)
                    or len(scores) != 3 or len(ious) != 3
                    or not all(isinstance(v, (int, float)) and not isinstance(v, bool)
                               and math.isfinite(v) for v in scores + ious)
                    or ious.count(max(ious)) != 1):
                continue
            if (row.get("step", -1) < 400 or ious.index(max(ious)) != 1
                    or reward.get("selected_index") != 0 or scores[0] <= scores[1]
                    or scores[0] < 0.5 or scores[1] <= max(scores[2], 0.01)
                    or ious[1] < 0.5 or ious[1] - ious[0] < 0.1):
                continue
            text = row.get("text")
            if not isinstance(text, str) or len(SCORE.findall(text)) != 3:
                continue
            records.append(row)
    records.sort(key=lambda x: (x["step"], x["sample_id"], x["text"]))
    selected = []
    used = set()
    for row in records:
        if row["sample_id"] not in used:
            selected.append(row)
            used.add(row["sample_id"])
        if len(selected) == 6:
            break
    if len(selected) < 6:
        raise RuntimeError("fewer than six eligible distinct samples")
    return selected


def prefixes(text):
    matches = list(SCORE.finditer(text))
    if len(matches) != 3:
        raise ValueError("not exactly three scores")
    marker = matches[1].start()
    end = marker + len("<score>")
    original = text[:end]
    first = SCORE.search(original)
    if first is None:
        raise ValueError("first score missing from prefix")
    return {
        "original": original,
        "low_001": original[:first.start(1)] + "0.01" + original[first.end(1):],
        "high_099": original[:first.start(1)] + "0.99" + original[first.end(1):],
    }


def first_score_prefixes(text):
    match = SCORE.search(text)
    if match is None:
        raise ValueError("first score is missing")
    next_answer = text.find("<answer>", match.end())
    if next_answer < 0 or text[match.end():next_answer].strip():
        raise ValueError("unexpected text between first and second candidate")
    original = text[:next_answer]
    return {
        "original": original,
        "low_001": original[:match.start(1)] + "0.01" + original[match.end(1):],
        "high_099": original[:match.start(1)] + "0.99" + original[match.end(1):],
    }


def prepare_base_input(row, processor, device):
    from iploc_szy.rl.data import prepare_prompt

    mapped = dict(row)
    mapped["reference_image"] = map_image(row["reference_image"])
    mapped["query_image"] = map_image(row["query_image"])
    inputs, _ = prepare_prompt(mapped, processor, device, 262144,
                               protocol="focus_multi3_instances_v1")
    return inputs


def build_input(base, prefix, processor):
    import torch

    token_ids = processor.tokenizer(prefix, add_special_tokens=False)["input_ids"]
    if processor.tokenizer.decode(token_ids, skip_special_tokens=False) != prefix:
        raise ValueError("forced prefix does not round-trip through tokenizer")
    added = torch.tensor([token_ids], dtype=base.input_ids.dtype,
                         device=base.input_ids.device)
    out = dict(base)
    out["input_ids"] = torch.cat((base.input_ids, added), dim=1)
    out["attention_mask"] = torch.cat((base.attention_mask,
                                       torch.ones_like(added)), dim=1)
    return out


def main(free_second=False):
    import torch
    from iploc_szy.compat import ensure_torchvision_nms_schema
    ensure_torchvision_nms_schema()
    from peft import PeftModel
    from transformers import AutoProcessor, BitsAndBytesConfig, Qwen3VLForConditionalGeneration
    if free_second:
        from transformers import StoppingCriteria, StoppingCriteriaList
        from iploc_szy.rl.data import normalize_box
        from iploc_szy.rl.rewards import iou, validate_box
        from PIL import Image

    for path in (TRAIN, MANIFEST, CHECKPOINT, MODEL):
        inside_project(path)
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required")
    cases = select_cases()
    by_id = {row["id"]: row for row in json.loads(MANIFEST.read_text())}
    if any(row["sample_id"] not in by_id for row in cases):
        raise RuntimeError("selected rollout sample missing from E-013 manifest")

    processor = AutoProcessor.from_pretrained(str(MODEL), local_files_only=True)
    quantization = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                      bnb_4bit_use_double_quant=True,
                                      bnb_4bit_compute_dtype=torch.bfloat16)
    base_model = Qwen3VLForConditionalGeneration.from_pretrained(
        str(MODEL), dtype=torch.bfloat16, device_map={"": 0},
        attn_implementation="sdpa", quantization_config=quantization,
        local_files_only=True)
    model = PeftModel.from_pretrained(base_model, str(CHECKPOINT), is_trainable=False,
                                     local_files_only=True)
    model.eval()
    device = model.get_input_embeddings().weight.device
    results = []
    for case in cases:
        sample = by_id[case["sample_id"]]
        base_inputs = prepare_base_input(sample, processor, device)
        if free_second:
            with Image.open(map_image(sample["query_image"])) as image:
                gt = normalize_box(sample["gt_box"], image.size)
        conditions = {}
        variants = first_score_prefixes(case["text"]) if free_second else prefixes(case["text"])
        for name, prefix in variants.items():
            inputs = build_input(base_inputs, prefix, processor)
            if free_second:
                start = inputs["input_ids"].shape[1]

                class StopAfterSecondScore(StoppingCriteria):
                    def __call__(self, input_ids, scores, **kwargs):
                        tail = processor.batch_decode(
                            input_ids[:, start:], skip_special_tokens=True)[0]
                        return "</score>" in tail

                extra = {"stopping_criteria": StoppingCriteriaList([StopAfterSecondScore()])}
                max_tokens = 96
            else:
                extra = {}
                max_tokens = 16
            with torch.inference_mode():
                output = model.generate(**inputs, do_sample=False,
                                        max_new_tokens=max_tokens,
                                        pad_token_id=processor.tokenizer.eos_token_id,
                                        **extra)
            continuation = processor.batch_decode(
                output[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True)[0]
            if free_second:
                match = FREE_SECOND.search(continuation)
                second_box = None
                second_iou = None
                if match:
                    try:
                        second_box = json.loads(match.group(1))
                        validate_box(second_box, 1000)
                        second_iou = iou(second_box, gt)
                    except (ValueError, TypeError):
                        second_box = None
                conditions[name] = {
                    "second_box": second_box,
                    "second_score": float(match.group(2)) if match else None,
                    "second_iou": second_iou,
                    "continuation": continuation[:220],
                }
            else:
                match = SECOND_SCORE.match(continuation)
                conditions[name] = {
                    "second_score": float(match.group(1)) if match else None,
                    "continuation": continuation[:100],
                }
        results.append({
            "sample_id": case["sample_id"], "rollout_step": case["step"],
            "original_scores": case["reward"]["scores"],
            "candidate_ious": case["reward"]["candidate_ious"],
            "conditions": conditions,
        })
        print(f"case_complete={len(results)}", file=sys.stderr, flush=True)
    print(json.dumps({
        "contract": ("e013-first-score-free-second/v1" if free_second
                     else "e013-first-score-intervention/v1"),
        "model_checkpoint": str(CHECKPOINT),
        "design": ("Same images, prompt, first box; force first score to original/0.01/0.99, then greedily continue second box and score."
                   if free_second else
                   "Same images, prompt, first and second boxes; force first score to original/0.01/0.99, then greedily continue second score."),
        "cases": results,
    }, ensure_ascii=False))


if __name__ == "__main__":
    if sys.argv[1:] == ["--dry-select"]:
        print(json.dumps([{"sample_id": x["sample_id"], "step": x["step"],
                           "scores": x["reward"]["scores"],
                           "ious": x["reward"]["candidate_ious"]}
                          for x in select_cases()], ensure_ascii=False))
    elif sys.argv[1:] == ["--check-inputs"]:
        from PIL import Image
        by_id = {row["id"]: row for row in json.loads(MANIFEST.read_text())}
        for case in select_cases():
            sample = by_id[case["sample_id"]]
            for key in ("reference_image", "query_image"):
                with Image.open(map_image(sample[key])) as image:
                    image.verify()
        print(json.dumps({"checked_cases": 6, "checked_images": 12}))
    elif sys.argv[1:] == ["--debug-prefix"]:
        from iploc_szy.compat import ensure_torchvision_nms_schema
        ensure_torchvision_nms_schema()
        from transformers import AutoProcessor
        processor = AutoProcessor.from_pretrained(str(MODEL), local_files_only=True)
        case = select_cases()[0]
        by_id = {row["id"]: row for row in json.loads(MANIFEST.read_text())}
        base = prepare_base_input(by_id[case["sample_id"]], processor, "cpu")
        variants = [build_input(base, prefix, processor)
                    for prefix in prefixes(case["text"]).values()]
        if not all(variant["image_grid_thw"] is base["image_grid_thw"]
                   and variant["pixel_values"] is base["pixel_values"]
                   for variant in variants):
            raise ValueError("image tensors changed across conditions")
        print(json.dumps({"prefix_check": "passed", "base_tokens": base.input_ids.shape[1],
                          "forced_tokens": [v["input_ids"].shape[1] for v in variants]}))
    elif sys.argv[1:] == ["--free-second"]:
        main(free_second=True)
    else:
        main()
