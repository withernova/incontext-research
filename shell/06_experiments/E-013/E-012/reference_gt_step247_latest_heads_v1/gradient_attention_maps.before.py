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
    figure, axes = plt.subplots(2, 5, figsize=(22, 9), constrained_layout=True)
    for axis, attention, head in zip(axes.flat, maps, heads):
        axis.imshow(image)
        axis.imshow(attention, cmap="magma", alpha=0.58, interpolation="bilinear",
                    extent=(0, width, height, 0))
        x1, y1, x2, y2 = target_box
        axis.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, edgecolor="#00e5ff", linewidth=2))
        axis.set_title(f"L{head['layer']:02d}H{head['head']:02d}\n|A·dL/dA| rank {head['rank']}", fontsize=10)
        axis.set_axis_off()
    figure.suptitle(sample_label + " · mean over teacher-forced bbox prediction rows · cyan=annotation GT", fontsize=14)
    figure.savefig(path, dpi=160)
    plt.close(figure)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    args = parser.parse_args(argv)
    spec = runpy.run_path(args.config)["visualization_spec"]
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
