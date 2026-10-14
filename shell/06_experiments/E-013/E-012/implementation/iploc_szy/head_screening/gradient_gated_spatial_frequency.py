"""R-001 gradient-gated spatial-frequency head selection; selection only, no causal claim."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import contextmanager
import hashlib
import json
import math
from pathlib import Path
import runpy

import numpy as np

from ..prompting.coordinates import parse_box
from .gradient_attention_maps import source_inputs
from .head_circuit import build_context, dataset_name
from .probes import temporary_eager_attention

SCHEMA = "iploc-szy.gradient-gated-spatial-frequency/v1"


def publish(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def head_name(head):
    return f"L{head[0]:02d}H{head[1]:02d}"


def normalized_entropy(values):
    total = float(values.sum())
    if not math.isfinite(total) or total <= 0:
        return None
    p = values / total
    entropy = float(-(p[p > 0] * np.log(p[p > 0])).sum())
    return entropy / math.log(values.size) if values.size > 1 else 0.0


def retained_mass_peak_component_fiou(values, occupancy, retained_mass=0.5):
    """IoU of the peak component in the minimal support carrying 50% attention mass."""
    total = float(values.sum())
    if not math.isfinite(total) or total <= 0:
        return 0.0, 0
    weights = values / total
    order = np.argsort(-weights.ravel(), kind="stable")
    count = int(np.searchsorted(np.cumsum(weights.ravel()[order]), retained_mass, side="left") + 1)
    mask = np.zeros(values.size, dtype=bool)
    mask[order[:count]] = True
    mask = mask.reshape(values.shape)
    start = tuple(map(int, np.unravel_index(int(values.argmax()), values.shape)))
    stack, component = [start], set()
    while stack:
        y, x = stack.pop()
        if (y, x) in component or not mask[y, x]:
            continue
        component.add((y, x))
        for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= yy < mask.shape[0] and 0 <= xx < mask.shape[1]:
                stack.append((yy, xx))
    support = np.zeros_like(mask, dtype=bool)
    for y, x in component:
        support[y, x] = True
    target = np.clip(np.asarray(occupancy, dtype=np.float64), 0.0, 1.0)
    intersection = float(target[support].sum())
    union = float(support.sum() + target.sum() - intersection)
    return (intersection / union if union else 0.0), len(component)


@contextmanager
def capture_candidate_maps(model, candidates, rows, span):
    """Capture only selected heads' attention slices after real Q/K softmax; do not modify output."""
    from transformers.models.qwen3_vl import modeling_qwen3_vl as implementation
    original, captured = implementation.eager_attention_forward, {}
    start, stop = span
    by_layer = defaultdict(list)
    for layer, head in candidates:
        by_layer[int(layer)].append(int(head))

    def intercepted(module, query, key, value, attention_mask, scaling, dropout=0.0, **kwargs):
        output, attention = original(module, query, key, value, attention_mask, scaling, dropout, **kwargs)
        if module.__class__.__name__ == "Qwen3VLTextAttention" and int(module.layer_idx) in by_layer:
            if query.shape[0] != 1 or dropout != 0:
                raise ValueError("frequency selector requires batch=1 eval attention")
            layer = int(module.layer_idx)
            for head in by_layer[layer]:
                if not 0 <= head < attention.shape[1]:
                    raise ValueError("candidate head outside runtime attention width")
                captured[(layer, head)] = attention[0, head, rows, start:stop].detach().float().cpu().numpy()
        return output, attention

    implementation.eager_attention_forward = intercepted
    try:
        with temporary_eager_attention(model):
            yield captured
    finally:
        implementation.eager_attention_forward = original


def source_records(root, expected_indices):
    path = Path(root) / "probe" / "records.json"
    raw = json.loads(path.read_text())
    rows = {int(row["dataset_index"]): row for row in raw.get("records", [])}
    if set(rows) != set(map(int, expected_indices)):
        raise ValueError("R-001 probe records do not exactly match frozen selected_indices")
    return rows, hashlib.sha256(path.read_bytes()).hexdigest()


def valid_target_indices(config, expected_indices, policy):
    """Resolve the spatial-score population without loading a model."""
    from ..registry import DATASETS
    dataset = DATASETS.build(config["screen_dataloader"]["dataset"])
    valid, excluded = [], []
    for index in sorted(map(int, expected_indices)):
        sample = dataset[index]
        box = parse_box(sample.get("query_answer"))
        reason = None
        if box is None:
            reason = "unparseable_query_answer"
        elif not (box[2] > box[0] and box[3] > box[1]):
            reason = "non_positive_normalized_box"
        if reason is None:
            valid.append(index)
        else:
            excluded.append(dict(dataset_index=index, sample_id=sample.get("id"),
                                 dataset=dataset_name(dataset, index), query_answer=sample.get("query_answer"), reason=reason))
    if excluded and policy != "exclude":
        raise ValueError(f"invalid GT samples require invalid_gt_policy=exclude: {excluded}")
    if not valid:
        raise ValueError("no samples have valid GT boxes")
    return valid, excluded


def candidate_heads(artifact, top_m, layers=36, width=32):
    with np.load(artifact) as payload:
        values = payload["absolute"].astype(np.float64)
    if values.shape != (layers, width) or not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("invalid R-001 per-sample absolute gradient artifact")
    order = sorted(np.ndindex(values.shape), key=lambda item: (-values[item], item[0], item[1]))[:top_m]
    return order, values


def frequency_plot(output, matrix, selected, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig, ax = plt.subplots(figsize=(15, 11), constrained_layout=True)
    image = ax.imshow(matrix, cmap="viridis", vmin=0, vmax=max(0.01, float(matrix.max())), aspect="auto")
    fig.colorbar(image, ax=ax, label="selection frequency (rate)")
    ax.set(xlabel="head", ylabel="layer", title=title, xticks=range(32), yticks=range(36))
    for layer, head in selected:
        ax.add_patch(Rectangle((head - .5, layer - .5), 1, 1, fill=False, edgecolor="#ff3b30", linewidth=2))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("--check-only", action="store_true", help="validate R-001 provenance and selection parameters without loading a model")
    args = parser.parse_args(argv)
    spec = runpy.run_path(args.config)["selection_spec"]
    source = source_inputs(spec["source_run_dir"], 10)
    output = Path(spec["output_dir"])
    if output.exists():
        raise FileExistsError(f"refusing to overwrite: {output}")
    top_gradient, top_per_sample, top_k = (int(spec[k]) for k in ("gradient_top_m", "spatial_top_m", "top_k"))
    if not 1 <= top_k <= top_per_sample <= top_gradient <= 1152:
        raise ValueError("require 1 <= top_k <= spatial_top_m <= gradient_top_m <= 1152")
    if not 0 <= float(spec["visual_mass_quantile"]) < 1 or float(spec["fiou_weight"]) < 0:
        raise ValueError("invalid mass quantile or fiou weight")
    records_source, probe_records_sha = source_records(source["root"], source["selected_indices"])
    policy = str(spec.get("invalid_gt_policy", "fail"))
    valid_indices, excluded = valid_target_indices(source["config"], source["selected_indices"], policy)
    if args.check_only:
        print(json.dumps(dict(schema=SCHEMA, status="validated", source_run_dir=source["root"],
                              source_frozen_sha256=source["frozen_sha256"], source_summary_sha256=source["summary_sha256"],
                              probe_records_sha256=probe_records_sha, source_samples=len(source["selected_indices"]), analyzed_samples=len(valid_indices),
                              excluded_invalid_gt=excluded), ensure_ascii=False))
        return 0
    output.mkdir(parents=True)
    publish(output / "resolved_plan.json", dict(schema=SCHEMA, status="planned", source=source,
        probe_records_sha256=probe_records_sha,
        parameters=dict(gradient_top_m=top_gradient, spatial_top_m=top_per_sample,
                        visual_mass_quantile=float(spec["visual_mass_quantile"]), fiou_weight=float(spec["fiou_weight"]), top_k=top_k,
                        retained_attention_mass=0.5, invalid_gt_policy=policy),
        analyzed_indices=valid_indices, excluded_invalid_gt=excluded,
        claim_boundary="selection diagnostic only; requires independent causal ablation"))
    try:
        dataset, probe, checkpoint, wrapper, runner = build_context(source["config"])
        from .metrics import normalized_box_occupancy
        import torch
        model = wrapper.model.eval().requires_grad_(False)
        all_records, frequency, by_dataset = [], Counter(), defaultdict(Counter)
        for order, index in enumerate(valid_indices):
            candidates, gradients = candidate_heads(records_source[index]["artifact"], top_gradient)
            sample, encoded, metadata, _, rows, spans = probe.encode_sample(runner, index)
            grid = metadata["image_grid_thw"][-1]
            merge = int(model.config.vision_config.spatial_merge_size)
            height, width = int(grid[1]) // merge, int(grid[2]) // merge
            if spans[-1][1] - spans[-1][0] != height * width:
                raise ValueError("query grid/token mismatch")
            target = parse_box(sample["query_answer"])
            if target is None:
                raise ValueError("missing normalized query annotation")
            forward = {key: value.to(wrapper.input_device) for key, value in encoded.items()}
            forward.update(use_cache=False, output_attentions=False, return_dict=True, logits_to_keep=0)
            with torch.inference_mode(), capture_candidate_maps(model, candidates, rows, spans[-1]) as captured:
                model(**forward)
            if set(captured) != set(candidates):
                raise ValueError("not every gradient candidate attention map was captured")
            items, masses = [], []
            target_mask = normalized_box_occupancy(target, height, width)
            for head in candidates:
                values = captured[head].mean(axis=0).reshape(height, width)
                mass = float(values.sum())
                entropy = normalized_entropy(values)
                fiou, component_area = retained_mass_peak_component_fiou(values, target_mask)
                items.append(dict(head=head_name(head), layer=head[0], query_head=head[1],
                                  gradient_absolute=float(gradients[head]), query_visual_mass=mass,
                                  normalized_entropy=entropy, support50_fiou=fiou,
                                  support50_component_area=component_area))
                masses.append(mass)
            mass_floor = float(np.quantile(masses, float(spec["visual_mass_quantile"])))
            eligible = [item for item in items if item["query_visual_mass"] >= mass_floor and item["normalized_entropy"] is not None]
            for item in eligible:
                item["spatial_score"] = float(1 - item["normalized_entropy"] + float(spec["fiou_weight"]) * item["support50_fiou"])
            eligible.sort(key=lambda item: (-item["spatial_score"], -item["gradient_absolute"], item["layer"], item["query_head"]))
            chosen = eligible[:top_per_sample]
            if len(chosen) < top_per_sample:
                raise ValueError("visual-mass gate left fewer than spatial_top_m candidates")
            dataset = dataset_name(runner.dataset, index)
            for item in chosen:
                frequency[(item["layer"], item["query_head"])] += 1
                by_dataset[dataset][(item["layer"], item["query_head"])] += 1
            all_records.append(dict(dataset_index=index, sample_id=sample["id"], dataset=dataset,
                                    gradient_candidates=items, visual_mass_floor=mass_floor,
                                    selected_heads=[item["head"] for item in chosen]))
            if (order + 1) % 10 == 0 or order == 0:
                publish(output / "records.json", dict(schema=SCHEMA, status="in_progress", records=all_records))
                print(f"[SPATIAL_FREQUENCY] {order + 1}/{len(valid_indices)}", flush=True)
        ranked = sorted(((head, count) for head, count in frequency.items()), key=lambda item: (-item[1], item[0]))
        selected = [head for head, _ in ranked[:top_k]]
        count_matrices, rate_matrices = {}, {}
        denominators = {"all": len(valid_indices)}
        denominators.update({name: sum(1 for index in valid_indices if dataset_name(runner.dataset, index) == name) for name in by_dataset})
        for name, values in {"all": frequency, **by_dataset}.items():
            matrix = np.zeros((36, 32), dtype=np.int64)
            for (layer, head), count in values.items(): matrix[layer, head] = count
            count_matrices[name] = matrix.tolist()
            rate = matrix.astype(np.float64) / denominators[name]
            rate_matrices[name] = rate.tolist()
            frequency_plot(output / f"frequency_{name}.png", rate, selected, f"{name}: gradient-gated spatial selection frequency")
        payload = dict(schema=SCHEMA, status="completed", source=source, probe_records_sha256=probe_records_sha,
                       parameters=dict(gradient_top_m=top_gradient, spatial_top_m=top_per_sample,
                                       visual_mass_quantile=float(spec["visual_mass_quantile"]), fiou_weight=float(spec["fiou_weight"]), top_k=top_k,
                                       retained_attention_mass=0.5, invalid_gt_policy=policy),
                       selected_heads=[head_name(head) for head in selected], ranking=[dict(head=head_name(head), frequency=count) for head, count in ranked],
                       source_samples=len(source["selected_indices"]), analyzed_samples=len(all_records), excluded_invalid_gt=excluded,
                       frequency_denominators=denominators, frequency_count_matrices=count_matrices,
                       frequency_rate_matrices=rate_matrices, claim_boundary="selection diagnostic only; requires independent causal ablation")
        publish(output / "summary.json", payload)
        publish(output / "records.json", dict(schema=SCHEMA, status="completed", records=all_records))
    except BaseException as error:
        publish(output / "failure.json", dict(schema=SCHEMA, status="failed", exception=type(error).__name__, reason=str(error)))
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
