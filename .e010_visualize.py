#!/usr/bin/env python3
import argparse, json
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def remap(path):
    return str(path).replace("/home/featurize/data/LaSOTTesting", "/defaultShare/archive/liuwenchu/data/LaSOTTesting")


def norm(array):
    array = np.asarray(array, float)
    return (array - array.min()) / (array.max() - array.min() + 1e-12)


def parse_head(name):
    return tuple(map(int, name.lstrip("L").replace("H", ":").split(":")))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--count", type=int, default=12)
    args = parser.parse_args()
    run = Path(args.run_dir)
    summary = json.loads((run / "analysis/summary.json").read_text())
    recs = json.loads((run / "records.json").read_text())["records"]
    source = json.loads(Path(args.manifest).read_text())
    held = set(summary["integrity"]["evaluation_groups"])
    heads = summary["roles"]["q_to_r"]["fixed_heads"]["5"]
    chosen = [record for record in recs if record["group"] in held]
    correct = [record for record in chosen if record["natural_iou"] is not None and record["natural_iou"] >= .5][:4]
    error = [record for record in chosen if record["natural_iou"] is None or record["natural_iou"] < .1][:4]
    selected = correct + error
    for record in chosen:
        if len(selected) >= args.count:
            break
        if record not in selected:
            selected.append(record)
    out = run / "visualizations/q_to_r_fixed_top5_heldout"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for record in selected:
        src = source[record["index"]]
        image = Image.open(remap(src["image_path"][0])).convert("RGB")
        box = list(map(float, json.loads(src["bbox"][0])))
        maps = np.load(record["artifact"])["q_to_r"].astype(float)
        fig, axes = plt.subplots(2, 3, figsize=(15, 9), constrained_layout=True)
        axes = axes.ravel()
        base = np.asarray(image)
        selected_maps = []
        for index, name in enumerate(heads):
            layer, head = parse_head(name)
            attention = maps[layer, head]
            selected_maps.append(attention)
            heat = plt.get_cmap("turbo")(norm(attention))[..., :3]
            heat = np.asarray(Image.fromarray(np.uint8(heat * 255)).resize(image.size, Image.Resampling.BILINEAR)) / 255
            axes[index].imshow(base)
            axes[index].imshow(heat, alpha=.58)
            axes[index].add_patch(plt.Rectangle((box[0], box[1]), box[2] - box[0], box[3] - box[1], fill=False, edgecolor="lime", linewidth=3))
            axes[index].set_title(name)
            axes[index].axis("off")
        aggregate = np.mean(selected_maps, axis=0)
        heat = plt.get_cmap("turbo")(norm(aggregate))[..., :3]
        heat = np.asarray(Image.fromarray(np.uint8(heat * 255)).resize(image.size, Image.Resampling.BILINEAR)) / 255
        axes[5].imshow(base)
        axes[5].imshow(heat, alpha=.58)
        axes[5].add_patch(plt.Rectangle((box[0], box[1]), box[2] - box[0], box[3] - box[1], fill=False, edgecolor="lime", linewidth=3))
        axes[5].set_title("Top-5 mean")
        axes[5].axis("off")
        outcome = "correct" if record in correct else ("error" if record in error else "other")
        fig.suptitle(f"Natural generated bbox rows -> reference image | held-out | {record['group']} | {outcome} | IoU={record['natural_iou']}", fontsize=13)
        path = out / f"sample_{record['index']:04d}_{outcome}_{record['group']}.png"
        fig.savefig(path, dpi=140)
        plt.close(fig)
        rows.append({"index": record["index"], "group": record["group"], "outcome": outcome, "natural_iou": record["natural_iou"], "heads": heads, "path": str(path)})
    (out / "manifest.json").write_text(json.dumps({"definition": "natural generated query bbox p-1 rows -> reference image tokens", "split": "E010 held-out evaluation groups only", "green_box": "reference GT, evaluation overlay only; not used for head discovery", "records": rows}, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"rendered": len(rows), "output": str(out), "heads": heads}))


if __name__ == "__main__":
    main()
