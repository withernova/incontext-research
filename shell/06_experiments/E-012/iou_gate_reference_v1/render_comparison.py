"""Render fixed first-two-per-dataset samples from the exact cached reference maps."""
import argparse
from collections import Counter
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from PIL import Image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("result_dir", type=Path)
    args = parser.parse_args()
    root = args.result_dir
    rows = json.loads((root / "records.json").read_text())["records"]
    out = root / "visualizations"
    out.mkdir(exist_ok=True)
    counts, figures = Counter(), []
    for row in rows:
        name = row["dataset"]
        if counts[name] >= 2:
            continue
        counts[name] += 1
        index = row["dataset_index"]
        with np.load(root / "attention_maps" / f"sample_{index:06d}.npz") as cache:
            maps = {f"L{int(layer):02d}H{int(head):02d}": values.copy()
                    for (layer, head), values in zip(cache["heads"], cache["attention"])}
        metrics = {item["head"]: item for item in row["gradient_candidates"]}
        with Image.open(row["image_path"]) as raw:
            photo = raw.convert("RGB")
        width, height = photo.size
        x1,y1,x2,y2 = row["gt_box_normalized"]
        box = (x1 * width / 1000, y1 * height / 1000,
               (x2-x1) * width / 1000, (y2-y1) * height / 1000)
        fig, axes = plt.subplots(2, 5, figsize=(20, 8), constrained_layout=True)
        for r, (title, heads) in enumerate((("Old rule", row["legacy_selected_heads"]),
                                            ("IoU >= 0.5", row["selected_heads"]))):
            for c, ax in enumerate(axes[r]):
                ax.imshow(photo)
                ax.add_patch(Rectangle(box[:2], box[2], box[3], fill=False, edgecolor="cyan", linewidth=2))
                if c < len(heads):
                    head = heads[c]
                    values = maps[head]
                    ax.imshow(values / values.max(), cmap="magma", alpha=.6, vmin=0, vmax=1,
                              interpolation="nearest", extent=(0, width, height, 0))
                    item = metrics[head]
                    ax.set_title(f"{title}: {head}\nDominant IoU={item['dominant_component_fiou']:.3f}; GT mass={item['gt_attention_mass']:.3f}", fontsize=10)
                else:
                    ax.set_title(f"{title}: no additional qualifying head", fontsize=10)
                ax.set_axis_off()
        fig.suptitle(f"{name} | index {index} | reference image | cyan=GT | each map scaled to its peak\n"
                     f"bbox prediction rows; frozen step1973; new rule selects {len(row['selected_heads'])}/10 heads; first 5 shown", fontsize=13)
        path = out / f"sample_{index:06d}_{name}_old_vs_iou050.png"
        fig.savefig(path, dpi=140)
        plt.close(fig)
        figures.append(dict(dataset_index=index, dataset=name, filename=path.name))
    (out / "index.json").write_text(json.dumps(figures,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(figures,ensure_ascii=False))


if __name__ == "__main__":
    main()
