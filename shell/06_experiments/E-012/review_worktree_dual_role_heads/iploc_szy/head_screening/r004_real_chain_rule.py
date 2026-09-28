"""Real-checkpoint R-004 chain-rule and finite-difference gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import torch

from ..config import Config
from ..registry import DATASETS, MODELS
from .bbox_gradient import attach_checkpoint, bbox_loss, resolve_checkpoint
from .dual_role_metrics import (
    coordinate_prediction_rows,
    coordinate_target_positions,
    validate_coordinate_positions,
)
from .probes import consecutive_spans, temporary_eager_attention


SCHEMA = "e012.real-reference-chain-rule-check/v1"


def _publish(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2,
                                    allow_nan=False) + "\n")
    temporary.replace(path)


@contextmanager
def capture_chain_rule(model, rows, reference_span, selected_heads,
                       captures, perturbation=None):
    """Capture gradients at the same post-softmax A and pre-transpose AV node."""
    from transformers.models.qwen3_vl import modeling_qwen3_vl as implementation

    original = implementation.eager_attention_forward
    modules = [module for module in model.modules()
               if module.__class__.__name__ == "Qwen3VLTextAttention"]
    if not modules or model.training:
        raise ValueError("R004 requires eval Qwen3-VL text attention")
    start, stop = map(int, reference_span)
    selected = {(int(layer), int(head)) for layer, head in selected_heads}

    def intercepted(module, query, key, value, attention_mask, scaling,
                    dropout=0.0, **kwargs):
        if module.__class__.__name__ != "Qwen3VLTextAttention":
            return original(module, query, key, value, attention_mask,
                            scaling, dropout, **kwargs)
        if dropout != 0 or query.shape[0] != 1 or attention_mask is None:
            raise ValueError("R004 requires batch=1, dropout=0 and causal mask")
        unused, attention = original(module, query, key, value, attention_mask,
                                     scaling, dropout, **kwargs)
        del unused
        layer = int(module.layer_idx)
        values = implementation.repeat_kv(value, module.num_key_value_groups)
        if perturbation is not None and layer == perturbation[0]:
            head, removal_epsilon = perturbation[1:]
            attention = attention.clone()
            attention[0, head, rows, start:stop] *= 1.0 - removal_epsilon
        if perturbation is None and any(item[0] == layer for item in selected):
            if not attention.requires_grad:
                attention.requires_grad_(True)
        head_output = torch.matmul(attention, values)

        for selected_layer, head in selected:
            if selected_layer != layer or perturbation is not None:
                continue
            a = attention[0, head, rows, start:stop].detach().float().cpu()
            v = values[0, head, start:stop].detach().float().cpu()
            captures[(layer, head)] = {"attention": a, "value": v}

            def save_attention_gradient(gradient, key=(layer, head)):
                captures[key]["grad_attention"] = (
                    gradient[0, key[1], rows, start:stop].detach().float().cpu()
                )

            def save_output_gradient(gradient, key=(layer, head)):
                captures[key]["grad_head_output"] = (
                    gradient[0, key[1], rows].detach().float().cpu()
                )

            attention.register_hook(save_attention_gradient)
            head_output.register_hook(save_output_gradient)
        return head_output.transpose(1, 2).contiguous(), attention

    implementation.eager_attention_forward = intercepted
    try:
        with temporary_eager_attention(model):
            yield len(modules)
    finally:
        implementation.eager_attention_forward = original


def _relative_error(left, right, floor=1e-12):
    return abs(left - right) / max(abs(left), abs(right), floor)


def _sample_inputs(dataset, collator, model, index, max_sequence_tokens):
    sample = dataset[index]
    encoded = collator([sample])
    metadata = encoded.pop("metadata")[0]
    labels = encoded.pop("labels")
    ids = encoded["input_ids"]
    fields = validate_coordinate_positions(
        ids[0].tolist(), labels[0].tolist(), metadata["coordinate_token_positions"]
    )
    positions = list(coordinate_target_positions(fields))
    rows = list(coordinate_prediction_rows(fields))
    if ids.shape[1] > max_sequence_tokens:
        raise ValueError("sample exceeds frozen sequence-token budget")
    tokenizer = collator.processor.tokenizer
    image_id = int(tokenizer.convert_tokens_to_ids("<|image_pad|>"))
    spans = consecutive_spans(ids[0].tolist(), image_id)
    grids = metadata["image_grid_thw"]
    if len(spans) != 2 or len(grids) != 2:
        raise ValueError("R004 requires one Reference and one Query image")
    merge = int(model.config.vision_config.spatial_merge_size)
    for span, grid in zip(spans, grids):
        temporal, height, width = map(int, grid)
        if temporal != 1 or height % merge or width % merge:
            raise ValueError("invalid merged image grid")
        if span[1] - span[0] != (height // merge) * (width // merge):
            raise ValueError("image span and merged grid differ")
    if spans[-1][1] > min(rows):
        raise ValueError("visual tokens must precede coordinate prediction rows")
    forward = {key: value.to(next(model.parameters()).device)
               for key, value in encoded.items()}
    forward.update(use_cache=False, output_attentions=False,
                   return_dict=True, logits_to_keep=0)
    return sample, metadata, forward, positions, rows, spans


def run(config):
    cfg = Config.fromfile(config)
    required = cfg["r004"]
    output = Path(cfg["work_dir"])
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    manifest = Path(cfg["screen_dataloader"]["dataset"]["ann_file"])
    manifest_hash = hashlib.sha256(manifest.read_bytes()).hexdigest()
    if manifest_hash != required["input_manifest_sha256"]:
        raise ValueError("input manifest SHA-256 mismatch")
    checkpoint = resolve_checkpoint(cfg["checkpoint_path"], cfg["model"]["model_path"])
    _publish(output / "frozen_input.json", {
        "schema": SCHEMA, "status": "planned", "config": str(Path(config).resolve()),
        "manifest": str(manifest), "manifest_sha256": manifest_hash,
        "checkpoint": checkpoint, "sample_indices": required["sample_indices"],
        "layer_heads": required["layer_heads"], "epsilons": required["epsilons"],
    })
    dataset = DATASETS.build(cfg["screen_dataloader"]["dataset"])
    wrapper = MODELS.build(cfg["model"])
    wrapper = attach_checkpoint(wrapper, checkpoint)
    model = wrapper.model.eval()
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    collator = DATASETS.build(cfg["screen_dataloader"]["collator"],
                             processor=wrapper.processor)
    records = []
    try:
        for order, index in enumerate(required["sample_indices"]):
            sample, metadata, forward, positions, rows, spans = _sample_inputs(
                dataset, collator, model, int(index), required["max_sequence_tokens"]
            )
            with torch.no_grad(), temporary_eager_attention(model):
                baseline_output = model(**forward)
                baseline_logits = baseline_output.logits[0, rows].float().cpu()
                baseline_loss = float(bbox_loss(
                    baseline_output.logits, forward["input_ids"], positions
                ))
            captures = {}
            with torch.enable_grad(), capture_chain_rule(
                model, rows, spans[0], required["layer_heads"], captures
            ) as layers:
                output_model = model(**forward)
                loss = bbox_loss(output_model.logits, forward["input_ids"], positions)
                hooked_logits = output_model.logits[0, rows].detach().float().cpu()
                loss.backward()
            parity = float((hooked_logits - baseline_logits).abs().max())
            if parity > required["parity_atol"]:
                raise ValueError(f"empty hook parity failed: {parity}")
            if len(captures) != len(required["layer_heads"]):
                raise ValueError("not all frozen heads were captured")
            head_records = []
            for layer, head in required["layer_heads"]:
                values = captures[(layer, head)]
                if set(values) != {"attention", "value", "grad_attention", "grad_head_output"}:
                    raise ValueError("incomplete A/AV gradient capture")
                a, v = values["attention"], values["value"]
                e_attention = a * values["grad_attention"]
                e_value = (values["grad_head_output"][:, None, :]
                           * a[:, :, None] * v[None, :, :]).sum(-1)
                max_abs = float((e_attention - e_value).abs().max())
                scale = torch.maximum(e_attention.abs(), e_value.abs())
                relative_l2 = float((e_attention - e_value).norm()
                                    / scale.norm().clamp_min(1e-30))
                algebra_pass = bool(torch.allclose(
                    e_attention, e_value, atol=required["algebra_atol"],
                    rtol=required["algebra_rtol"]
                ))
                signed = float(e_attention.sum())
                finite_differences = []
                for epsilon in required["epsilons"]:
                    losses = []
                    for removal in (-epsilon, epsilon):
                        with torch.no_grad(), capture_chain_rule(
                            model, rows, spans[0], required["layer_heads"], {},
                            perturbation=(layer, head, removal)
                        ):
                            changed = model(**forward)
                            losses.append(float(bbox_loss(
                                changed.logits, forward["input_ids"], positions
                            )))
                    central = (losses[1] - losses[0]) / (2.0 * epsilon)
                    predicted = -signed
                    rel = _relative_error(central, predicted)
                    finite_differences.append({
                        "epsilon": epsilon, "loss_negative_removal": losses[0],
                        "loss_positive_removal": losses[1],
                        "predicted_dloss_dremoval": predicted,
                        "central_difference": central,
                        "sign_agreement": bool(central * predicted > 0),
                        "relative_error": rel,
                        "pass": bool(central * predicted > 0 and rel <= required["fd_relative_error_max"]),
                    })
                head_records.append({
                    "layer": layer, "head": head,
                    "reference_edges": int(e_attention.numel()),
                    "signed_reference_contribution": signed,
                    "absolute_reference_contribution": float(e_attention.abs().sum()),
                    "algebra_max_abs_error": max_abs,
                    "algebra_relative_l2_error": relative_l2,
                    "algebra_pass": algebra_pass,
                    "finite_differences": finite_differences,
                })
            records.append({
                "dataset_index": int(index), "sample_id": sample["id"],
                "coordinate_token_positions": metadata["coordinate_token_positions"],
                "coordinate_prediction_rows": rows,
                "reference_span": list(spans[0]), "query_span": list(spans[1]),
                "baseline_coordinate_ce": baseline_loss,
                "empty_hook_max_abs_logit_error": parity,
                "text_layers": layers, "heads": head_records,
            })
            _publish(output / "records.json", {
                "schema": SCHEMA, "status": "in_progress", "records": records
            })
            print(f"[R004_REAL] {order + 1}/{len(required['sample_indices'])}", flush=True)
            del output_model, loss, baseline_output, forward
        heads = [head for record in records for head in record["heads"]]
        finite = [item for head in heads for item in head["finite_differences"]]
        summary = {
            "schema": SCHEMA,
            "status": "completed" if all(head["algebra_pass"] for head in heads)
            and all(item["pass"] for item in finite) else "completed_gate_failed",
            "real_checkpoint_tested": True, "real_images_tested": True,
            "samples": len(records), "head_sample_pairs": len(heads),
            "algebra_pass_count": sum(head["algebra_pass"] for head in heads),
            "finite_difference_pass_count": sum(item["pass"] for item in finite),
            "finite_difference_total": len(finite),
            "max_algebra_abs_error": max(head["algebra_max_abs_error"] for head in heads),
            "max_algebra_relative_l2_error": max(head["algebra_relative_l2_error"] for head in heads),
            "max_empty_hook_abs_logit_error": max(
                record["empty_hook_max_abs_logit_error"] for record in records
            ),
            "claim_boundary": "implementation correctness gate only; no head-selection or causal claim",
        }
        _publish(output / "records.json", {"schema": SCHEMA, "status": summary["status"], "records": records})
        _publish(output / "summary.json", summary)
        return 0 if summary["status"] == "completed" else 1
    except Exception as exc:
        _publish(output / "failure.json", {"schema": SCHEMA, "status": "failed",
                                           "reason": f"{type(exc).__name__}: {exc}"})
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    args = parser.parse_args(argv)
    return run(args.config)


if __name__ == "__main__":
    raise SystemExit(main())
