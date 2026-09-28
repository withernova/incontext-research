"""E-012 整头置零：自由生成、配对定位指标与独立 teacher-forced CE。

可显式读取 source_run_dir 的 R-001 冻结输入与 summary，绝不扫描“最新”结果。
--validate-only 只检查冻结输入，不加载模型，也不创建结果目录。
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
import hashlib
import json
import math
from pathlib import Path
import random
import re
import runpy

SCHEMA = "iploc-szy.top10-head-ablation/v1"
NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"
BOX = re.compile(r"(?:\[|\()\s*(" + NUMBER + r")\s*,\s*(" + NUMBER
                 + r")\s*,\s*(" + NUMBER + r")\s*,\s*(" + NUMBER + r")\s*(?:\]|\))")
HEAD_LABEL = re.compile(r"L(\d+)H(\d+)")


def write_json(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    tmp.replace(path)


def checked_file(path, digest):
    if not path or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("explicit file path and SHA256 are required")
    content = Path(path).read_bytes()
    if hashlib.sha256(content).hexdigest() != digest:
        raise ValueError(f"SHA256 mismatch: {path}")
    return content


def heads_checked(values, layers, width, expected=None):
    if not isinstance(values, (list, tuple)) or not values:
        raise ValueError("explicit non-empty head list required")
    heads = []
    for pair in values:
        if (not isinstance(pair, (list, tuple)) or len(pair) != 2
                or any(type(v) is not int for v in pair)):
            raise ValueError("heads must be integer [layer, head] pairs, zero-based")
        layer, head = pair
        if not 0 <= layer < layers or not 0 <= head < width:
            raise ValueError("head index outside model dimensions")
        heads.append((layer, head))
    if len(set(heads)) != len(heads) or (expected is not None and len(heads) != expected):
        raise ValueError("head count/uniqueness mismatch")
    return heads


def parse_head_labels(values, layers, width):
    if not isinstance(values, (list, tuple)) or not values:
        raise ValueError("legacy head source must provide a non-empty label list")
    pairs = []
    for value in values:
        match = HEAD_LABEL.fullmatch(str(value))
        if match is None:
            raise ValueError("legacy heads must use exact LxxHyy labels")
        pairs.append([int(match.group(1)), int(match.group(2))])
    return heads_checked(pairs, layers, width)


def conditions(heads, width, seeds):
    """同层等数量随机抽样，排除全部 candidate heads；每个 seed 独立。"""
    result = [dict(name="baseline", heads=[]), dict(name="top10_joint", heads=heads)]
    result += [dict(name=f"single_L{l:02d}H{h:02d}", heads=[(l, h)]) for l, h in heads]
    forbidden = set(heads)
    for seed in seeds:
        rng, selected = random.Random(seed), []
        for layer, count in sorted(Counter(l for l, _ in heads).items()):
            pool = [h for h in range(width) if (layer, h) not in forbidden]
            if len(pool) < count:
                raise ValueError("insufficient same-layer noncandidate control heads")
            selected.extend((layer, h) for h in sorted(rng.sample(pool, count)))
        result.append(dict(name=f"random_seed_{seed}", heads=selected, seed=seed))
    return result


def joint_set_conditions(named_sets, width, seeds, random_heads):
    """Only joint conditions, plus same-layer matched controls for the largest tested set."""
    result = [dict(name="baseline", heads=[])]
    seen_names = set()
    for name, heads in named_sets:
        if not isinstance(name, str) or not name or name in seen_names:
            raise ValueError("joint condition names must be non-empty and unique")
        seen_names.add(name)
        result.append(dict(name=name, heads=list(heads)))
    controls = conditions(random_heads, width, seeds)
    result.extend(item for item in controls if item["name"].startswith("random_seed_"))
    return result


def valid_box(box, scale):
    return (isinstance(box, (list, tuple)) and len(box) == 4
            and all(type(v) in (float, int) and math.isfinite(v) and 0 <= v <= scale for v in box)
            and box[2] > box[0] and box[3] > box[1])


def parse_generated_box(text, scale):
    matches = list(BOX.finditer(text))
    if len(matches) != 1:
        return None
    match = matches[0]
    if (match.group()[0], match.group()[-1]) not in {("[", "]"), ("(", ")")}:
        return None
    box = [float(v) for v in match.groups()]
    return box if valid_box(box, scale) else None


def iou(a, b):
    area = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - area
    return area / union


def paired_metrics(base, current, target, scale):
    clean, box = base["box"], current["box"]
    clean_iou = iou(clean, target) if clean is not None else 0.0
    actual_iou = iou(box, target) if box is not None else 0.0
    both = clean is not None and box is not None
    return dict(iou=actual_iou, delta_iou=actual_iou - clean_iou,
                invalid_output=box is None, box_changed=box != clean,
                text_changed=current["text"] != base["text"],
                coordinate_mae_normalized=(sum(abs(a - b) for a, b in zip(clean, box)) / (4 * scale)
                                           if both else None),
                bbox_token_ce=current["bbox_token_ce"],
                delta_bbox_token_ce=current["bbox_token_ce"] - base["bbox_token_ce"])


def validate_common(spec):
    if Path(spec["output_dir"]).exists():
        raise ValueError("output directory already exists; refusing overwrite")
    for key in ("num_layers", "num_heads", "max_new_tokens", "max_sequence_tokens", "coordinate_scale"):
        if type(spec.get(key)) is not int or spec[key] <= 0:
            raise ValueError(f"positive integer required: {key}")
    seeds = spec.get("random_seeds")
    if (not isinstance(seeds, list) or len(seeds) < 3 or any(type(s) is not int or s < 0 for s in seeds)
            or len(set(seeds)) != len(seeds)):
        raise ValueError("at least three distinct non-negative random seeds required")
    for key in ("parity_atol", "parity_rtol"):
        value = spec.get(key)
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError(f"invalid parity tolerance: {key}")


def validated_ranking(ranking, layers, heads):
    if ranking.get("schema") != "iploc-szy.bbox-gradient-ranking/v1" or ranking.get("status") != "completed":
        raise ValueError("unexpected ranking schema/status")
    rows = ranking["ranking"]
    if len(rows) != layers * heads:
        raise ValueError("ranking must cover every model head")
    heads_checked([[r["layer"], r["head"]] for r in rows], layers, heads)
    if any(type(r["absolute"]) not in (int, float) or not math.isfinite(r["absolute"])
           or r["absolute"] < 0 for r in rows):
        raise ValueError("invalid absolute contribution")
    ordered = sorted(rows, key=lambda r: (-r["absolute"], r["layer"], r["head"]))
    if rows != ordered or [r.get("rank") for r in rows] != list(range(1, len(rows) + 1)):
        raise ValueError("ranking order/rank mismatch")
    return rows


def validate_source_run(spec):
    required = ["source_run_dir", "output_dir"]
    missing = [key for key in required if not spec.get(key)]
    if missing:
        raise ValueError("unresolved source-run inputs: " + ", ".join(missing))
    validate_common(spec)
    if spec.get("source_run_id") != "E-012/R-001" or spec.get("ranking_metric") != "bbox_grad_abs_contrib_mean":
        raise ValueError("this proposal requires explicit E-012/R-001 absolute-contribution ranking")
    source = Path(spec["source_run_dir"]).resolve()
    frozen_path, summary_path = source / "frozen_input.json", source / "summary.json"
    if not frozen_path.is_file() or not summary_path.is_file():
        raise ValueError("source run must contain frozen_input.json and summary.json")
    frozen_bytes = frozen_path.read_bytes()
    summary_bytes = summary_path.read_bytes()
    frozen, ranking = json.loads(frozen_bytes), json.loads(summary_bytes)
    rows = validated_ranking(ranking, spec["num_layers"], spec["num_heads"])
    config = frozen.get("config")
    if not isinstance(config, dict) or Path(config.get("work_dir", "")).resolve() != source:
        raise ValueError("R-001 frozen configuration does not identify the supplied source directory")
    if config.get("model", {}).get("attn_implementation") != "eager" or not config.get("checkpoint_path"):
        raise ValueError("R-001 source lacks explicit eager model or LoRA checkpoint")
    dataloader = config.get("screen_dataloader", {})
    if dataloader.get("dataset", {}).get("normalized_scale") != spec["coordinate_scale"]:
        raise ValueError("R-001 coordinate scale differs from ablation configuration")
    if dataloader.get("collator", {}).get("assistant_only") is not True:
        raise ValueError("R-001 source lacks assistant-only supervision")
    manifest = Path(dataloader.get("dataset", {}).get("ann_file", ""))
    expected_manifest_hash = frozen.get("manifests_sha256", {}).get(str(manifest))
    manifest_bytes = checked_file(manifest, expected_manifest_hash)
    indices = frozen.get("selected_indices")
    if (not isinstance(indices, list) or not indices or any(type(i) is not int or i < 0 for i in indices)
            or len(set(indices)) != len(indices)):
        raise ValueError("R-001 selected_indices must be unique non-negative integers")
    counts = spec.get("samples_per_dataset")
    if (not isinstance(counts, dict) or not counts
            or any(not isinstance(name, str) or type(value) is not int or value < 1 for name, value in counts.items())):
        raise ValueError("samples_per_dataset must map dataset names to positive integers")
    snapshots = {"r001_frozen_input_snapshot.json": frozen_bytes,
                 "r001_summary_snapshot.json": summary_bytes,
                 "r001_manifest_sha256.txt": (hashlib.sha256(manifest_bytes).hexdigest() + "\n").encode(),
                 "resolved_r001_config.json": json.dumps(config, ensure_ascii=False, indent=2).encode()}
    legacy = spec.get("legacy_head_source")
    if legacy is None:
        candidates = [(row["layer"], row["head"]) for row in rows[:10]]
        selection = dict(kind="r001_absolute_top10", ranking_metric=spec["ranking_metric"],
                         heads=[f"L{layer:02d}H{head:02d}" for layer, head in candidates])
    else:
        if set(legacy) != {"config_path", "config_sha256", "field"}:
            raise ValueError("legacy_head_source requires config_path, config_sha256 and field only")
        if legacy["field"] not in {"teacher_heads", "student_heads"}:
            raise ValueError("legacy head source field must be teacher_heads or student_heads")
        legacy_bytes = checked_file(legacy["config_path"], legacy["config_sha256"])
        legacy_config = runpy.run_path(legacy["config_path"])
        try:
            labels = legacy_config["runtime"]["runner"]["auxiliary_loss"][legacy["field"]]
        except (KeyError, TypeError) as error:
            raise ValueError("legacy head source lacks runtime.runner.auxiliary_loss field") from error
        candidates = parse_head_labels(labels, spec["num_layers"], spec["num_heads"])
        selection = dict(kind="legacy_e009_fixed_heads", field=legacy["field"],
                         config_path=str(legacy["config_path"]), config_sha256=legacy["config_sha256"],
                         heads=[f"L{layer:02d}H{head:02d}" for layer, head in candidates])
        snapshots["legacy_e009_head_config.py"] = legacy_bytes
    if spec.get("combine_r001_top10_with_legacy"):
        if legacy is None:
            raise ValueError("combined union requires legacy_head_source")
        r001_top10 = [(row["layer"], row["head"]) for row in rows[:10]]
        union = tuple(dict.fromkeys(r001_top10 + list(candidates)))
        if len(union) != len(r001_top10) + len(candidates):
            raise ValueError("R-001 Top-10 and legacy set overlap; union-size assumption failed")
        conditions_out = joint_set_conditions(
            [("r001_top10_joint", r001_top10),
             ("e009_fixed5_joint", candidates),
             ("new_old_union15_joint", union)],
            spec["num_heads"], spec["random_seeds"], union,
        )
        selection = dict(kind="r001_top10_plus_legacy_e009_fixed5", r001_top10=[f"L{l:02d}H{h:02d}" for l, h in r001_top10],
                         legacy_fixed5=[f"L{l:02d}H{h:02d}" for l, h in candidates],
                         union15=[f"L{l:02d}H{h:02d}" for l, h in union], legacy_source=selection)
    else:
        conditions_out = conditions(candidates, spec["num_heads"], spec["random_seeds"])
    source_plan = dict(directory=str(source), frozen_input_sha256=hashlib.sha256(frozen_bytes).hexdigest(),
                       summary_sha256=hashlib.sha256(summary_bytes).hexdigest(),
                       manifest=str(manifest), manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
                       selected_indices=indices, samples_per_dataset=counts, config=config,
                       ranking_top10=[dict(rank=row["rank"], layer=row["layer"], head=row["head"],
                                           absolute=row["absolute"]) for row in rows[:10]],
                       candidate_selection=selection)
    plan = dict(schema=SCHEMA, spec=spec, source=source_plan,
                conditions=conditions_out,
                sample_count=sum(counts.values()))
    return plan, snapshots


def select_source_indices(dataset, allowed, counts):
    from .head_circuit import dataset_name
    observed, selected = {name: 0 for name in counts}, []
    for index in sorted(allowed):
        name = dataset_name(dataset, index)
        if name in observed and observed[name] < counts[name]:
            selected.append(index)
            observed[name] += 1
    if observed != counts:
        raise ValueError(f"R-001 frozen indices cannot meet dataset quotas: {observed} != {counts}")
    return selected, observed


def validate_spec(spec):
    if spec.get("source_run_dir"):
        return validate_source_run(spec)
    required = ["runtime_config", "runtime_config_sha256", "input_manifest_sha256", "ranking_path",
                "ranking_sha256", "samples_path", "samples_sha256", "output_dir", "heads"]
    missing = [k for k in required if not spec.get(k)]
    if missing:
        raise ValueError("unresolved run inputs: " + ", ".join(missing))
    if not isinstance(spec["input_manifest_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", spec["input_manifest_sha256"]):
        raise ValueError("explicit input manifest SHA256 required")
    if spec.get("source_run_id") != "E-012/R-001" or spec.get("ranking_metric") != "bbox_grad_abs_contrib_mean":
        raise ValueError("this proposal requires explicit E-012/R-001 absolute-contribution ranking")
    validate_common(spec)
    heads = heads_checked(spec["heads"], spec["num_layers"], spec["num_heads"], expected=10)
    ranking_bytes = checked_file(spec["ranking_path"], spec["ranking_sha256"])
    ranking = json.loads(ranking_bytes)
    rows = validated_ranking(ranking, spec["num_layers"], spec["num_heads"])
    if heads != [(r["layer"], r["head"]) for r in rows[:10]]:
        raise ValueError("explicit heads differ from frozen ranking Top-10")
    runtime_bytes = checked_file(spec["runtime_config"], spec["runtime_config_sha256"])
    sample_bytes = checked_file(spec["samples_path"], spec["samples_sha256"])
    frozen = json.loads(sample_bytes)
    if (frozen.get("schema") != "iploc-szy.head-ablation-samples/v1"
            or frozen.get("coordinate_scale") != spec["coordinate_scale"]
            or frozen.get("target_box_source") != "annotation"):
        raise ValueError("samples require annotation GT and explicit matching coordinate scale")
    samples = frozen["samples"]
    seen, identities = set(), set()
    if not samples:
        raise ValueError("empty evaluation set")
    for s in samples:
        index = s["dataset_index"]
        if type(index) is not int or index < 0 or index in seen:
            raise ValueError("sample indices must be unique non-negative integers")
        if not s.get("dataset") or not s.get("sample_id") or not valid_box(s.get("target_box"), spec["coordinate_scale"]):
            raise ValueError("sample identity or annotation box missing/invalid")
        identity = (s["dataset"], str(s["sample_id"]))
        if identity in identities:
            raise ValueError("duplicate sample identity")
        identities.add(identity)
        seen.add(index)
    return dict(schema=SCHEMA, spec=spec, conditions=conditions(heads, spec["num_heads"], spec["random_seeds"]), samples=samples), {
        "ranking_snapshot.json": ranking_bytes, "samples_snapshot.json": sample_bytes,
        "runtime_config_snapshot.py": runtime_bytes,
    }


class WholeHeadZeroHook:
    """覆盖所选文本 query head 的全部 rows/keys；保留非目标 head 的原始输出。"""

    def __init__(self, heads):
        self.heads = set(map(tuple, heads))
        self.audits = {}
        self.layer_calls = Counter()

    @contextmanager
    def installed(self, model):
        import torch
        from transformers.models.qwen3_vl import modeling_qwen3_vl as implementation

        modules = [m for m in model.modules() if m.__class__.__name__ == "Qwen3VLTextAttention"]
        layers = {int(m.layer_idx) for m in modules}
        if model.training or not modules or not {l for l, _ in self.heads} <= layers:
            raise ValueError("hook requires eval Qwen3-VL text attention with all selected layers")
        # 配置必须已是 eager；不在这里改变 baseline 的数值路径。
        if any(m.config._attn_implementation != "eager" for m in modules):
            raise ValueError("all text attention modules must use eager")
        original = implementation.eager_attention_forward

        def intercepted(module, query, key, value, attention_mask, scaling, dropout=0.0, **kwargs):
            output, attention = original(module, query, key, value, attention_mask, scaling, dropout, **kwargs)
            if module.__class__.__name__ != "Qwen3VLTextAttention":
                return output, attention
            if query.shape[0] != 1 or dropout != 0:
                raise ValueError("whole-head ablation requires batch=1 and dropout=0")
            layer = int(module.layer_idx)
            self.layer_calls[layer] += 1
            selected = sorted(h for l, h in self.heads if l == layer)
            if not selected:
                return output, attention
            if min(selected) < 0 or max(selected) >= attention.shape[1]:
                raise ValueError("selected query head outside attention tensor")
            attention, output = attention.clone(), output.clone()
            values = implementation.repeat_kv(value, module.num_key_value_groups)
            for head in selected:
                before = attention[:, head].float()
                if not bool(torch.isfinite(before).all()):
                    raise ValueError("non-finite original attention")
                mass = float(before.sum(-1).mean())
                attention[:, head, :, :] = 0
                av = torch.matmul(attention[:, head], values[:, head])
                if not bool(torch.isfinite(av).all()) or bool(torch.count_nonzero(av)):
                    raise ValueError("selected A@V did not become finite exact zero")
                output[:, :, head, :] = av
                label = f"L{layer:02d}H{head:02d}"
                audit = self.audits.setdefault(label, dict(calls=0, prefill_calls=0, decode_calls=0,
                                                          removed_mass_mean_sum=0.0, max_abs_av=0.0,
                                                          intervened_attention_entries=0))
                audit["calls"] += 1
                audit["prefill_calls" if query.shape[-2] > 1 else "decode_calls"] += 1
                audit["intervened_attention_entries"] += attention.shape[-2] * attention.shape[-1]
                if query.shape[-2] > 1:
                    audit["prefill_query_tokens"] = attention.shape[-2]
                    audit["prefill_key_tokens"] = attention.shape[-1]
                audit["removed_mass_mean_sum"] += mass
            return output, attention

        implementation.eager_attention_forward = intercepted
        try:
            yield self
        finally:
            implementation.eager_attention_forward = original

    def validate(self, expected_calls, num_layers):
        if set(self.layer_calls) != set(range(num_layers)) or any(n != expected_calls for n in self.layer_calls.values()):
            raise ValueError("attention interception did not cover every forward/layer")
        for layer, head in self.heads:
            audit = self.audits.get(f"L{layer:02d}H{head:02d}", {})
            if audit.get("calls") != expected_calls or audit.get("prefill_calls") != 1:
                raise ValueError("selected head missing prefill/decode intervention")


def generation_prefix(encoded, labels, tokenizer, spans):
    """从第一个受监督回答 token 之前截断，禁止 teacher-forcing 答案泄漏。"""
    import torch
    ids = encoded["input_ids"]
    if ids.shape[0] != 1 or labels.shape != ids.shape:
        raise ValueError("batch/label shape mismatch")
    positions = torch.nonzero(labels[0] != -100, as_tuple=False).flatten()
    if not len(positions):
        raise ValueError("no supervised assistant response")
    start = int(positions[0])
    if not spans or start <= max(s[1] for s in spans):
        raise ValueError("assistant response must follow both complete images")
    prefix_text = tokenizer.decode(ids[0, :start].tolist(), skip_special_tokens=False)
    if not prefix_text.endswith("<|im_start|>assistant\n"):
        raise ValueError("unsupported assistant boundary; cannot guarantee GT-free generation")
    # Qwen3-VL generation 自行计算 position_ids/rope/cache；未知键拒绝，避免漏截断。
    allowed = {"input_ids", "attention_mask", "pixel_values", "image_grid_thw", "token_type_ids"}
    if set(encoded) - allowed:
        raise ValueError(f"unsupported generation input keys: {sorted(set(encoded) - allowed)}")
    result = {}
    for key, tensor in encoded.items():
        result[key] = tensor[:, :start].clone() if key in {"input_ids", "attention_mask", "token_type_ids"} else tensor
    if "attention_mask" not in result or not bool((result["attention_mask"] == 1).all()):
        raise ValueError("generation requires one unpadded prompt")
    return result, start


def summarize(records, condition_names):
    output = {}
    datasets = sorted({r["dataset"] for r in records})
    for name in condition_names:
        output[name] = {}
        for group in ["all"] + datasets:
            rows = [r["metrics"] for r in records if r["condition"] == name and (group == "all" or r["dataset"] == group)]
            if not rows:
                raise ValueError("incomplete condition/dataset matrix")
            entry = dict(samples=len(rows))
            for key in rows[0]:
                values = [r[key] for r in rows if r[key] is not None]
                entry[key + "_mean"] = sum(values) / len(values) if values else None
                entry[key + "_count"] = len(values)
            output[name][group] = entry
    return output


def execute(plan, snapshots):
    import torch
    from .head_circuit import build_context, dataset_name
    from .bbox_gradient import bbox_loss
    from ..prompting.coordinates import parse_box

    spec = plan["spec"]
    # 模型加载前校验数据和配置，冻结内容变更一律拒绝。
    source = plan.get("source")
    if source is None:
        from ..config import Config
        checked_file(spec["runtime_config"], spec["runtime_config_sha256"])
        cfg = Config.fromfile(spec["runtime_config"])
        checked_file(cfg["screen_dataloader"]["dataset"]["ann_file"], spec["input_manifest_sha256"])
        frozen_samples = plan["samples"]
    else:
        cfg = source["config"]
        checked_file(source["manifest"], source["manifest_sha256"])
        frozen_samples = None
    if cfg["model"].get("attn_implementation") != "eager" or not cfg.get("checkpoint_path"):
        raise ValueError("explicit eager model plus fixed LoRA checkpoint required")
    if cfg["screen_dataloader"]["dataset"].get("normalized_scale") != spec["coordinate_scale"]:
        raise ValueError("dataset coordinate scale differs from frozen GT")
    if cfg["screen_dataloader"]["collator"].get("assistant_only") is not True:
        raise ValueError("assistant-only supervision required to derive prompt boundary")
    root = Path(spec["output_dir"])
    root.mkdir(parents=True, exist_ok=False)
    write_json(root / "resolved_plan.json", plan)
    for name, content in snapshots.items():
        (root / name).write_bytes(content)
    try:
        dataset, probe, checkpoint, wrapper, runner = build_context(cfg)
        model, tokenizer = wrapper.model.eval(), wrapper.processor.tokenizer
        model.requires_grad_(False)
        text_cfg = getattr(model.config, "text_config", model.config)
        if (text_cfg.num_hidden_layers, text_cfg.num_attention_heads) != (spec["num_layers"], spec["num_heads"]):
            raise ValueError("runtime model dimensions differ from frozen plan")
        write_json(root / "checkpoint.json", checkpoint)
        if source is not None:
            indices, observed = select_source_indices(dataset, source["selected_indices"],
                                                      source["samples_per_dataset"])
            frozen_samples = []
            for index in indices:
                sample = dataset[index]
                target_box = parse_box(sample.get("query_answer"))
                if not valid_box(target_box, spec["coordinate_scale"]):
                    raise ValueError("dataset query annotation cannot produce a valid normalized target box")
                frozen_samples.append(dict(dataset_index=index, dataset=dataset_name(dataset, index),
                                           sample_id=str(sample.get("sample_id", sample.get("id"))),
                                           target_box=target_box,
                                           target_box_source="dataset_query_answer_derived_from_annotation"))
            write_json(root / "selected_samples.json", dict(
                schema="iploc-szy.head-ablation-samples/v1",
                source_run="E-012/R-001", selected_indices=indices,
                samples_per_dataset=observed, coordinate_scale=spec["coordinate_scale"],
                target_box_source="dataset_query_answer_derived_from_annotation",
                samples=frozen_samples))
        records = []
        for order, frozen in enumerate(frozen_samples):
            index = frozen["dataset_index"]
            sample, encoded, metadata, positions, _, spans = probe.encode_sample(runner, index)
            sample_id = str(sample.get("sample_id", sample.get("id")))
            if sample_id != str(frozen["sample_id"]) or dataset_name(dataset, index) != frozen["dataset"]:
                raise ValueError("dataset sample identity differs from frozen manifest")
            # 现有 probe 消费 labels；重新 collate 并逐元素核验，以保留回答起点。
            labeled = runner.collator([sample])
            if not torch.equal(labeled["input_ids"], encoded["input_ids"]):
                raise ValueError("collator is not deterministic")
            prefix, prompt_length = generation_prefix(encoded, labeled["labels"], tokenizer, spans)
            if encoded["input_ids"].shape[1] > spec["max_sequence_tokens"] or prompt_length + spec["max_new_tokens"] > spec["max_sequence_tokens"]:
                raise ValueError("sequence exceeds frozen budget; no silent truncation")
            forward = {k: v.to(wrapper.input_device) for k, v in encoded.items()}
            forward.update(use_cache=False, output_attentions=False, return_dict=True, logits_to_keep=0)
            prefix = {k: v.to(wrapper.input_device) for k, v in prefix.items()}
            # GenerationConfig 独立构造，禁用模型残留的 beam/sampling/penalty 设置。
            from transformers import GenerationConfig
            generation = GenerationConfig(
                do_sample=False, num_beams=1, max_new_tokens=spec["max_new_tokens"], use_cache=True,
                eos_token_id=model.generation_config.eos_token_id,
                pad_token_id=model.generation_config.pad_token_id,
                bos_token_id=model.generation_config.bos_token_id,
            )
            def run(heads, no_hook=False):
                ce_hook, gen_hook = WholeHeadZeroHook(heads), WholeHeadZeroHook(heads)
                with torch.inference_mode():
                    if no_hook:
                        out = model(**forward)
                    else:
                        with ce_hook.installed(model):
                            out = model(**forward)
                        ce_hook.validate(1, spec["num_layers"])
                    ce = float(bbox_loss(out.logits, forward["input_ids"], positions))
                    logits = out.logits[0, [p - 1 for p in positions]].float().cpu().clone()
                    del out
                    if not math.isfinite(ce):
                        raise ValueError("non-finite bbox CE")
                    if no_hook:
                        generated = model.generate(**prefix, generation_config=generation)
                    else:
                        with gen_hook.installed(model):
                            generated = model.generate(**prefix, generation_config=generation)
                    if not torch.equal(generated[:, :prompt_length], prefix["input_ids"]):
                        raise ValueError("generate returned unexpected prompt prefix")
                    tokens = generated[0, prompt_length:].tolist()
                    if not tokens:
                        raise ValueError("generate returned no response")
                    if not no_hook:
                        gen_hook.validate(len(tokens), spec["num_layers"])
                    text = tokenizer.decode(tokens, skip_special_tokens=True)
                eos = generation.eos_token_id
                eos = [eos] if isinstance(eos, int) else (eos or [])
                truncated = len(tokens) >= spec["max_new_tokens"] and tokens[-1] not in eos
                return dict(text=text, box=None if truncated else parse_generated_box(text, spec["coordinate_scale"]),
                            bbox_token_ce=ce, generated_tokens=tokens, truncated=truncated,
                            ce_attention_audit=ce_hook.audits, generation_attention_audit=gen_hook.audits), logits

            baseline, base_logits = run([], no_hook=True)
            # 空 hook 只验证同一 teacher-forced forward 的数值透明性。再次调用
            # generate 会创建独立的 KV cache / decoding 循环，不能用于精确 token parity。
            identity_hook = WholeHeadZeroHook([])
            with torch.inference_mode(), identity_hook.installed(model):
                identity_output = model(**forward)
            identity_hook.validate(1, spec["num_layers"])
            identity_logits = identity_output.logits[0, [p - 1 for p in positions]].float().cpu().clone()
            del identity_output
            torch.testing.assert_close(identity_logits, base_logits, atol=spec["parity_atol"], rtol=spec["parity_rtol"])
            for condition in plan["conditions"]:
                value = baseline if condition["name"] == "baseline" else run(condition["heads"])[0]
                record = dict(dataset_index=index, dataset=frozen["dataset"], sample_id=sample_id,
                              condition=condition["name"], heads=condition["heads"],
                              target_box=frozen["target_box"], prompt_tokens=prompt_length,
                              bbox_token_count=len(positions), image_token_counts=[s[1] - s[0] for s in spans],
                              image_grid_thw=[list(map(int, grid)) for grid in metadata["image_grid_thw"]],
                              empty_hook_teacher_forced_logit_parity_passed=True, output=value,
                              metrics=paired_metrics(baseline, value, frozen["target_box"], spec["coordinate_scale"]))
                records.append(record)
                write_json(root / "records.json", dict(schema=SCHEMA, status="in_progress", records=records))
            print(f"[TOP10_ABLATION] {order + 1}/{len(frozen_samples)}", flush=True)
        expected = len(plan["conditions"]) * len(frozen_samples)
        if len(records) != expected:
            raise ValueError("incomplete paired condition matrix")
        write_json(root / "summary.json", dict(schema=SCHEMA, status="completed", records=len(records),
                   invalid_output_iou_policy="zero_in_full_denominator", delta_direction="intervention_minus_baseline",
                   summary=summarize(records, [c["name"] for c in plan["conditions"]])))
        write_json(root / "records.json", dict(schema=SCHEMA, status="completed", records=records))
    except BaseException as error:
        write_json(root / "failure.json", dict(schema=SCHEMA, status="failed", exception=type(error).__name__, reason=str(error)))
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    spec = runpy.run_path(args.config)["run_spec"]
    plan, snapshots = validate_spec(spec)
    if args.validate_only:
        print(json.dumps(dict(schema=SCHEMA, status="input_contract_passed", samples=plan.get("sample_count", len(plan.get("samples", []))),
                              conditions=len(plan["conditions"]), model_runtime_checked=False), ensure_ascii=False))
        return 0
    execute(plan, snapshots)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
