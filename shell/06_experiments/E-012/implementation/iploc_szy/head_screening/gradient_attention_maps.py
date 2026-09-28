"""Render R-001 gradient-ranked heads' teacher-forced bbox-row -> query-image attention."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import runpy


SCHEMA = "iploc-szy.gradient-head-attention-maps/v1"


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_inputs(source_dir, top_k):
    root = Path(source_dir).resolve()
    frozen_path, summary_path = root / "frozen_input.json", root / "summary.json"
    if not frozen_path.is_file() or not summary_path.is_file():
        raise ValueError("source must contain R-001 frozen_input.json and summary.json")
    frozen, summary = json.loads(frozen_path.read_text()), json.loads(summary_path.read_text())
    if summary.get("schema") != "iploc-szy.bbox-gradient-ranking/v1" or summary.get("status") != "completed":
        raise ValueError("source summary is not a completed bbox-gradient ranking")
    ranking = summary.get("ranking", [])
    if len(ranking) < top_k or [row.get("rank") for row in ranking] != list(range(1, len(ranking) + 1)):
        raise ValueError("ranking is incomplete or unordered")
    heads = ranking[:top_k]
    config = frozen.get("config")
    if not isinstance(config, dict) or Path(config.get("work_dir", "")).resolve() != root:
        raise ValueError("frozen configuration does not identify this source")
    manifest = Path(config["screen_dataloader"]["dataset"]["ann_file"])
    expected = frozen.get("manifests_sha256", {}).get(str(manifest))
    if not expected or digest(manifest) != expected:
        raise ValueError("R-001 manifest hash mismatch")
    return dict(root=str(root), config=config, selected_indices=frozen["selected_indices"], heads=heads,
                frozen_sha256=digest(frozen_path), summary_sha256=digest(summary_path),
                manifest=str(manifest), manifest_sha256=expected)


def choose_indices(dataset, allowed, per_dataset):
    from .head_circuit import dataset_name
    counts, result = {str(k): 0 for k in per_dataset}, []
    for index in sorted(map(int, allowed)):
        name = dataset_name(dataset, index)
        if name in counts and counts[name] < int(per_dataset[name]):
            result.append(index)
            counts[name] += 1
    if counts != {str(k): int(v) for k, v in per_dataset.items()}:
        raise ValueError(f"cannot meet per-dataset visualization quota: {counts}")
    return result, counts


def render_sample(path, image_path, target_box, maps, heads, width, height, sample_label):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from PIL import Image

    image = Image.open(image_path).convert("RGB")
    import numpy as np
    columns = min(5, len(maps))
    rows = (len(maps) + columns - 1) // columns
    figure, axes = plt.subplots(rows, columns, figsize=(4.4 * columns, 4.8 * rows), constrained_layout=True)
    for axis in np.asarray(axes).reshape(-1):
        axis.set_axis_off()
    for axis, attention, head in zip(np.asarray(axes).reshape(-1), maps, heads):
        axis.imshow(image)
        axis.imshow(attention, cmap="magma", alpha=0.58, interpolation="bilinear",
                    extent=(0, width, height, 0))
        x1, y1, x2, y2 = target_box
        axis.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, edgecolor="#00e5ff", linewidth=2))
        title = head.get("label")
        if title is None:
            title = f"L{head['layer']:02d}H{head['head']:02d}\n|A·dL/dA| rank {head['rank']}"
        axis.set_title(title, fontsize=10)
        axis.set_axis_off()
    figure.suptitle(sample_label + " · mean over teacher-forced bbox prediction rows · cyan=annotation GT", fontsize=14)
    figure.savefig(path, dpi=160)
    plt.close(figure)


def selection_reference_maps(spec, args):
    """Audit selected reference heads using the existing E009 teacher aggregation."""
    import copy
    from collections import defaultdict
    import numpy as np
    import torch
    from PIL import Image
    from ..attention_distillation.artifacts import ensemble_teacher, sample_geometries
    from ..attention_distillation.selected import parse_head
    from ..prompting.coordinates import normalized_to_pixel, parse_box
    from .gradient_gated_spatial_frequency import capture_candidate_maps, retained_mass_peak_component_fiou
    from .head_circuit import build_context, dataset_name
    from .bbox_gradient import publish

    selection_path = Path(args.selection_summary).resolve()
    selection = json.loads(selection_path.read_text())
    if selection.get("status") != "completed" or selection["parameters"].get("role") != "reference":
        raise ValueError("require a completed reference selection summary")
    if digest(selection["source"]["manifest"]) != selection["source"]["manifest_sha256"]:
        raise ValueError("selection manifest changed")
    config = copy.deepcopy(selection["source"]["config"])
    if args.checkpoint:
        config["checkpoint_path"] = str(Path(args.checkpoint).resolve())
    config["model"]["device_map"] = "balanced"
    output = Path(args.output_dir).resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite: {output}")
    config["work_dir"] = str(output)
    new_heads = [parse_head(value) for value in selection["selected_heads"]]
    legacy = runpy.run_path(args.reference_baselines_config)["runtime"]["runner"]["auxiliary_loss"]
    groups = dict(new_reference_top3=new_heads[:3], new_reference_top10=new_heads,
                  old_teacher_top3=[parse_head(v) for v in legacy["teacher_heads"]],
                  old_query_top5=[parse_head(v) for v in legacy["student_heads"]])
    heads = sorted(set(head for group in groups.values() for head in group))
    excluded = selection.get("excluded_invalid_gt", selection.get("excluded_invalid_reference_gt", []))
    excluded_indices = {int(row["dataset_index"]) for row in excluded}
    indices = [int(i) for i in selection["source"]["selected_indices"] if int(i) not in excluded_indices]
    output.mkdir(parents=True)
    publish(output / "resolved_plan.json", dict(status="planned", source_selection=str(selection_path),
        source_selection_sha256=digest(selection_path), config=config, selected_indices=indices,
        head_groups=groups, code_sha256=digest(__file__), baseline_config_sha256=digest(args.reference_baselines_config),
        attention_edge="teacher-forced bbox prediction rows p-1 -> reference image key tokens",
        group_aggregation="E009 ensemble_teacher: normalize each head within reference, then equal-weight mean"))

    def metrics(raw, distribution, occupancy):
        conditional = float((distribution * occupancy).sum())
        area = float(occupancy.mean())
        fiou, component_area = retained_mass_peak_component_fiou(distribution, occupancy)
        return dict(reference_span_mass=float(raw.sum()), reference_gt_mass=float((raw * occupancy).sum()),
                    conditional_gt_mass=conditional, gt_area_fraction=area,
                    gt_enrichment=conditional / area, pointing_token_overlaps_gt=bool(occupancy.flat[int(distribution.argmax())] > 0),
                    support50_fiou=fiou, support50_component_tokens=component_area)

    try:
        dataset, probe, checkpoint, wrapper, runner = build_context(config)
        if not args.checkpoint and checkpoint["adapter_weights_sha256"] != selection["checkpoint"]["adapter_weights_sha256"]:
            raise ValueError("visualization checkpoint differs from selection checkpoint")
        model = wrapper.model.eval().requires_grad_(False)
        visualize, _ = choose_indices(dataset, indices, spec["samples_per_dataset"])
        records = []
        for order, index in enumerate(indices):
            sample, encoded, metadata, positions, rows, spans = probe.encode_sample(runner, index)
            geometry = sample_geometries(encoded["input_ids"], [metadata],
                image_token_id=int(model.config.image_token_id),
                spatial_merge_size=int(model.config.vision_config.spatial_merge_size))[0]
            if tuple(rows) != geometry.prediction_rows or tuple(spans[0]) != geometry.reference_span[:2]:
                raise ValueError("E009 teacher geometry differs from screening bbox rows/reference span")
            forward = {key: value.to(wrapper.input_device) for key, value in encoded.items()}
            forward.update(use_cache=False, output_attentions=False, return_dict=True, logits_to_keep=1)
            with torch.inference_mode(), capture_candidate_maps(model, heads, rows, (0, int(encoded["input_ids"].shape[1]))) as captured:
                model(**forward)
            if set(captured) != set(heads):
                raise ValueError("missing selected head map")
            start, stop, height, width = geometry.reference_span
            occupancy = geometry.reference_occupancy
            head_maps, head_metrics = {}, {}
            selected = {head: [torch.from_numpy(captured[head])] for head in heads}
            for head in heads:
                raw = captured[head][:, start:stop].mean(0).reshape(height, width)
                if not np.isfinite(raw).all() or float(raw.sum()) <= 0:
                    raise ValueError("invalid reference head map")
                label = f"L{head[0]:02d}H{head[1]:02d}"
                head_maps[label] = raw
                head_metrics[label] = metrics(raw, raw / raw.sum(), occupancy)
            group_maps, group_metrics = {}, {}
            for name, group in groups.items():
                values = ensemble_teacher(selected, 0, geometry, group)
                group_maps[name] = values["distribution"]
                group_metrics[name] = metrics(values["raw_reference_map"], values["distribution"], occupancy)
            item = dict(dataset_index=index, sample_id=sample["id"], dataset=dataset_name(dataset, index),
                        bbox_token_positions=positions, bbox_prediction_rows=rows,
                        reference_span=list(geometry.reference_span), reference_grid_hw=[height, width],
                        heads=head_metrics, groups=group_metrics)
            if index in visualize:
                image_path = sample["image_paths"][0]
                target = parse_box(sample["reference_answers"][0])
                with Image.open(image_path) as image:
                    image_size = image.size
                pixels = normalized_to_pixel(target, image_size, 1000)
                caption = f"{item['dataset']} index {index} | bbox p-1 -> REFERENCE image"
                labels = [f"L{h[0]:02d}H{h[1]:02d}" for h in new_heads]
                panel_heads = [dict(label=f"{name} (frequency rank {i+1})\nGT fraction={head_metrics[name]['conditional_gt_mass']:.3f}; enrichment={head_metrics[name]['gt_enrichment']:.1f}x\nreference mass={head_metrics[name]['reference_span_mass']:.4f}") for i, name in enumerate(labels)]
                filename = f"sample_{index:06d}_{item['dataset']}_new_heads.png"
                render_sample(output / filename, image_path, pixels,
                    [head_maps[name] / head_maps[name].max() for name in labels], panel_heads, *image_size, caption)
                group_filename = f"sample_{index:06d}_{item['dataset']}_groups.png"
                panel_groups = [dict(label=f"{name}\nGT fraction={group_metrics[name]['conditional_gt_mass']:.3f}; enrichment={group_metrics[name]['gt_enrichment']:.1f}x\nreference mass={group_metrics[name]['reference_span_mass']:.4f}") for name in groups]
                render_sample(output / group_filename, image_path, pixels,
                    [group_maps[name] / group_maps[name].max() for name in groups], panel_groups, *image_size, caption)
                item.update(figures=[filename, group_filename], reference_image=image_path, reference_gt_normalized=target)
                np.savez_compressed(output / f"sample_{index:06d}_raw_maps.npz", occupancy=occupancy, **head_maps, **group_maps)
            records.append(item)
            del forward, encoded, captured, selected
            if (order + 1) % 50 == 0 or order == 0:
                publish(output / "records.json", dict(status="in_progress", records=records))
                print(f"[REFERENCE_GT_MAPS] {order + 1}/{len(indices)}", flush=True)
        aggregate = {}
        for scope in ("all", "LaSOT", "GOT10k", "TAO"):
            subset = [r for r in records if scope == "all" or r["dataset"] == scope]
            aggregate[scope] = {}
            for kind in ("heads", "groups"):
                aggregate[scope][kind] = {}
                for name in subset[0][kind]:
                    values = [r[kind][name] for r in subset]
                    aggregate[scope][kind][name] = {key: dict(mean=float(np.mean([v[key] for v in values])), median=float(np.median([v[key] for v in values]))) for key in values[0]}
                    aggregate[scope][kind][name]["majority_gt_rate"] = float(np.mean([v["conditional_gt_mass"] > .5 for v in values]))
                    aggregate[scope][kind][name]["samples"] = len(subset)
        publish(output / "records.json", dict(status="completed", records=records))
        publish(output / "summary.json", dict(schema=SCHEMA, status="completed", analyzed_samples=len(records),
            visualized_indices=visualize, figures=sum(len(r.get("figures", [])) for r in records),
            selection_summary=str(selection_path), selection_summary_sha256=digest(selection_path),
            selection_checkpoint=selection["checkpoint"], visualization_checkpoint=checkpoint,
            code_sha256=digest(__file__), head_groups=groups, aggregate=aggregate,
            claim_boundary="Descriptive reference-GT alignment; GT-informed selection and same eval population do not establish held-out validity, transfer effectiveness or causality."))
    except BaseException as error:
        publish(output / "failure.json", dict(status="failed", exception=type(error).__name__, reason=str(error)))
        raise
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("--selection-summary")
    parser.add_argument("--checkpoint")
    parser.add_argument("--output-dir")
    parser.add_argument("--reference-baselines-config")
    args = parser.parse_args(argv)
    spec = runpy.run_path(args.config)["visualization_spec"]
    if args.selection_summary:
        if not args.output_dir or not args.reference_baselines_config:
            parser.error("--selection-summary requires --output-dir and --reference-baselines-config")
        return selection_reference_maps(spec, args)
    source = source_inputs(spec["source_run_dir"], int(spec.get("top_k", 10)))
    output = Path(spec["output_dir"])
    if output.exists():
        raise FileExistsError(f"refusing to overwrite: {output}")

    import numpy as np
    import torch
    from ..prompting.coordinates import normalized_to_pixel, parse_box
    from .bbox_gradient import attach_checkpoint
    from .head_circuit import build_context, dataset_name
    from .probes import temporary_eager_attention

    output.mkdir(parents=True)
    write_json(output / "source.json", dict(schema=SCHEMA, source=source, aggregation="mean_bbox_prediction_rows"))
    try:
        dataset, probe, checkpoint, wrapper, runner = build_context(source["config"])
        indices, counts = choose_indices(dataset, source["selected_indices"], spec["samples_per_dataset"])
        model = wrapper.model.eval().requires_grad_(False)
        records = []
        for order, index in enumerate(indices):
            sample, encoded, metadata, positions, rows, spans = probe.encode_sample(runner, index)
            forward = {key: value.to(wrapper.input_device) for key, value in encoded.items()}
            forward.update(use_cache=False, output_attentions=True, return_dict=True, logits_to_keep=0)
            with torch.inference_mode(), temporary_eager_attention(model):
                output_model = model(**forward)
            attentions = output_model.attentions
            if not attentions or len(attentions) != 36 or any(value is None for value in attentions):
                raise ValueError("model did not return all eager text attention maps")
            start, stop = spans[-1]
            grid = metadata["image_grid_thw"][-1]
            merge = int(model.config.vision_config.spatial_merge_size)
            grid_h, grid_w = int(grid[1]) // merge, int(grid[2]) // merge
            if stop - start != grid_h * grid_w:
                raise ValueError("query token span/grid mismatch")
            maps = []
            for head in source["heads"]:
                attention = attentions[int(head["layer"])][0, int(head["head"]), rows, start:stop]
                values = attention.float().mean(0).cpu().numpy().reshape(grid_h, grid_w)
                if not np.isfinite(values).all() or float(values.sum()) <= 0:
                    raise ValueError("invalid head attention map")
                maps.append(values / values.max())
            target_normalized = parse_box(sample["query_answer"])
            image_path = sample["image_paths"][-1]
            from PIL import Image
            with Image.open(image_path) as image:
                image_size = image.size
            target_pixels = normalized_to_pixel(target_normalized, image_size, 1000)
            if target_pixels is None:
                raise ValueError("cannot convert query annotation to pixels")
            filename = f"sample_{index:06d}_{dataset_name(dataset, index)}.png"
            render_sample(output / filename, image_path, target_pixels, maps, source["heads"],
                          image_size[0], image_size[1], f"{dataset_name(dataset, index)} · index {index}")
            records.append(dict(dataset_index=index, sample_id=sample["id"], dataset=dataset_name(dataset, index),
                                image_path=image_path, target_box_normalized=target_normalized,
                                target_box_pixels=target_pixels, query_grid_hw=[grid_h, grid_w],
                                bbox_prediction_rows=rows, figure=filename))
            print(f"[GRADIENT_MAP] {order + 1}/{len(indices)}", flush=True)
        write_json(output / "summary.json", dict(schema=SCHEMA, status="completed", samples=len(records),
                                                   samples_per_dataset=counts, heads=source["heads"], records=records))
    except BaseException as error:
        write_json(output / "failure.json", dict(schema=SCHEMA, status="failed", exception=type(error).__name__, reason=str(error)))
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
