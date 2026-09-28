"""E-012 两阶段 head 路径 patching。

上游干预把指定 head 在 bbox prediction rows 上的 query-visual attention
按真实 merged token grid 做水平翻转；该变换严格保持每行 query mass、数值集合与熵。
下游 patch 位于 A@V 之后、o_proj 之前，只替换指定 head/rows 的 128 维输出。
"""
from __future__ import annotations

import argparse
import json
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch

from ..config import Config
from ..prompting.coordinates import parse_box
from ..registry import DATASETS, HEAD_PROBES, MODELS
from .bbox_gradient import attach_checkpoint, bbox_loss, publish, resolve_checkpoint
from .probes import temporary_eager_attention

SCHEMA = "iploc-szy.head-circuit-path-patching/v1"


def head_label(head):
    return f"L{int(head[0]):02d}H{int(head[1]):02d}"


def parse_heads(values):
    heads = tuple(sorted({(int(x[0]), int(x[1])) for x in values}))
    if not heads:
        raise ValueError("head set must be non-empty")
    if any(layer < 0 or head < 0 for layer, head in heads):
        raise ValueError("layer/head indices must be non-negative")
    return heads


def horizontal_flip_visual(block, height, width):
    """Flip only spatial locations. block is [..., height*width]."""
    if block.shape[-1] != height * width:
        raise ValueError("visual block length differs from merged grid")
    return block.reshape(*block.shape[:-1], height, width).flip(-1).reshape_as(block)


def entropy(values):
    mass = values.sum(-1, keepdim=True)
    probability = values.float() / mass.float().clamp_min(1e-12)
    return -(probability * probability.clamp_min(1e-12).log()).sum(-1)


def relative_change(clean, corrupt):
    numerator = torch.linalg.vector_norm((corrupt.float() - clean.float()).reshape(-1))
    denominator = torch.linalg.vector_norm(clean.float().reshape(-1)).clamp_min(1e-8)
    return float(numerator / denominator)


def safe_fraction(effect, damage, threshold=1e-4):
    return None if damage <= threshold else float(effect / damage)


def box_iou(a, b):
    if a is None or b is None:
        return None
    iw = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    ih = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    intersection = iw * ih
    union = ((a[2] - a[0]) * (a[3] - a[1])
             + (b[2] - b[0]) * (b[3] - b[1]) - intersection)
    return None if union <= 0 else float(intersection / union)


class CircuitHook:
    """One forward pass can corrupt upstream attention, capture and/or patch downstream A@V."""

    def __init__(self, rows, query_span, grid_hw, corrupt_heads=(), capture_heads=(),
                 patch_values=None, corruption_mode="horizontal_flip", atol=2e-5):
        self.rows = list(map(int, rows))
        self.query_span = tuple(map(int, query_span[:2]))
        self.grid_hw = tuple(map(int, grid_hw))
        self.corruption_mode = str(corruption_mode)
        if self.corruption_mode not in ("horizontal_flip", "zero_query_attention"):
            raise ValueError("corruption_mode must be horizontal_flip or zero_query_attention")
        self.corrupt_heads = set(parse_heads(corrupt_heads)) if corrupt_heads else set()
        self.capture_heads = set(parse_heads(capture_heads)) if capture_heads else set()
        self.patch_values = {} if patch_values is None else {
            (int(k[0]), int(k[1])): v for k, v in patch_values.items()
        }
        self.atol = float(atol)
        start, stop = self.query_span
        if not self.rows or len(self.rows) != len(set(self.rows)) or min(self.rows) < 0:
            raise ValueError("prediction rows must be non-empty, unique, and non-negative")
        if start < 0 or stop <= start or min(self.grid_hw) < 1:
            raise ValueError("query span and merged grid must be positive")
        if stop - start != self.grid_hw[0] * self.grid_hw[1]:
            raise ValueError("query span length differs from merged grid")
        self.captured = {}
        self.fired = {"corrupt": {}, "capture": {}, "patch": {}}
        self.audits = []

    def _mark(self, kind, head):
        self.fired[kind][head_label(head)] = self.fired[kind].get(head_label(head), 0) + 1

    def validate(self):
        expected = {
            "corrupt": self.corrupt_heads,
            "capture": self.capture_heads,
            "patch": set(self.patch_values),
        }
        for kind, heads in expected.items():
            actual = self.fired[kind]
            missing = [head_label(h) for h in heads if actual.get(head_label(h), 0) != 1]
            if missing:
                raise ValueError(f"{kind} hook firing mismatch: {missing}")

    @contextmanager
    def installed(self, model):
        from transformers.models.qwen3_vl import modeling_qwen3_vl as implementation
        original = implementation.eager_attention_forward
        start, stop = self.query_span
        height, width = self.grid_hw

        def intercepted(module, query, key, value, attention_mask, scaling, dropout=0.0, **kwargs):
            output, attention = original(module, query, key, value, attention_mask,
                                         scaling, dropout, **kwargs)
            if module.__class__.__name__ != "Qwen3VLTextAttention":
                return output, attention
            if query.shape[0] != 1 or dropout != 0:
                raise ValueError("circuit hook requires batch=1 and zero dropout")
            layer = int(module.layer_idx)
            layer_corrupt = sorted(h for h in self.corrupt_heads if h[0] == layer)
            if layer_corrupt:
                attention = attention.clone()
                for head in layer_corrupt:
                    before = attention[0, head[1], self.rows, start:stop].clone()
                    full_sum_before = attention[0, head[1], self.rows].sum(-1).clone()
                    if self.corruption_mode == "horizontal_flip":
                        after = horizontal_flip_visual(before, height, width)
                    else:
                        after = torch.zeros_like(before)
                    attention[0, head[1], self.rows, start:stop] = after
                    full_sum_after = attention[0, head[1], self.rows].sum(-1)
                    removed = before.sum(-1) - after.sum(-1)
                    full_row_sum_drop_error = float(
                        ((full_sum_before - full_sum_after) - removed).abs().max())
                    mass_error = float((before.sum(-1) - after.sum(-1)).abs().max())
                    sorted_error = float((before.float().sort(-1).values
                                          - after.float().sort(-1).values).abs().max())
                    entropy_error = float((entropy(before) - entropy(after)).abs().max())
                    remaining_query_mass_max = float(after.sum(-1).abs().max())
                    if self.corruption_mode == "horizontal_flip":
                        if max(mass_error, sorted_error, entropy_error,
                               full_row_sum_drop_error) > self.atol:
                            raise ValueError("spatial flip failed mass/value/entropy preservation")
                    elif max(remaining_query_mass_max, full_row_sum_drop_error) > self.atol:
                        raise ValueError("zero attention failed block/drop integrity")
                    self.audits.append(dict(
                        head=head_label(head), corruption_mode=self.corruption_mode,
                        query_mass_mean=float(before.sum(-1).float().mean()),
                        removed_query_mass_mean=float(removed.float().mean()),
                        remaining_query_mass_max=remaining_query_mass_max,
                        full_row_sum_drop_error=full_row_sum_drop_error,
                        attention_l1_change_mean=float((after.float() - before.float()).abs().sum(-1).mean()),
                        mass_error=mass_error,
                        sorted_value_error=sorted_error,
                        entropy_error=entropy_error,
                    ))
                    self._mark("corrupt", head)
                values = implementation.repeat_kv(value, module.num_key_value_groups)
                output = torch.matmul(attention, values).transpose(1, 2).contiguous()

            for head in sorted(h for h in self.capture_heads if h[0] == layer):
                self.captured[head] = output[0, self.rows, head[1]].detach().cpu().clone()
                self._mark("capture", head)

            layer_patches = sorted(h for h in self.patch_values if h[0] == layer)
            if layer_patches:
                output = output.clone()
                for head in layer_patches:
                    source = self.patch_values[head]
                    expected = (len(self.rows), output.shape[-1])
                    if tuple(source.shape) != expected:
                        raise ValueError(f"patch shape {tuple(source.shape)} != {expected}")
                    output[0, self.rows, head[1]] = source.to(output.device, output.dtype)
                    self._mark("patch", head)
            return output, attention

        implementation.eager_attention_forward = intercepted
        try:
            with temporary_eager_attention(model):
                yield self
        finally:
            implementation.eager_attention_forward = original


def build_context(cfg):
    from ..compat import ensure_torchvision_nms_schema
    ensure_torchvision_nms_schema()
    dataset = DATASETS.build(cfg["screen_dataloader"]["dataset"])
    probe = HEAD_PROBES.build(cfg["head_screening"]["probe"])
    checkpoint = resolve_checkpoint(cfg.get("checkpoint_path"), cfg["model"]["model_path"])
    wrapper = attach_checkpoint(MODELS.build(cfg["model"]), checkpoint)
    collator = DATASETS.build(cfg["screen_dataloader"]["collator"], processor=wrapper.processor)
    runner = SimpleNamespace(wrapper=wrapper, dataset=dataset, collator=collator, world_size=1)
    return dataset, probe, checkpoint, wrapper, runner


def dataset_name(dataset, index):
    row = dataset.rows[index]
    raw = row.get("raw", {})
    name = raw.get("dataset", row.get("dataset"))
    if name is None:
        raise ValueError(f"dataset identity is missing for index {index}")
    return str(name)


def select_indices(dataset, frozen_path, counts):
    frozen = json.loads(Path(frozen_path).read_text())
    allowed = set(map(int, frozen["selected_indices"]))
    counts = {str(k): int(v) for k, v in counts.items()}
    selected, observed = [], {name: 0 for name in counts}
    for index in sorted(allowed):
        name = dataset_name(dataset, index)
        if name in counts and observed[name] < counts[name]:
            selected.append(index)
            observed[name] += 1
    if observed != counts:
        raise ValueError(f"unable to meet stratified counts: {observed} != {counts}")
    return selected, observed


def decode(logits, positions, tokenizer):
    rows = torch.tensor(positions, device=logits.device) - 1
    tokens = logits[0, rows].argmax(-1)
    text = tokenizer.decode(tokens.tolist())
    return text, parse_box(text)


def run_condition(model, forward, positions, tokenizer, hook=None):
    with torch.no_grad():
        if hook is None:
            output = model(**forward)
        else:
            with hook.installed(model):
                output = model(**forward)
            hook.validate()
        loss = float(bbox_loss(output.logits, forward["input_ids"], positions))
        text, box = decode(output.logits, positions, tokenizer)
        selected_logits = output.logits[0, torch.tensor(positions, device=output.logits.device) - 1]
        selected_logits = selected_logits.float().cpu().clone()
    del output
    return dict(loss=loss, text=text, box=box), selected_logits


def path_spec(raw):
    candidate_u = parse_heads(raw["upstream"])
    control_u = parse_heads(raw["upstream_control"])
    candidate_d = parse_heads(raw["downstream"])
    control_d = parse_heads(raw["downstream_control"])
    for u in candidate_u + control_u:
        for d in candidate_d + control_d:
            if u[0] >= d[0]:
                raise ValueError(f"upstream must precede downstream: {u} !< {d}")
    return dict(name=str(raw["name"]), candidate_u=candidate_u, control_u=control_u,
                candidate_d=candidate_d, control_d=control_d)


def condition_record(base, value):
    result = dict(value)
    result["iou_vs_clean"] = box_iou(base["box"], value["box"])
    return result


def evaluate_path(model, forward, positions, rows, query_span, grid_hw, tokenizer, spec,
                  corruption_mode="horizontal_flip", identity=False,
                  parity_atol=0.002, parity_rtol=0.002):
    all_d = tuple(sorted(set(spec["candidate_d"] + spec["control_d"])))
    clean_hook = CircuitHook(rows, query_span, grid_hw, capture_heads=all_d)
    clean, clean_logits = run_condition(model, forward, positions, tokenizer, clean_hook)

    corrupt_hook = CircuitHook(rows, query_span, grid_hw, corrupt_heads=spec["candidate_u"],
                               capture_heads=all_d, corruption_mode=corruption_mode)
    corrupt, corrupt_logits = run_condition(model, forward, positions, tokenizer, corrupt_hook)

    upstream_control_hook = CircuitHook(rows, query_span, grid_hw,
                                        corrupt_heads=spec["control_u"],
                                        corruption_mode=corruption_mode)
    upstream_control, _ = run_condition(model, forward, positions, tokenizer,
                                        upstream_control_hook)

    conditions = {
        "clean": clean,
        "upstream_corrupt": condition_record(clean, corrupt),
        "upstream_control": condition_record(clean, upstream_control),
    }
    for label, downstream in (("candidate", spec["candidate_d"]),
                              ("control", spec["control_d"])):
        rescue_hook = CircuitHook(rows, query_span, grid_hw,
                                  corrupt_heads=spec["candidate_u"],
                                  patch_values={h: clean_hook.captured[h] for h in downstream},
                                  corruption_mode=corruption_mode)
        rescue, _ = run_condition(model, forward, positions, tokenizer, rescue_hook)
        transfer_hook = CircuitHook(rows, query_span, grid_hw,
                                    patch_values={h: corrupt_hook.captured[h] for h in downstream})
        transfer, _ = run_condition(model, forward, positions, tokenizer, transfer_hook)
        conditions[f"{label}_rescue"] = condition_record(clean, rescue)
        conditions[f"{label}_transfer"] = condition_record(clean, transfer)

    identity_result = None
    if identity:
        native, native_logits = run_condition(model, forward, positions, tokenizer)
        torch.testing.assert_close(clean_logits, native_logits,
                                   atol=parity_atol, rtol=parity_rtol)
        if abs(clean["loss"] - native["loss"]) > parity_atol:
            raise ValueError("capture-only clean loss differs from native forward")
        clean_identity = CircuitHook(rows, query_span, grid_hw,
                                     patch_values={h: clean_hook.captured[h] for h in all_d})
        _, identity_logits = run_condition(model, forward, positions, tokenizer, clean_identity)
        torch.testing.assert_close(identity_logits, clean_logits,
                                   atol=parity_atol, rtol=parity_rtol)
        corrupt_identity = CircuitHook(rows, query_span, grid_hw,
                                       corrupt_heads=spec["candidate_u"],
                                       patch_values={h: corrupt_hook.captured[h] for h in all_d},
                                       corruption_mode=corruption_mode)
        _, corrupt_identity_logits = run_condition(model, forward, positions, tokenizer,
                                                    corrupt_identity)
        torch.testing.assert_close(corrupt_identity_logits, corrupt_logits,
                                   atol=parity_atol, rtol=parity_rtol)
        identity_result = dict(
            native_capture_max_logit_error=float((clean_logits - native_logits).abs().max()),
            clean_max_logit_error=float((identity_logits - clean_logits).abs().max()),
            corrupt_max_logit_error=float((corrupt_identity_logits - corrupt_logits).abs().max()))

    damage = corrupt["loss"] - clean["loss"]
    metrics = {
        "upstream_damage": float(damage),
        "upstream_control_damage": float(upstream_control["loss"] - clean["loss"]),
    }
    for label in ("candidate", "control"):
        rescue_effect = corrupt["loss"] - conditions[f"{label}_rescue"]["loss"]
        transfer_effect = conditions[f"{label}_transfer"]["loss"] - clean["loss"]
        metrics.update({
            f"{label}_rescue_effect": float(rescue_effect),
            f"{label}_rescue_fraction": safe_fraction(rescue_effect, damage),
            f"{label}_transfer_effect": float(transfer_effect),
        })
    changes = {}
    for head in all_d:
        changes[head_label(head)] = relative_change(clean_hook.captured[head],
                                                    corrupt_hook.captured[head])
    return dict(path=spec["name"], conditions=conditions, metrics=metrics,
                downstream_relative_change=changes,
                attention_audit=corrupt_hook.audits,
                control_attention_audit=upstream_control_hook.audits,
                identity=identity_result)


def summarize(records, paths):
    result = []
    for spec in paths:
        rows = [r for r in records if r["path"] == spec["name"]]
        keys = ("upstream_damage", "upstream_control_damage", "candidate_rescue_effect",
                "candidate_transfer_effect", "control_rescue_effect", "control_transfer_effect")
        item = dict(path=spec["name"], samples=len(rows))
        for key in keys:
            values = np.array([r["metrics"][key] for r in rows], dtype=np.float64)
            item[key + "_mean"] = float(values.mean())
            item[key + "_median"] = float(np.median(values))
            item[key + "_positive_fraction"] = float((values > 0).mean())
        eligible = [r["metrics"]["candidate_rescue_fraction"] for r in rows
                    if r["metrics"]["candidate_rescue_fraction"] is not None]
        item["candidate_rescue_fraction_defined_n"] = len(eligible)
        item["candidate_rescue_fraction_mean"] = (float(np.mean(eligible)) if eligible else None)
        for label, audit_key in (("candidate", "attention_audit"),
                                 ("control", "control_attention_audit")):
            audits = [audit for row in rows for audit in row.get(audit_key, [])]
            if audits:
                item[f"{label}_removed_query_mass_mean"] = float(np.mean(
                    [audit["removed_query_mass_mean"] for audit in audits]))
                item[f"{label}_attention_l1_change_mean"] = float(np.mean(
                    [audit["attention_l1_change_mean"] for audit in audits]))
        result.append(item)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    parser.add_argument("overrides", nargs="*")
    args = parser.parse_args(argv)
    cfg = Config.fromfile(args.config).merge_options(args.overrides)
    root = Path(cfg["work_dir"])
    root.mkdir(parents=True, exist_ok=False)
    try:
        dataset, probe, checkpoint, wrapper, runner = build_context(cfg)
        circuit = cfg["head_circuit"]
        indices, counts = select_indices(dataset, circuit["sample_source"],
                                         circuit["samples_per_dataset"])
        paths = [path_spec(raw) for raw in circuit["paths"]]
        records = []
        for order, index in enumerate(indices):
            sample, encoded, metadata, positions, rows, spans = probe.encode_sample(runner, index)
            grids = metadata["image_grid_thw"]
            merge = int(wrapper.model.config.vision_config.spatial_merge_size)
            grid_hw = (int(grids[-1][1]) // merge, int(grids[-1][2]) // merge)
            forward = {k: v.to(wrapper.input_device) for k, v in encoded.items()}
            forward.update(use_cache=False, output_attentions=False,
                           return_dict=True, logits_to_keep=0)
            for path_index, spec in enumerate(paths):
                result = evaluate_path(wrapper.model, forward, positions, rows, spans[-1],
                                       grid_hw, wrapper.processor.tokenizer, spec,
                                       corruption_mode=str(circuit.get(
                                           "corruption_mode", "horizontal_flip")),
                                       identity=(order == 0 and path_index == 0),
                                       parity_atol=float(circuit.get("parity_atol", 0.002)),
                                       parity_rtol=float(circuit.get("parity_rtol", 0.002)))
                result.update(dataset_index=int(index),
                              sample_id=sample.get("sample_id", sample.get("id")),
                              dataset=dataset_name(dataset, index))
                records.append(result)
                publish(root / "records.json", dict(schema=SCHEMA, records=records))
            print(f"[HEAD_CIRCUIT] {order + 1}/{len(indices)}", flush=True)
        payload = dict(schema=SCHEMA, status="completed", checkpoint=checkpoint,
                       corruption_mode=str(circuit.get("corruption_mode", "horizontal_flip")),
                       selected_indices=indices, samples_per_dataset=counts,
                       paths=[{k: ([head_label(h) for h in v] if isinstance(v, tuple) else v)
                               for k, v in spec.items()} for spec in paths],
                       summary=summarize(records, paths), records=len(records))
        publish(root / "summary.json", payload)
        print(f"[HEAD_CIRCUIT_DONE] samples={len(indices)} paths={len(paths)}", flush=True)
    except BaseException as error:
        publish(root / "failure.json", dict(status="failed", exception=type(error).__name__,
                                            reason=str(error)))
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
