"""R-006 Query 五头整头 attention 置零消融的汇总：条件间配对比较与随机头对照。

输入：远程 r006-query5-whole-head-ablation-step741-v1/records.json（只读副本）。
输出：stdout 表格 + summary JSON；不启动模型。
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

METRIC_KEYS = ["iou", "delta_iou", "invalid_output", "box_changed", "coordinate_mae_normalized",
               "delta_bbox_token_ce"]


def bootstrap_ci(values, replicates=10000, seed=20260915):
    values = np.asarray(values, float)
    rng = np.random.default_rng(seed)
    draws = values[rng.integers(0, values.size, (replicates, values.size))].mean(1)
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    payload = json.loads(Path(args.records).read_text())
    records = payload["records"]

    by_condition = {}
    for row in records:
        by_condition.setdefault(row["condition"], {})[row["dataset_index"]] = row

    baseline = by_condition["baseline"]
    order = ["baseline"] + sorted(
        (c for c in by_condition if c != "baseline"),
        key=lambda c: (c.startswith("random_seed_"), c.startswith("single_"), c))
    assert set(order) == set(by_condition)

    result = {"schema": "e012.r006-query5-head-ablation-summary/v1", "records": len(records),
              "delta_direction": "intervention_minus_baseline", "conditions": {}}
    for name in order:
        rows = by_condition[name]
        entry = {"n": len(rows)}
        for key in METRIC_KEYS:
            values = [rows[i]["metrics"][key] for i in sorted(rows)
                      if rows[i]["metrics"].get(key) is not None]
            if key == "delta_iou":
                values = []
            if not values:
                continue
            entry[key + "_mean"] = float(np.mean(values))
            if key in ("iou", "coordinate_mae_normalized"):
                lo, hi = bootstrap_ci(values)
                entry[key + "_ci95"] = [lo, hi]
        # 与 baseline 的逐样本配对差
        paired = [(rows[i]["metrics"]["iou"] - baseline[i]["metrics"]["iou"])
                  for i in sorted(rows) if i in baseline]
        entry["paired_delta_iou_vs_baseline_mean"] = float(np.mean(paired))
        entry["paired_delta_iou_vs_baseline_ci95"] = list(bootstrap_ci(paired))
        entry["paired_delta_iou_positive_fraction"] = float(np.mean([p > 0 for p in paired]))
        entry["iou_drop_relative_to_baseline"] = (
            1.0 - entry["iou_mean"] / result["conditions"].get("baseline", entry)["iou_mean"]
            if name != "baseline" else 0.0)
        result["conditions"][name] = entry

    # joint 与随机对照的差：逐样本先平均随机 3 组，再配对
    random_names = [n for n in order if n.startswith("random_seed_")]
    if random_names and "top10_joint" in by_condition:
        joint = by_condition["top10_joint"]
        joint_vs_random = []
        for i in sorted(joint):
            if any(i not in by_condition[n] for n in random_names):
                continue
            random_mean = np.mean([by_condition[n][i]["metrics"]["iou"] for n in random_names])
            joint_vs_random.append(joint[i]["metrics"]["iou"] - random_mean)
        result["joint_minus_random_control"] = {
            "n": len(joint_vs_random),
            "delta_iou_mean": float(np.mean(joint_vs_random)),
            "delta_iou_ci95": list(bootstrap_ci(joint_vs_random)),
            "negative_fraction": float(np.mean([v < 0 for v in joint_vs_random])),
        }

    per_dataset = {}
    for dataset in sorted({r["dataset"] for r in records}):
        block = {}
        for name in order:
            rows = {i: by_condition[name][i] for i in by_condition[name] if by_condition[name][i]["dataset"] == dataset}
            paired = [(rows[i]["metrics"]["iou"] - baseline[i]["metrics"]["iou"])
                      for i in sorted(rows) if i in baseline]
            block[name] = {"n": len(rows),
                           "iou_mean": float(np.mean([r["metrics"]["iou"] for r in rows.values()])),
                           "paired_delta_iou_mean": float(np.mean(paired)),
                           "paired_delta_iou_ci95": list(bootstrap_ci(paired))}
        per_dataset[dataset] = block
    result["by_dataset"] = per_dataset

    if args.output:
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")

    print(f"{'condition':26s} {'mIoU':>7s} {'ΔIoU vs base':>26s} {'IoU↓%':>7s} {'invalid':>8s} {'box_chg':>8s}")
    for name in order:
        e = result["conditions"][name]
        ci = e["paired_delta_iou_vs_baseline_ci95"]
        print(f"{name:26s} {e['iou_mean']:7.4f} [{ci[0]:+.4f},{ci[1]:+.4f}]".ljust(60)
              + f" {100 * e['iou_drop_relative_to_baseline']:6.2f}%"
              + f" {e.get('invalid_output_mean', float('nan')):8.4f}"
              + f" {e.get('box_changed_mean', float('nan')):8.4f}")
    if "joint_minus_random_control" in result:
        j = result["joint_minus_random_control"]
        print(f"\njoint(5 new query heads) - mean(random controls): ΔIoU={j['delta_iou_mean']:+.4f} "
              f"CI95=[{j['delta_iou_ci95'][0]:+.4f},{j['delta_iou_ci95'][1]:+.4f}] n={j['n']}")
    for dataset, block in per_dataset.items():
        print(f"\n[{dataset}]")
        for name in order:
            b = block[name]
            print(f"  {name:26s} mIoU={b['iou_mean']:.4f} ΔIoU={b['paired_delta_iou_mean']:+.4f} "
                  f"CI95=[{b['paired_delta_iou_ci95'][0]:+.4f},{b['paired_delta_iou_ci95'][1]:+.4f}]")


if __name__ == "__main__":
    main()
