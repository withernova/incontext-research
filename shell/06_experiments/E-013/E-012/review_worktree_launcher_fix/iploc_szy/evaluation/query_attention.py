"""Qwen3-VL query-head intervention during native autoregressive generation.

Only selected probabilities are recomputed, after native Q/K normalization,
RoPE and KV-cache update. Other heads/rows use the original attention backend.
The selected probabilities are changed before their matrix product with V.
"""
from __future__ import annotations

import inspect
import math
import random
from types import FunctionType, MethodType

import torch

from ..attention_distillation.selected import parse_head, head_label
from ..head_screening.probes import consecutive_spans
from ..prompting.coordinates import parse_box
from .bbox import box_iou


def validate_settings(settings, allow_auto=False):
    heads = tuple(parse_head(h) for h in settings.get("heads", ()))
    raw_steps = settings.get("generation_steps", ())
    steps = "all" if raw_steps == "all" else tuple(raw_steps)
    automatic = settings.get("auto_head_screening") or {}
    auto_enabled = bool(allow_auto and automatic.get("enabled") and not heads)
    if auto_enabled:
        top_k = automatic.get("top_k", 5)
        samples = automatic.get("samples")
        if type(top_k) is not int or top_k < 1:
            raise ValueError("auto_head_screening.top_k must be a positive integer")
        if samples not in (None, "None") and (type(samples) is not int or samples < 1):
            raise ValueError("auto_head_screening.samples must be positive or None")
    if (not heads and not auto_enabled) or len(set(heads)) != len(heads):
        raise ValueError("attention_intervention.heads must be fixed, nonempty and unique")
    if steps != "all" and (not steps or any(type(s) is not int or s < 0 for s in steps) or len(set(steps)) != len(steps)):
        raise ValueError("generation_steps must be fixed unique zero-based integers")
    if settings.get("normalization") != "overlap_area_preserve_query_mass":
        raise ValueError("normalization must be overlap_area_preserve_query_mass")
    for key in ("logits_atol", "logits_rtol"):
        value = float(settings.get(key, 0.0))
        if not math.isfinite(value) or value < 0:
            raise ValueError(key + " must be finite and nonnegative")
    return heads, steps


def query_geometry(inputs, processor, model, answer):
    """Validate final-image span; use actual post-merge grid and normalized GT."""
    ids = inputs["input_ids"]
    if ids.shape[0] != 1 or not bool(inputs["attention_mask"].eq(1).all()):
        raise ValueError("intervention requires batch=1 and no padding")
    spans = consecutive_spans(ids[0].tolist(), int(processor.tokenizer.convert_tokens_to_ids("<|image_pad|>")))
    grids = inputs["image_grid_thw"].tolist()
    if not spans or len(spans) != len(grids):
        raise ValueError("image spans do not match image_grid_thw")
    base = model.get_base_model() if hasattr(model, "get_base_model") else model
    merge = int(base.config.vision_config.spatial_merge_size)
    for (start, stop), (t, h, w) in zip(spans, grids):
        if t != 1 or h % merge or w % merge or stop - start != (h // merge) * (w // merge):
            raise ValueError("unsupported image grid/span mapping")
    start, stop = spans[-1]
    _, h, w = grids[-1]
    h, w = h // merge, w // merge
    box = parse_box(answer)
    if box is None or not all(math.isfinite(x) for x in box):
        raise ValueError("GT bbox must be finite")
    x1, y1, x2, y2 = box
    if not (0 <= x1 < x2 <= 1000 and 0 <= y1 < y2 <= 1000):
        raise ValueError("GT bbox must be positive-area xyxy in [0,1000]")
    xs = torch.arange(w, dtype=torch.float64) * (1000.0 / w)
    ys = torch.arange(h, dtype=torch.float64) * (1000.0 / h)
    dx = (torch.minimum(xs + 1000.0 / w, torch.tensor(x2)) - torch.maximum(xs, torch.tensor(x1))).clamp_min(0)
    dy = (torch.minimum(ys + 1000.0 / h, torch.tensor(y2)) - torch.maximum(ys, torch.tensor(y1))).clamp_min(0)
    areas = (dy[:, None] * dx[None, :]).flatten()
    if not bool(areas.sum() > 0):
        raise ValueError("GT selected-token-count is zero")
    return dict(query_span=[start, stop], token_grid=[h, w],
                selected_token_count=int((areas > 0).sum()),
                gt_distribution=(areas / areas.sum()).float().tolist(),
                gt_box=box, prompt_length=int(ids.shape[1]))


class QueryAttentionHook:
    """Instance-local backend interception; restores the exact original forward."""

    def __init__(self, model, heads, generation_steps, geometry, mode):
        if mode not in ("noop", "gt_align"):
            raise ValueError("unsupported intervention condition")
        self.model, self.mode, self.geometry = model, mode, geometry
        self.heads = tuple(parse_head(h) for h in heads)
        self.steps = None if generation_steps == "all" else set(generation_steps)
        self.records, self._originals = [], []

    def __enter__(self):
        modules = {int(m.layer_idx): m for m in self.model.modules()
                   if m.__class__.__name__ == "Qwen3VLTextAttention"}
        try:
            for layer, head in self.heads:
                if layer not in modules or head >= int(modules[layer].config.num_attention_heads):
                    raise ValueError("selected Qwen3-VL head is outside model bounds")
            for layer in sorted({layer for layer, _ in self.heads}):
                module = modules[layer]
                if module.training or float(module.attention_dropout) != 0:
                    raise ValueError("query intervention requires eval mode and zero dropout")
                original = module.forward
                fn = inspect.unwrap(original.__func__)
                namespace = dict(fn.__globals__)
                if not {"eager_attention_forward", "ALL_ATTENTION_FUNCTIONS"}.issubset(namespace):
                    raise RuntimeError("installed Qwen3-VL attention backend contract changed")
                impl = module.config._attn_implementation
                if impl not in ("eager", "sdpa"):
                    raise ValueError("query intervention supports eager or sdpa only")
                backend = namespace["eager_attention_forward"] if impl == "eager" else namespace["ALL_ATTENTION_FUNCTIONS"][impl]
                interface = self._interface(backend, layer)
                namespace["eager_attention_forward"] = interface
                namespace["ALL_ATTENTION_FUNCTIONS"] = {impl: interface}
                cloned = FunctionType(fn.__code__, namespace, fn.__name__, fn.__defaults__, fn.__closure__)
                cloned.__kwdefaults__ = fn.__kwdefaults__
                self._originals.append((module, "forward" in module.__dict__, module.__dict__.get("forward")))
                module.forward = MethodType(cloned, module)
        except BaseException:
            self.close()
            raise
        return self

    def _interface(self, backend, layer):
        def forward(module, query, key, value, attention_mask, scaling, dropout=0.0, **kwargs):
            output, weights = backend(module, query, key, value, attention_mask,
                                      scaling=scaling, dropout=dropout, **kwargs)
            qlen, klen = query.shape[-2], key.shape[-2]
            # The final query row predicts token step 0 at prefill, then step N
            # when the cache contains prompt_length + N keys.
            step = klen - self.geometry["prompt_length"]
            if step < 0 or (self.steps is not None and step not in self.steps):
                return output, weights
            if query.shape[0] != 1 or klen < qlen:
                raise ValueError("unsupported batch/cache geometry")
            row = qlen - 1
            start, stop = self.geometry["query_span"]
            if not (0 <= start < stop <= klen):
                raise ValueError("query image span is outside attention keys")
            output = output.clone()
            if weights is not None:
                weights = weights.clone()
            for l, head in self.heads:
                if l != layer:
                    continue
                kv_head = head // int(module.num_key_value_groups)
                scores = torch.matmul(query[0, head, row], key[0, kv_head].T) * scaling
                if attention_mask is not None:
                    if attention_mask.ndim != 4 or attention_mask.dtype == torch.bool:
                        raise ValueError("requires native additive attention mask")
                    mask_head = 0 if attention_mask.shape[1] == 1 else head
                    mask_row = 0 if attention_mask.shape[-2] == 1 else row
                    scores = scores + attention_mask[0, mask_head, mask_row, :klen]
                probs = torch.softmax(scores, dim=-1, dtype=torch.float32).to(query.dtype)
                target = torch.tensor(self.geometry["gt_distribution"], device=probs.device, dtype=probs.dtype)
                before = probs[start:stop].clone()
                mass = before.float().sum()
                if not bool(torch.isfinite(probs).all()) or not bool(mass > 0):
                    raise ValueError("nonfinite attention or zero query mass")
                changed = probs.clone()
                if self.mode == "gt_align":
                    changed[start:stop] = (target.float() * mass).to(probs.dtype)
                original_head_output = torch.matmul(probs, value[0, kv_head])
                modified_head_output = torch.matmul(changed, value[0, kv_head])
                native_error = (original_head_output.float() - output[0, row, head].float()).abs().max()
                # Apply the AV difference to the native backend output. No-op
                # has an exact zero delta, avoiding SDPA/recompute roundoff drift.
                output[0, row, head] = output[0, row, head] + (
                    modified_head_output - original_head_output)
                if weights is not None:
                    weights[0, head, row] = changed
                after = changed[start:stop]
                support = target > 0
                self.records.append(dict(
                    head=head_label((layer, head)), generation_step=step,
                    prediction_row=klen - 1, local_query_row=row, key_length=klen,
                    query_span=[start, stop], token_grid=self.geometry["token_grid"],
                    selected_token_count=self.geometry["selected_token_count"],
                    before_map=before.float().cpu().tolist(), after_map=after.float().cpu().tolist(),
                    gt_mass_before=float(before[support].float().sum()),
                    gt_mass_after=float(after[support].float().sum()),
                    query_mass_before=float(mass), query_mass_after=float(after.float().sum()),
                    row_sum_before=float(probs.float().sum()), row_sum_after=float(changed.float().sum()),
                    native_head_output_max_abs_error=float(native_error),
                    head_output_delta_l2=float(torch.linalg.vector_norm(modified_head_output.float() - original_head_output.float())),
                    alignment_passed=bool(torch.allclose(after.float(), mass * target.float(), atol=1e-5, rtol=0.01)) if self.mode == "gt_align" else bool(torch.equal(before, after)),
                ))
            return output, weights
        return forward

    def close(self):
        for module, owned, original in reversed(self._originals):
            if owned:
                module.forward = original
            else:
                del module.forward
        self._originals.clear()

    def __exit__(self, *exc):
        self.close()


def _score(text, target):
    box, gt = parse_box(text), parse_box(target)
    valid = box is not None and all(math.isfinite(x) for x in box) and box[0] < box[2] and box[1] < box[3]
    return dict(prediction=text, parsed=box is not None, valid_bbox=valid,
                iou=box_iou(text, target),
                center_distance=math.hypot((box[0]+box[2]-gt[0]-gt[2])/2000,
                                           (box[1]+box[3]-gt[1]-gt[3])/2000) if valid else None)


def generate_comparison(model, processor, inputs, answer, settings, intervention):
    from contextlib import nullcontext
    heads, steps = validate_settings(intervention)
    if settings.get("do_sample", False):
        raise ValueError("paired smoke requires deterministic greedy generation")
    if steps != "all" and max(steps) >= int(settings.get("max_new_tokens", 32)):
        raise ValueError("generation_steps exceed max_new_tokens")
    geometry = query_geometry(inputs, processor, model, answer)
    seed = int(settings.get("seed", 20260901))
    rows, raw = {}, {}
    for mode in ("baseline", "noop", "gt_align"):
        random.seed(seed)
        torch.manual_seed(seed)
        hook = None if mode == "baseline" else QueryAttentionHook(model, heads, steps, geometry, mode)
        with torch.inference_mode(), hook if hook is not None else nullcontext():
            output = model.generate(**inputs, max_new_tokens=int(settings.get("max_new_tokens", 32)),
                                    do_sample=False, use_cache=True, return_dict_in_generate=True,
                                    output_logits=True)
        ids = output.sequences[:, geometry["prompt_length"]:]
        text = processor.batch_decode(ids, skip_special_tokens=True)[0]
        raw[mode] = output
        records = [] if hook is None else hook.records
        for record in records:
            step = record["generation_step"]
            record["predicted_token_id"] = int(ids[0, step])
            record["generated_prefix"] = processor.batch_decode(ids[:, :step], skip_special_tokens=False)[0]
            record["predicted_token_text"] = processor.batch_decode(ids[:, step:step+1], skip_special_tokens=False)[0]
        rows[mode] = dict(**_score(text, answer), token_ids=ids[0].tolist(), attention=records)
    base, noop = raw["baseline"], raw["noop"]
    same_tokens = torch.equal(base.sequences, noop.sequences)
    logits_comparable = len(base.logits) == len(noop.logits) and len(base.logits) > 0
    logits_equal = logits_comparable and all(torch.allclose(a.float(), b.float(),
        atol=float(intervention.get("logits_atol", 0.0)), rtol=float(intervention.get("logits_rtol", 0.0)))
        for a, b in zip(base.logits, noop.logits))
    maximum = max(float((a.float()-b.float()).abs().max()) for a,b in zip(base.logits, noop.logits)) if logits_comparable else None
    def covered(mode):
        actual_steps = range(len(rows[mode]["token_ids"])) if steps == "all" else steps
        expected = {(head_label(h), s) for h in heads for s in actual_steps}
        records = rows[mode]["attention"]
        return bool(expected) and len(records) == len(expected) and {
            (r["head"], r["generation_step"]) for r in records} == expected
    coverage = all(covered(m) for m in ("noop", "gt_align"))
    aligned = all(r["alignment_passed"] for m in ("noop", "gt_align") for r in rows[m]["attention"])
    gates = dict(noop_tokens_equal=same_tokens, noop_logits_close=bool(logits_equal),
                 noop_logits_max_abs_error=maximum, intervention_coverage=coverage, attention_alignment=aligned)
    deltas = {}
    for control in ("baseline", "noop"):
        a, b = rows["gt_align"], rows[control]
        deltas[control] = dict(iou=a["iou"] - b["iou"],
            center_distance=a["center_distance"] - b["center_distance"]
            if a["center_distance"] is not None and b["center_distance"] is not None else None)
    return dict(geometry=geometry, seed=seed, conditions=rows, gates=gates, paired_deltas=deltas,
                integrity_passed=bool(same_tokens and logits_equal and coverage and aligned))


def summarize_comparisons(rows):
    summaries = {}
    for condition in ("baseline", "noop", "gt_align"):
        values = [r["attention_comparison"]["conditions"][condition] for r in rows]
        distances = [v["center_distance"] for v in values if v["center_distance"] is not None]
        summaries[condition] = dict(samples=len(values), miou=sum(v["iou"] for v in values)/len(values),
            valid_bbox_rate=sum(v["valid_bbox"] for v in values)/len(values),
            mean_center_distance=sum(distances)/len(distances) if distances else None)
    return dict(conditions=summaries,
                integrity_passed=all(r["attention_comparison"]["integrity_passed"] for r in rows)
                and all(s["valid_bbox_rate"] > 0 for s in summaries.values()),
                inference_boundary="指定 head/生成行的受控概率改写敏感性；不证明自然定位机制。")


def validate_run_config(config):
    """Reject incomplete scientific settings before allocating a named run/GPU."""
    import json
    from pathlib import Path
    validate_settings(config.get("attention_intervention") or {}, allow_auto=True)
    settings = config.get("evaluation") or {}
    limit = settings.get("limit")
    if limit not in (None, "None") and (type(limit) is not int or limit < 1):
        raise ValueError("evaluation.limit must be positive or None for the complete eval set")
    if settings.get("do_sample", False):
        raise ValueError("attention intervention requires do_sample=False")
    _, steps = validate_settings(config["attention_intervention"], allow_auto=True)
    if steps != "all" and max(steps) >= int(settings.get("max_new_tokens", 32)):
        raise ValueError("generation_steps exceed max_new_tokens")
    key = settings.get("dataloader", "test_dataloader")
    data = config.get(key, {}).get("dataset", {})
    manifest = data.get("ann_file")
    if not manifest or not Path(str(manifest)).is_file():
        raise ValueError("explicit existing evaluation manifest is required")
    if int(data.get("normalized_scale", 1000)) != 1000:
        raise ValueError("intervention requires normalized_scale=1000")
    if config.get("model", {}).get("attn_implementation") not in ("eager", "sdpa"):
        raise ValueError("set runtime.model.attn_implementation to eager or sdpa")
    named = config.get("named_run") or {}
    checkpoint = named.get("resolved_resume_checkpoint") or named.get("parent_checkpoint")
    if not checkpoint or checkpoint == "-":
        raise ValueError("attention intervention requires a checkpoint source")
    from ..checkpointing import validate_checkpoint
    checkpoint = validate_checkpoint(checkpoint)
    adapter = json.loads((checkpoint / "adapter" / "adapter_config.json").read_text())
    model = config["model"]
    if Path(adapter["base_model_name_or_path"]).resolve() != Path(model["model_path"]).resolve():
        raise ValueError("adapter base model differs from branch model_path")
    lora = model.get("lora") or {}
    if int(adapter["r"]) != int(lora.get("r", 8)) or int(adapter["lora_alpha"]) != int(lora.get("alpha", 16)):
        raise ValueError("checkpoint LoRA rank/alpha differ from branch")
    target = lora.get("target_modules")
    adapter_target = adapter.get("target_modules")
    if isinstance(target, (list, tuple)) and isinstance(adapter_target, list):
        compatible = set(target) == set(adapter_target)
    else:
        compatible = target == adapter_target
    if not compatible:
        raise ValueError("checkpoint LoRA target modules differ from branch")
