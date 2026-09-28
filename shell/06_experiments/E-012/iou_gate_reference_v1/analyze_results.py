"""Audit a completed reference IoU-gated run using its explicit source records."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import statistics
import numpy as np


def distribution(values):
    if not values:
        return dict(n=0, mean=None, median=None, minimum=None, maximum=None)
    return dict(n=len(values), mean=statistics.mean(values), median=statistics.median(values),
                minimum=min(values), maximum=max(values))


def overlap(a, b):
    a, b = set(a), set(b)
    return dict(intersection=sorted(a & b), intersection_count=len(a & b),
                jaccard=len(a & b) / len(a | b) if a | b else None)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("result_dir", type=Path)
    parser.add_argument("source_dir", type=Path)
    args = parser.parse_args()
    root = args.result_dir
    summary = json.loads((root / "summary.json").read_text())
    records = json.loads((root / "records.json").read_text())
    source = json.loads((args.source_dir / "summary.json").read_text())
    old_raw = (args.source_dir / "records.json").read_bytes()
    old = {row["dataset_index"]: row for row in json.loads(old_raw)["records"]}
    assert summary["status"] == records["status"] == "completed"
    assert hashlib.sha256(old_raw).hexdigest() == summary["parameters"]["gradient_records_sha256"]
    threshold = summary["parameters"]["min_component_iou"]
    assert threshold == .5
    rows = records["records"]
    assert len(rows) == summary["analyzed_samples"] == len(old) == 690
    assert len({row["dataset_index"] for row in rows}) == 690
    assert {row["dataset_index"] for row in rows} == set(old)
    counts, legacy, datasets = Counter(), Counter(), defaultdict(list)
    selected_iou, old_iou, selected_entropy, selected_gt_mass = [], [], [], []
    matches, selected_single_tokens = 0, 0
    grid_bounds = []
    for row in rows:
        before = old[row["dataset_index"]]
        assert row["sample_id"] == before["sample_id"]
        items = {item["head"]: item for item in row["gradient_candidates"]}
        old_items = {item["head"]: item for item in before["gradient_candidates"]}
        assert set(items) == set(old_items) and len(items) == 50
        assert all(items[h]["gradient_absolute"] == old_items[h]["gradient_absolute"] for h in items)
        assert 0 <= len(row["selected_heads"]) <= 10
        assert len(set(row["selected_heads"])) == len(row["selected_heads"])
        for head in row["selected_heads"]:
            item = items[head]
            assert item["dominant_component_fiou"] >= threshold
            assert item["reference_visual_mass"] >= row["visual_mass_floor"]
            selected_iou.append(item["dominant_component_fiou"])
            selected_entropy.append(item["normalized_entropy"])
            selected_gt_mass.append(item["gt_attention_mass"])
            selected_single_tokens += item["dominant_component_area"] == 1
            counts[head] += 1
        for head in row["legacy_selected_heads"]:
            legacy[head] += 1
            old_iou.append(items[head]["dominant_component_fiou"])
        matches += set(row["legacy_selected_heads"]) == set(before["selected_heads"])
        datasets[row["dataset"]].append(row)
        cache = root / "attention_maps" / f"sample_{row['dataset_index']:06d}.npz"
        if cache.is_file():
            with np.load(cache) as data:
                g = np.sort(data["occupancy"].ravel().astype(np.float64))[::-1]
            intersection = g.cumsum()
            # Maximum possible fractional IoU of ANY binary token mask, ignoring connectivity.
            bound = float(np.max(intersection / (np.arange(1, len(g)+1) + g.sum() - intersection)))
            grid_bounds.append(dict(dataset_index=row["dataset_index"], dataset=row["dataset"],
                                    upper_bound=bound, selected=len(row["selected_heads"])))
    ranking = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    assert summary["ranking"] == [dict(head=h, frequency=n) for h, n in ranking]
    assert summary["selected_heads"] == [h for h, n in ranking[:10]]
    for name, population in {"all": rows, **datasets}.items():
        c = Counter(h for row in population for h in row["selected_heads"])
        assert summary["frequency_denominators"][name] == len(population)
        matrix = summary["frequency_count_matrices"][name]
        assert len(matrix) == 36 and all(len(line) == 32 for line in matrix)
        for layer in range(36):
            for head in range(32):
                label = f"L{layer:02d}H{head:02d}"
                assert matrix[layer][head] == c[label]
                assert abs(summary["frequency_rate_matrices"][name][layer][head] - c[label] / len(population)) < 1e-12
        assert (root / f"frequency_{name}.png").is_file()
    quality = []
    for head, count in ranking[:10]:
        available = [item for row in rows for item in row["gradient_candidates"] if item["head"] == head]
        quality.append(dict(head=head, frequency=count, frequency_rate=count / len(rows),
            candidate_samples=len(available), unavailable_samples=len(rows)-len(available),
            candidate_iou=distribution([item["dominant_component_fiou"] for item in available]),
            candidate_gt_mass=distribution([item["gt_attention_mass"] for item in available]),
            candidate_iou_pass_count=sum(item["dominant_component_fiou"] >= threshold for item in available)))
    payload = dict(status="verified", result_id=root.name, source_id=args.source_dir.name, samples=len(rows),
        threshold=threshold, total_selections=sum(counts.values()),
        selected_count_histogram=dict(sorted(Counter(len(row["selected_heads"]) for row in rows).items())),
        by_dataset={name:dict(samples=len(pop), total_selections=sum(len(row["selected_heads"]) for row in pop),
            zero_selection_samples=sum(not row["selected_heads"] for row in pop),
            full_selection_samples=sum(len(row["selected_heads"]) == 10 for row in pop)) for name, pop in datasets.items()},
        selected_iou=distribution(selected_iou), legacy_selected_dominant_iou=distribution(old_iou),
        selected_entropy=distribution(selected_entropy), selected_gt_attention_mass=distribution(selected_gt_mass),
        selected_single_token_components=selected_single_tokens,
        token_grid_upper_bound_audit=dict(checked_samples=len(grid_bounds),
            impossible_at_threshold=[r for r in grid_bounds if r["upper_bound"] < threshold]),
        legacy_same_forward_exact_sample_matches=matches,
        legacy_same_forward_overlap=overlap([h for h,n in sorted(legacy.items(),key=lambda pair:(-pair[1],pair[0]))[:10]], source["selected_heads"]),
        overlap_with_original=overlap(summary["selected_heads"], source["selected_heads"]),
        top10=quality,
        limitations="同一发现集上的筛选诊断；入选IoU上升由门槛强制，不是独立性能验证；未进入梯度Top-50的head样本缺少map，不算零IoU。")
    (root / "comparison.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(payload,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
