"""Render fixed reference-head maps for deterministic high/low-IoU eval examples."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path
import runpy
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from ..prompting.coordinates import normalized_to_pixel, parse_box
from ..attention_distillation.selected import parse_head
from .metrics import normalized_box_occupancy

SCHEMA = "iploc-szy.eval-stratified-reference-maps/v1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def checked_json(path: Any, expected_sha256: str):
    path = Path(path).resolve()
    if sha256(path) != str(expected_sha256):
        raise ValueError(f"SHA-256 mismatch: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def read_predictions(path: Any, expected_sha256: str):
    path = Path(path).resolve()
    if sha256(path) != str(expected_sha256):
        raise ValueError(f"SHA-256 mismatch: {path}")
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    indices = [int(row["dataset_index"]) for row in rows]
    if not rows or len(indices) != len(set(indices)):
        raise ValueError("predictions must contain unique dataset indices")
    return rows


def select_iou_extremes(
    rows: Iterable[Mapping[str, Any]], per_tail: int, datasets: Sequence[str]
):
    if int(per_tail) < 1:
        raise ValueError("per_tail must be positive")
    groups = defaultdict(list)
    for row in rows:
        dataset = str(row["dataset"])
        iou = float(row["iou"])
        if dataset in datasets:
            if not np.isfinite(iou) or not 0.0 <= iou <= 1.0:
                raise ValueError("prediction IoU must be finite and within [0,1]")
            groups[dataset].append(dict(row))
    selected = []
    for dataset in datasets:
        candidates = groups[dataset]
        if len(candidates) < 2 * per_tail:
            raise ValueError(f"not enough predictions for both {dataset} tails")
        low = sorted(candidates, key=lambda row: (float(row["iou"]), int(row["dataset_index"])))[:per_tail]
        low_indices = {int(row["dataset_index"]) for row in low}
        high = [
            row for row in sorted(
                candidates, key=lambda row: (-float(row["iou"]), int(row["dataset_index"]))
            )
            if int(row["dataset_index"]) not in low_indices
        ][:per_tail]
        if len(high) != per_tail:
            raise ValueError(f"overlapping high/low tails for {dataset}")
        selected.extend(dict(row, stratum="low_iou") for row in low)
        selected.extend(dict(row, stratum="high_iou") for row in high)
    return selected


def distribution_metrics(distribution: np.ndarray, raw: np.ndarray, occupancy: np.ndarray):
    area = float(occupancy.mean())
    conditional = float((distribution * occupancy).sum())
    return {
        "reference_span_mass": float(raw.sum()),
        "conditional_gt_mass": conditional,
        "gt_area_fraction": area,
        "gt_enrichment": conditional / area,
        "pointing_token_overlaps_gt": bool(occupancy.flat[int(distribution.argmax())] > 0),
    }


def equal_head_ensemble(raw_maps: Sequence[np.ndarray]):
    if not raw_maps:
        raise ValueError("cannot ensemble an empty head set")
    normalized = []
    for raw in raw_maps:
        mass = float(raw.sum())
        if not np.isfinite(raw).all() or mass <= 0:
            raise ValueError("head map must be finite with positive reference mass")
        normalized.append(raw / mass)
    return np.stack(normalized).mean(0)


@contextmanager
def capture_selected_attention(model, heads, rows, full_span):
    """Capture only selected post-softmax attention rows to avoid all-head tensors."""
    import torch
    from transformers.models.qwen3_vl import modeling_qwen3_vl as implementation

    original = implementation.eager_attention_forward
    selected = set(heads)
    captured = {}
    key_start, key_stop = map(int, full_span)

    def intercepted(module, query, key, value, attention_mask, scaling, dropout=0.0, **kwargs):
        output, attention = original(
            module, query, key, value, attention_mask, scaling, dropout, **kwargs
        )
        if module.__class__.__name__ == "Qwen3VLTextAttention":
            layer = int(module.layer_idx)
            for head in sorted(item for item in selected if item[0] == layer):
                captured[head] = (
                    attention[0, head[1], rows, key_start:key_stop]
                    .detach().float().cpu().numpy()
                )
        return output, attention

    implementation.eager_attention_forward = intercepted
    try:
        yield captured
    finally:
        implementation.eager_attention_forward = original


def render(path, image_path, target_box, maps, labels, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from PIL import Image

    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    columns = min(5, len(maps))
    rows = (len(maps) + columns - 1) // columns
    figure, axes = plt.subplots(rows, columns, figsize=(4.5 * columns, 4.7 * rows), constrained_layout=True)
    axes = np.asarray(axes).reshape(-1)
    vmax = max(float(value.max()) for value in maps)
    rendered = None
    for axis in axes:
        axis.set_axis_off()
    for axis, values, label in zip(axes, maps, labels):
        axis.imshow(image)
        rendered = axis.imshow(
            values, cmap="magma", alpha=0.58, interpolation="bilinear",
            extent=(0, width, height, 0), vmin=0.0, vmax=vmax,
        )
        x1, y1, x2, y2 = target_box
        axis.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1,
                                 fill=False, edgecolor="#00e5ff", linewidth=2))
        axis.set_title(label, fontsize=9)
    if rendered is not None:
        figure.colorbar(rendered, ax=list(axes), shrink=0.65, label="P(key | reference span)")
    figure.suptitle(title + " · shared color scale · cyan=reference GT", fontsize=13)
    figure.savefig(path, dpi=160)
    plt.close(figure)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args(argv)
    spec = runpy.run_path(args.config)["visualization_spec"]

    selection = checked_json(spec["selection_summary"], spec["selection_summary_sha256"])
    if selection.get("status") != "completed" or selection.get("parameters", {}).get("role") != "reference":
        raise ValueError("selection summary must be completed for role=reference")
    reference_heads = tuple(parse_head(value) for value in selection["selected_heads"][:10])
    if len(reference_heads) != 10 or len(set(reference_heads)) != 10:
        raise ValueError("reference selection must provide ten unique heads")

    metrics = checked_json(spec["eval_metrics"], spec["eval_metrics_sha256"])
    predictions = read_predictions(spec["eval_predictions"], spec["eval_predictions_sha256"])
    manifest = Path(spec["eval_manifest"]).resolve()
    if sha256(manifest) != spec["eval_manifest_sha256"]:
        raise ValueError("evaluation manifest SHA-256 mismatch")
    checkpoint = Path(spec["checkpoint"]).resolve()
    if metrics.get("status") != "completed":
        raise ValueError("evaluation metrics are incomplete")
    if Path(metrics["checkpoint"]).resolve() != checkpoint:
        raise ValueError("visualization checkpoint differs from evaluation checkpoint")
    if int(metrics["evaluated_samples"]) != len(predictions):
        raise ValueError("evaluation metrics/prediction count mismatch")
    selected = select_iou_extremes(
        predictions, int(spec["samples_per_tail"]), tuple(spec["datasets"])
    )
    plan = {
        "schema": SCHEMA,
        "status": "validated" if args.check_only else "planned",
        "checkpoint": str(checkpoint),
        "selection_summary": str(Path(spec["selection_summary"]).resolve()),
        "eval_metrics": str(Path(spec["eval_metrics"]).resolve()),
        "eval_predictions": str(Path(spec["eval_predictions"]).resolve()),
        "eval_manifest": str(manifest),
        "eval_manifest_sha256": spec["eval_manifest_sha256"],
        "reference_heads": [f"L{layer:02d}H{head:02d}" for layer, head in reference_heads],
        "selected_samples": selected,
        "attention_edge": "teacher-forced query bbox p-1 rows -> reference image tokens",
        "normalization": "each head conditioned on its reference-span mass; shared scale per figure",
        "replay_precision": spec["replay_precision"],
        "max_sequence_tokens": int(spec["max_sequence_tokens"]),
        "claim_boundary": "descriptive visualization only; eval IoU strata do not establish attention causality",
    }
    if args.check_only:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0

    output = Path(spec["output_dir"]).resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite: {output}")
    output.mkdir(parents=True)
    (output / "resolved_plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    import torch
    from PIL import Image
    from ..config import Config
    from .bbox_gradient import publish
    from .head_circuit import build_context, dataset_name
    from .probes import temporary_eager_attention

    config = Config.fromfile(spec["screen_config"])
    config["checkpoint_path"] = str(checkpoint)
    config["work_dir"] = str(output)
    config["screen_dataloader"]["dataset"]["ann_file"] = spec["eval_manifest"]
    config["screen_dataloader"]["collator"]["vision_max_patch_tokens"] = int(spec["vision_max_patch_tokens"])
    config["head_screening"]["probe"]["samples"] = len(selected)
    config["head_screening"]["probe"]["max_sequence_tokens"] = int(spec["max_sequence_tokens"])
    dataset, probe, checkpoint_record, wrapper, runner = build_context(config)
    model = wrapper.model.eval().requires_grad_(False)
    records = []
    try:
        for order, chosen in enumerate(selected, start=1):
            index = int(chosen["dataset_index"])
            if index >= len(dataset) or dataset_name(dataset, index) != chosen["dataset"]:
                raise ValueError("evaluation prediction no longer matches manifest row")
            sample, encoded, metadata, positions, rows, spans = probe.encode_sample(runner, index)
            if str(sample["id"]) != str(chosen["id"]):
                raise ValueError("evaluation prediction sample id mismatch")
            grid = metadata["image_grid_thw"][0]
            merge = int(model.config.vision_config.spatial_merge_size)
            height, width = int(grid[1]) // merge, int(grid[2]) // merge
            start, stop = spans[0]
            if stop - start != height * width:
                raise ValueError("reference span/grid mismatch")
            forward = {key: value.to(wrapper.input_device) for key, value in encoded.items()}
            forward.update(use_cache=False, output_attentions=False, return_dict=True, logits_to_keep=1)
            with torch.inference_mode(), temporary_eager_attention(model), capture_selected_attention(
                model, reference_heads, rows, (start, stop)
            ) as captured:
                model(**forward)
            if set(captured) != set(reference_heads):
                raise ValueError("missing selected reference attention maps")
            occupancy = normalized_box_occupancy(
                parse_box(sample["reference_answers"][0]), height, width
            )
            raw_maps, distributions, head_metrics = [], [], {}
            for head in reference_heads:
                raw = captured[head].mean(0).reshape(height, width)
                mass = float(raw.sum())
                if not np.isfinite(raw).all() or mass <= 0:
                    raise ValueError("captured head has invalid reference attention")
                distribution = raw / mass
                label = f"L{head[0]:02d}H{head[1]:02d}"
                raw_maps.append(raw)
                distributions.append(distribution)
                head_metrics[label] = distribution_metrics(distribution, raw, occupancy)
            group_maps = {
                "reference_top3": equal_head_ensemble(raw_maps[:3]),
                "reference_top10": equal_head_ensemble(raw_maps),
            }
            group_metrics = {
                name: distribution_metrics(values, np.stack(raw_maps[:3] if name.endswith("top3") else raw_maps).mean(0), occupancy)
                for name, values in group_maps.items()
            }
            image_path = sample["image_paths"][0]
            with Image.open(image_path) as image:
                image_size = image.size
            target = parse_box(sample["reference_answers"][0])
            target_pixels = normalized_to_pixel(target, image_size, 1000)
            stem = f"{chosen['dataset']}_{chosen['stratum']}_idx{index:04d}"
            head_labels = [
                f"{name}\nGT={head_metrics[name]['conditional_gt_mass']:.3f}; "
                f"enr={head_metrics[name]['gt_enrichment']:.1f}x; "
                f"Rmass={head_metrics[name]['reference_span_mass']:.3f}"
                for name in head_metrics
            ]
            title = (
                f"{chosen['dataset']} idx={index} {chosen['stratum']} eval-IoU={float(chosen['iou']):.3f}"
                " | bbox p-1 -> REFERENCE"
            )
            render(output / f"{stem}_heads.png", image_path, target_pixels,
                   distributions, head_labels, title)
            group_labels = [
                f"{name}\nGT={group_metrics[name]['conditional_gt_mass']:.3f}; "
                f"enr={group_metrics[name]['gt_enrichment']:.1f}x"
                for name in group_maps
            ]
            render(output / f"{stem}_ensembles.png", image_path, target_pixels,
                   list(group_maps.values()), group_labels, title)
            np.savez_compressed(
                output / f"{stem}_raw_maps.npz", occupancy=occupancy,
                **{name: value for name, value in zip(head_metrics, raw_maps)}, **group_maps,
            )
            records.append({
                **chosen,
                "sample_id": sample["id"],
                "reference_image": image_path,
                "reference_gt_normalized": target,
                "reference_grid_hw": [height, width],
                "sequence_tokens": int(encoded["input_ids"].shape[1]),
                "bbox_prediction_rows": rows,
                "heads": head_metrics,
                "groups": group_metrics,
                "figures": [f"{stem}_heads.png", f"{stem}_ensembles.png"],
                "raw_maps": f"{stem}_raw_maps.npz",
            })
            publish(output / "records.json", {"schema": SCHEMA, "status": "in_progress", "records": records})
            print(f"[REFERENCE_EVAL_VIZ] {order}/{len(selected)} {stem}", flush=True)
        publish(output / "records.json", {"schema": SCHEMA, "status": "completed", "records": records})
        publish(output / "summary.json", {
            "schema": SCHEMA, "status": "completed", "samples": len(records),
            "figures": sum(len(row["figures"]) for row in records),
            "checkpoint": checkpoint_record, "reference_heads": plan["reference_heads"],
            "selected_samples": selected, "claim_boundary": plan["claim_boundary"],
        })
    except BaseException as error:
        publish(output / "failure.json", {
            "schema": SCHEMA, "status": "failed",
            "exception": type(error).__name__, "reason": str(error),
        })
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
