"""Reference-image gradient-gated spatial-frequency head selection for E-012.

The gradient and spatial map both use teacher-forced bbox prediction rows as
queries and *reference-image* visual tokens as keys.  This is a selection
diagnostic only; it does not patch or ablate the model.
"""
from __future__ import annotations

import argparse
import copy
from collections import Counter, defaultdict
from contextlib import contextmanager
import json
import hashlib
import math
from pathlib import Path
import runpy

import numpy as np

from ..prompting.coordinates import parse_box
from .bbox_gradient import bbox_loss, reduce_edges
from .gradient_attention_maps import source_inputs
from .gradient_gated_spatial_frequency import (frequency_plot, head_name, normalized_entropy, publish,
                                                retained_mass_peak_component_fiou, valid_target_indices,
                                                capture_candidate_maps)
from .spatial_iou_gate import dominant_mass_component, choose_iou_heads
from .head_circuit import build_context, dataset_name
from .probes import temporary_eager_attention

SCHEMA = "iploc-szy.reference-gradient-gated-spatial-frequency/v1"


@contextmanager
def capture_reference_gradient(model, rows, span, scores, maps):
    """Reconnect real eager attention to A@V and collect reference-edge gradients/maps."""
    from transformers.models.qwen3_vl import modeling_qwen3_vl as implementation
    original = implementation.eager_attention_forward
    modules = [module for module in model.modules() if module.__class__.__name__ == "Qwen3VLTextAttention"]
    if not modules or model.training:
        raise ValueError("reference selector requires eval Qwen3-VL text attention")
    start, stop = map(int, span[:2])

    def intercepted(module, query, key, value, attention_mask, scaling, dropout=0.0, **kwargs):
        if module.__class__.__name__ != "Qwen3VLTextAttention":
            return original(module, query, key, value, attention_mask, scaling, dropout, **kwargs)
        if dropout != 0 or query.shape[0] != 1 or attention_mask is None:
            raise ValueError("reference selector requires batch=1, dropout=0, causal mask")
        unused, attention = original(module, query, key, value, attention_mask, scaling, dropout, **kwargs)
        del unused
        layer = int(module.layer_idx)
        if not attention.requires_grad:
            attention.requires_grad_(True)
        selected = attention[0, :, rows, start:stop].detach().float()
        maps[layer] = selected.cpu().numpy()

        def save_gradient(gradient):
            if layer in scores:
                raise RuntimeError("duplicate text-layer gradient; checkpoint recomputation unsupported")
            scores[layer] = reduce_edges(selected, gradient[0, :, rows, start:stop]).cpu()

        attention.register_hook(save_gradient)
        values = implementation.repeat_kv(value, module.num_key_value_groups)
        return torch_matmul_attention(attention, values), attention

    # Defined outside the interception logic so its layout is explicit and matches eager attention.
    import torch

    def torch_matmul_attention(attention, values):
        return torch.matmul(attention, values).transpose(1, 2).contiguous()

    implementation.eager_attention_forward = intercepted
    try:
        with temporary_eager_attention(model):
            yield len(modules)
    finally:
        implementation.eager_attention_forward = original


def valid_reference_indices(config, expected_indices, policy):
    from ..registry import DATASETS
    dataset = DATASETS.build(config["screen_dataloader"]["dataset"])
    valid, excluded = [], []
    for index in sorted(map(int, expected_indices)):
        sample = dataset[index]
        answers = sample.get("reference_answers", [])
        box = parse_box(answers[0]) if len(answers) == 1 else None
        reason = None
        if len(answers) != 1:
            reason = "expected_exactly_one_reference_answer"
        elif box is None:
            reason = "unparseable_reference_answer"
        elif not (box[2] > box[0] and box[3] > box[1]):
            reason = "non_positive_normalized_reference_box"
        if reason is None:
            valid.append(index)
        else:
            excluded.append(dict(dataset_index=index, sample_id=sample.get("id"), dataset=dataset_name(dataset, index),
                                 reference_answers=answers, reason=reason))
    if excluded and policy != "exclude":
        raise ValueError(f"invalid reference GT samples require invalid_gt_policy=exclude: {excluded}")
    if not valid:
        raise ValueError("no samples have a valid reference GT box")
    return valid, excluded


def top_candidates(values, top_m):
    if values.shape != (36, 32) or not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("invalid reference absolute gradient matrix")
    return sorted(np.ndindex(values.shape), key=lambda item: (-values[item], item[0], item[1]))[:top_m]


def source_from_selection_summary(path, expected_sha256):
    """Use the explicit selection artifact without opening its ancestor runs."""
    path = Path(path)
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise ValueError("selection summary SHA-256 mismatch")
    summary = json.loads(raw)
    if summary.get("status") != "completed":
        raise ValueError("selection summary is incomplete")
    source = copy.deepcopy(summary["source"])
    indices = source["selected_indices"]
    if len(indices) != len(set(indices)) or len(indices) != summary["source_samples"]:
        raise ValueError("selection summary population mismatch")
    if hashlib.sha256(Path(source["manifest"]).read_bytes()).hexdigest() != source["manifest_sha256"]:
        raise ValueError("selection manifest SHA-256 mismatch")
    source["selection_summary"] = str(path.resolve())
    source["selection_summary_sha256"] = digest
    return source, summary["parameters"]


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--source-summary")
    parser.add_argument("--source-summary-sha256")
    parser.add_argument("--checkpoint")
    parser.add_argument("--output-dir")
    parser.add_argument("--role", choices=("query", "reference"), default="reference")
    parser.add_argument("--samples-per-dataset", type=int, help="explicit smoke subset only")
    parser.add_argument("--device-map", help="optional model placement override")
    args = parser.parse_args(argv)
    spec = runpy.run_path(args.config)["selection_spec"]
    role = args.role
    if args.source_summary:
        if not args.source_summary_sha256 or not args.checkpoint or not args.output_dir:
            parser.error("--source-summary requires its SHA-256, --checkpoint and --output-dir")
        source, parameters = source_from_selection_summary(args.source_summary, args.source_summary_sha256)
        for key in ("gradient_top_m", "spatial_top_m", "visual_mass_quantile", "fiou_weight", "top_k", "invalid_gt_policy"):
            if spec[key] != parameters[key]:
                raise ValueError(f"selection parameter changed: {key}")
        if parameters["retained_attention_mass"] != 0.5:
            raise ValueError("unsupported retained attention mass")
    else:
        if args.checkpoint or role != "reference":
            parser.error("checkpoint/role overrides require an explicit --source-summary")
        source = source_inputs(spec["source_run_dir"], 10)
    if args.output_dir:
        spec["output_dir"] = args.output_dir
    if args.checkpoint:
        source["config"]["checkpoint_path"] = str(Path(args.checkpoint).resolve())
    if args.device_map:
        source["config"]["model"]["device_map"] = args.device_map
    source["config"]["work_dir"] = spec["output_dir"]
    output = Path(spec["output_dir"])
    if output.exists():
        raise FileExistsError(f"refusing to overwrite: {output}")
    top_gradient, top_per_sample, top_k = (int(spec[key]) for key in ("gradient_top_m", "spatial_top_m", "top_k"))
    if not 1 <= top_k <= top_per_sample <= top_gradient <= 1152:
        raise ValueError("require 1 <= top_k <= spatial_top_m <= gradient_top_m <= 1152")
    if not 0 <= float(spec["visual_mass_quantile"]) < 1 or float(spec["fiou_weight"]) < 0:
        raise ValueError("invalid visual_mass_quantile or fiou_weight")
    policy = str(spec.get("invalid_gt_policy", "fail"))
    iou_threshold = spec.get("min_component_iou")
    cached_candidates = None
    if iou_threshold is not None:
        iou_threshold = float(iou_threshold)
        if not 0 < iou_threshold <= 1 or role != "reference":
            raise ValueError("IoU-constrained cached selection requires reference role and 0 < threshold <= 1")
        raw = Path(spec["gradient_records_path"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != spec["gradient_records_sha256"]:
            raise ValueError("source reference gradient records SHA-256 mismatch")
        cached = json.loads(raw)
        if cached.get("status") != "completed" or cached.get("schema") != SCHEMA:
            raise ValueError("reference gradient records are not completed")
        cached_candidates = {int(row["dataset_index"]): row for row in cached["records"]}
        if len(cached_candidates) != len(cached["records"]) or set(cached_candidates) != set(source["selected_indices"]):
            raise ValueError("source reference gradient population mismatch")
        for row in cached_candidates.values():
            pairs = {(item["layer"], item["query_head"]) for item in row["gradient_candidates"]}
            if len(pairs) != top_gradient or len(row["gradient_candidates"]) != top_gradient:
                raise ValueError("source gradient candidate count mismatch")
    selection_details = dict(min_component_iou=iou_threshold,
        component_rule="largest_attention_mass" if iou_threshold is not None else "global_peak",
        ranking_rule="iou_then_gradient_then_entropy" if iou_threshold is not None else "weighted_spatial_score",
        allow_empty=iou_threshold is not None,
        gradient_records_path=spec.get("gradient_records_path"),
        gradient_records_sha256=spec.get("gradient_records_sha256"))
    validate_indices = valid_reference_indices if role == "reference" else valid_target_indices
    valid_indices, excluded = validate_indices(source["config"], source["selected_indices"], policy)
    if args.samples_per_dataset is not None:
        if args.samples_per_dataset < 1:
            parser.error("--samples-per-dataset must be positive")
        from ..registry import DATASETS
        dataset = DATASETS.build(source["config"]["screen_dataloader"]["dataset"])
        counts, subset = Counter(), []
        for index in valid_indices:
            name = dataset_name(dataset, index)
            if counts[name] < args.samples_per_dataset:
                subset.append(index)
                counts[name] += 1
        valid_indices = subset
    from .bbox_gradient import resolve_checkpoint
    checked_checkpoint = resolve_checkpoint(source["config"].get("checkpoint_path"), source["config"]["model"]["model_path"])
    if args.check_only:
        print(json.dumps(dict(schema=SCHEMA, status="validated", source_run_dir=source["root"],
                              source_frozen_sha256=source["frozen_sha256"], source_summary_sha256=source["summary_sha256"],
                              source_samples=len(source["selected_indices"]), analyzed_samples=len(valid_indices),
                              role=role, checkpoint=checked_checkpoint, selection=selection_details,
                              excluded_invalid_gt=excluded), ensure_ascii=False))
        return 0

    output.mkdir(parents=True)
    publish(output / "resolved_plan.json", dict(schema=SCHEMA, status="planned", source=source,
        parameters=dict(role=role, gradient_top_m=top_gradient, spatial_top_m=top_per_sample,
                        visual_mass_quantile=float(spec["visual_mass_quantile"]), fiou_weight=float(spec["fiou_weight"]),
                        top_k=top_k, retained_attention_mass=0.5, invalid_gt_policy=policy, **selection_details),
        analyzed_indices=valid_indices, excluded_invalid_gt=excluded,
        smoke_samples_per_dataset=args.samples_per_dataset, checkpoint=checked_checkpoint,
        code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        claim_boundary="selection diagnostic only; requires independent causal ablation"))
    try:
        dataset, probe, checkpoint, wrapper, runner = build_context(source["config"])
        from .metrics import normalized_box_occupancy
        import torch
        seed = int(source["config"]["head_screening"]["probe"]["seed"])
        torch.manual_seed(seed)
        np.random.seed(seed)
        model = wrapper.model.eval().requires_grad_(False)
        flags = [(parameter, parameter.requires_grad) for parameter in model.parameters()]
        all_records, frequency, by_dataset = [], Counter(), defaultdict(Counter)
        legacy_frequency = Counter()
        try:
            for parameter, _ in flags:
                parameter.requires_grad_(False)
            for order, index in enumerate(valid_indices):
                sample, encoded, metadata, positions, rows, spans = probe.encode_sample(runner, index)
                reference_box = parse_box(sample["reference_answers"][0] if role == "reference" else sample["query_answer"])
                image_index = 0 if role == "reference" else -1
                grid = metadata["image_grid_thw"][image_index]
                merge = int(model.config.vision_config.spatial_merge_size)
                height, width = int(grid[1]) // merge, int(grid[2]) // merge
                if spans[image_index][1] - spans[image_index][0] != height * width:
                    raise ValueError("reference grid/token mismatch")
                forward = {key: value.to(wrapper.input_device) for key, value in encoded.items()}
                forward.update(use_cache=False, output_attentions=False, return_dict=True, logits_to_keep=0)
                baseline = None
                if order == 0:
                    with torch.no_grad(), temporary_eager_attention(model):
                        baseline = model(**forward).logits[0, rows].float().cpu()
                scores, maps = {}, {}
                if cached_candidates is not None:
                    cached_row = cached_candidates[index]
                    if cached_row["sample_id"] != sample["id"]:
                        raise ValueError("source reference candidate sample identity mismatch")
                    candidates = [(item["layer"], item["query_head"]) for item in cached_row["gradient_candidates"]]
                    gradients = {(item["layer"], item["query_head"]): item["gradient_absolute"]
                                 for item in cached_row["gradient_candidates"]}
                    with torch.no_grad(), capture_candidate_maps(model, candidates, rows, spans[image_index]) as captured:
                        output_model = model(**forward)
                        loss = bbox_loss(output_model.logits, forward["input_ids"], positions)
                    if set(captured) != set(candidates):
                        raise ValueError("missing cached candidate attention maps")
                    maps = captured
                else:
                    with torch.enable_grad(), capture_reference_gradient(model, rows, spans[image_index], scores, maps) as layers:
                        output_model = model(**forward)
                        loss = bbox_loss(output_model.logits, forward["input_ids"], positions)
                        loss.backward()
                    if sorted(scores) != list(range(layers)) or sorted(maps) != list(range(layers)):
                        raise ValueError("missing reference attention map or gradient")
                    gradients = torch.stack([scores[layer] for layer in range(layers)]).numpy()[..., 0]
                    candidates = top_candidates(gradients, top_gradient)
                if not bool(torch.isfinite(loss)):
                    raise ValueError("non-finite bbox loss")
                if baseline is not None:
                    actual = output_model.logits[0, rows].detach().float().cpu()
                    torch.testing.assert_close(actual, baseline, atol=0.002, rtol=0.002)
                occupancy = normalized_box_occupancy(reference_box, height, width)
                items, masses, saved_maps = [], [], []
                for head in candidates:
                    values = (maps[head] if cached_candidates is not None else maps[head[0]][head[1]]).mean(axis=0).reshape(height, width)
                    mass = float(values.sum())
                    entropy = normalized_entropy(values)
                    fiou, component_area = retained_mass_peak_component_fiou(values, occupancy)
                    items.append(dict(head=head_name(head), layer=head[0], query_head=head[1],
                                      gradient_absolute=float(gradients[head]), **{f"{role}_visual_mass": mass},
                                      normalized_entropy=entropy, support50_fiou=fiou,
                                      support50_component_area=component_area))
                    if iou_threshold is not None:
                        items[-1].update(dominant_mass_component(values, occupancy))
                        saved_maps.append(values)
                    masses.append(mass)
                mass_floor = float(np.quantile(masses, float(spec["visual_mass_quantile"])))
                eligible = [item for item in items if item[f"{role}_visual_mass"] >= mass_floor and item["normalized_entropy"] is not None]
                for item in eligible:
                    item["spatial_score"] = float(1 - item["normalized_entropy"] + float(spec["fiou_weight"]) * item["support50_fiou"])
                eligible.sort(key=lambda item: (-item["spatial_score"], -item["gradient_absolute"], item["layer"], item["query_head"]))
                chosen = eligible[:top_per_sample]
                legacy_chosen = list(chosen)
                if iou_threshold is not None:
                    chosen = choose_iou_heads(items, role, mass_floor, top_per_sample, iou_threshold)
                    cache_dir = output / "attention_maps"
                    cache_dir.mkdir(exist_ok=True)
                    np.savez_compressed(cache_dir / f"sample_{index:06d}.npz", heads=np.asarray(candidates),
                                        attention=np.asarray(saved_maps), occupancy=occupancy)
                    for item in legacy_chosen:
                        legacy_frequency[(item["layer"], item["query_head"])] += 1
                elif len(chosen) < top_per_sample:
                    raise ValueError("visual-mass gate left fewer than spatial_top_m candidates")
                name = dataset_name(runner.dataset, index)
                by_dataset[name]  # Keep zero-selection datasets in the denominator and figures.
                for item in chosen:
                    head = (item["layer"], item["query_head"])
                    frequency[head] += 1
                    by_dataset[name][head] += 1
                all_records.append(dict(dataset_index=index, sample_id=sample["id"], dataset=name,
                                        role=role, bbox_token_ce=float(loss.detach()), token_grid=[height, width],
                                        visual_token_count=height * width, bbox_prediction_rows=list(map(int, rows)),
                                        sequence_tokens=int(forward["input_ids"].shape[1]),
                                        image_path=sample["image_paths"][image_index], gt_box_normalized=reference_box,
                                        legacy_selected_heads=[item["head"] for item in legacy_chosen] if iou_threshold is not None else None,
                                        gradient_candidates=items, visual_mass_floor=mass_floor,
                                        selected_heads=[item["head"] for item in chosen]))
                del output_model, loss, forward, encoded, scores, maps
                if (order + 1) % 10 == 0 or order == 0:
                    publish(output / "records.json", dict(schema=SCHEMA, status="in_progress", records=all_records))
                    print(f"[{role.upper()}_SPATIAL_FREQUENCY] {order + 1}/{len(valid_indices)}", flush=True)
        finally:
            for parameter, enabled in flags:
                parameter.requires_grad_(enabled)
        ranked = sorted(frequency.items(), key=lambda item: (-item[1], item[0]))
        selected = [head for head, _ in ranked[:top_k]]
        denominators = {"all": len(valid_indices)}
        denominators.update({name: sum(1 for index in valid_indices if dataset_name(runner.dataset, index) == name) for name in by_dataset})
        count_matrices, rate_matrices = {}, {}
        for name, values in {"all": frequency, **by_dataset}.items():
            matrix = np.zeros((36, 32), dtype=np.int64)
            for (layer, head), count in values.items():
                matrix[layer, head] = count
            count_matrices[name] = matrix.tolist()
            rate = matrix.astype(np.float64) / denominators[name]
            rate_matrices[name] = rate.tolist()
            frequency_plot(output / f"frequency_{name}.png", rate, selected,
                           f"{name}: {role} gradient-gated spatial selection frequency")
        publish(output / "summary.json", dict(schema=SCHEMA, status="completed", source=source,
            parameters=dict(role=role, gradient_top_m=top_gradient, spatial_top_m=top_per_sample,
                            visual_mass_quantile=float(spec["visual_mass_quantile"]), fiou_weight=float(spec["fiou_weight"]),
                            top_k=top_k, retained_attention_mass=0.5, invalid_gt_policy=policy, **selection_details),
            source_samples=len(source["selected_indices"]), analyzed_samples=len(all_records),
            excluded_invalid_gt=excluded, selected_heads=[head_name(head) for head in selected],
            checkpoint=checkpoint, smoke_samples_per_dataset=args.samples_per_dataset, seed=seed,
            bbox_token_ce_mean=float(np.mean([row["bbox_token_ce"] for row in all_records])),
            first_sample_forward_parity="passed", code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            ranking=[dict(head=head_name(head), frequency=count) for head, count in ranked],
            frequency_denominators=denominators, frequency_count_matrices=count_matrices,
            frequency_rate_matrices=rate_matrices,
            selected_count_histogram=dict(sorted(Counter(len(row["selected_heads"]) for row in all_records).items())),
            legacy_same_forward_ranking=[dict(head=head_name(head), frequency=count)
                for head, count in sorted(legacy_frequency.items(), key=lambda item: (-item[1], item[0]))],
            claim_boundary="selection diagnostic only; requires independent causal ablation"))
        publish(output / "records.json", dict(schema=SCHEMA, status="completed", records=all_records))
    except BaseException as error:
        publish(output / "failure.json", dict(schema=SCHEMA, status="failed", exception=type(error).__name__, reason=str(error)))
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
