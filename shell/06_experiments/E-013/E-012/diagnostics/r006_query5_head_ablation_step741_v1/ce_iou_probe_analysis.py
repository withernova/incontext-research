"""CE 与 IoU 目标一致性：沿选头排名的单头整头置零结果分析。

输入：
  --records      探针 run 的 records.json（22 条件：baseline + 17 单头 + 17 头联合 + 3 随机）
  --screening    R-006 attempt-001/summary.json（提供 36x32 的 combined_score_mean / C）
  --extra        可选，额外单头记录（其余 run 的同协议单头），用于扩大散点
输出：逐 head 的 score/|ΔCE|/ΔIoU 表、相关系数、象限划分。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def load_records(path):
    rows = json.loads(Path(path).read_text())["records"]
    by = {}
    for row in rows:
        by.setdefault(row["condition"], {})[row["dataset_index"]] = row
    return by


def paired(by, name, base="baseline"):
    out = []
    for index, row in sorted(by[name].items()):
        if index not in by[base]:
            continue
        out.append((row["metrics"]["bbox_token_ce"] - by[base][index]["metrics"]["bbox_token_ce"],
                    row["metrics"]["iou"] - by[base][index]["metrics"]["iou"]))
    return np.asarray(out, float)


def bootstrap_ci(values, replicates=10000, seed=20260915):
    values = np.asarray(values, float)
    rng = np.random.default_rng(seed)
    draws = values[rng.integers(0, values.size, (replicates, values.size))].mean(1)
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if x.size < 3 or np.all(x == x[0]) or np.all(y == y[0]):
        return float("nan")
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def screening_scores(path):
    summary = json.loads(Path(path).read_text())
    combined = np.asarray(summary["discovery"]["head_metrics"]["combined_score_mean"], float)
    contribution = np.asarray(summary["discovery"]["head_metrics"]["reference_abs_contribution_mean"], float)
    ordered = sorted(((combined[l, h], l, h) for l in range(combined.shape[0])
                      for h in range(combined.shape[1])), key=lambda t: (-t[0], t[1], t[2]))
    rank = {(l, h): (i, float(v), float(contribution[l, h])) for i, (v, l, h) in enumerate(ordered, 1)}
    return rank


def label_to_pair(name):
    head = name.split("_", 1)[1]
    layer, width = head.split("H")
    return int(layer[1:]), int(width)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", required=True)
    parser.add_argument("--screening", required=True)
    parser.add_argument("--extra", nargs="*", default=[])
    parser.add_argument("--output")
    args = parser.parse_args()

    by = load_records(args.records)
    rank = screening_scores(args.screening)
    conditions = [c for c in by if c != "baseline"]

    rows, pooled = [], []
    for name in sorted(conditions):
        pairs = paired(by, name)
        pooled.append(pairs)
        entry = {"condition": name, "n": int(pairs.shape[0]),
                 "d_ce_mean": float(pairs[:, 0].mean()), "d_iou_mean": float(pairs[:, 1].mean()),
                 "d_ce_abs_mean": float(np.abs(pairs[:, 0]).mean()),
                 "d_iou_ci95": list(bootstrap_ci(pairs[:, 1])),
                 "d_ce_ci95": list(bootstrap_ci(pairs[:, 0])),
                 "d_iou_positive_fraction": float((pairs[:, 1] > 0).mean())}
        if name.startswith("single_"):
            layer, head = label_to_pair(name)
            r, score, contribution = rank[(layer, head)]
            entry.update({"layer": layer, "head": head, "screening_rank": r,
                          "screening_score": score, "abs_contribution_C": contribution})
        rows.append(entry)

    for path in args.extra:
        other = load_records(path)
        for name in sorted(other):
            if name.startswith("single_") and name not in by:
                pairs = paired(other, name)
                layer, head = label_to_pair(name)
                r, score, contribution = rank[(layer, head)]
                rows.append({"condition": name, "n": int(pairs.shape[0]), "source": str(path),
                             "d_ce_mean": float(pairs[:, 0].mean()), "d_iou_mean": float(pairs[:, 1].mean()),
                             "d_ce_abs_mean": float(np.abs(pairs[:, 0]).mean()),
                             "d_iou_ci95": list(bootstrap_ci(pairs[:, 1])),
                             "screening_rank": r, "screening_score": score,
                             "abs_contribution_C": contribution, "layer": layer, "head": head})

    singles = [r for r in rows if r.get("screening_score") is not None]
    scores = [r["screening_score"] for r in singles]
    absce = [r["d_ce_abs_mean"] for r in singles]
    diou = [r["d_iou_mean"] for r in singles]
    contributions = [r["abs_contribution_C"] for r in singles]

    flat = np.concatenate(pooled) if pooled else np.zeros((0, 2))
    result = {
        "schema": "e012.ce-vs-iou-probe-analysis/v1",
        "records": str(args.records),
        "n_conditions": len(rows),
        "per_condition": rows,
        "head_level": {
            "n_heads": len(singles),
            "spearman_score_vs_abs_d_ce": spearman(scores, absce),
            "spearman_score_vs_d_iou": spearman(scores, diou),
            "spearman_C_vs_abs_d_ce": spearman(contributions, absce),
            "spearman_C_vs_d_iou": spearman(contributions, diou),
            "spearman_abs_d_ce_vs_d_iou": spearman(absce, diou),
        },
        "pooled_per_sample": {
            "n_pairs": int(flat.shape[0]),
            "spearman_d_ce_vs_d_iou": spearman(flat[:, 0], flat[:, 1]),
            "spearman_abs_d_ce_vs_d_iou": spearman(np.abs(flat[:, 0]), flat[:, 1]),
        },
    }

    print("条件级（ΔCE / ΔIoU 均为主产物指标；ΔIoU<0 表示变差）")
    print("  %-24s %9s %9s %26s" % ("condition", "ΔCE", "ΔIoU", "ΔIoU 95% CI"))
    for row in sorted(rows, key=lambda r: (r.get("screening_rank") or 9999, r["condition"])):
        tag = ("rank %-4d" % row["screening_rank"]) if "screening_rank" in row else " ".ljust(9)
        print("  %-9s %-14s %+9.4f %+9.4f  [%+.4f,%+.4f]"
              % (tag, row["condition"], row["d_ce_mean"], row["d_iou_mean"],
                 row["d_iou_ci95"][0], row["d_iou_ci95"][1]))

    print("\n单头 head 级相关（n=%d）" % len(singles))
    for key, value in result["head_level"].items():
        if key.startswith("spearman"):
            print("  %-32s %+.3f" % (key, value))
    print("  逐样本整体 Spearman(ΔCE,ΔIoU)=%+.3f (n=%d)"
          % (result["pooled_per_sample"]["spearman_d_ce_vs_d_iou"], result["pooled_per_sample"]["n_pairs"]))

    if args.output:
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
