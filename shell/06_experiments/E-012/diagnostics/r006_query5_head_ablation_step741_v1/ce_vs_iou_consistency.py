"""用既有整头消融记录检验 CE 与 IoU 两个目标的一致性。

输入：两次 step741 整头消融的 records.json（各自自带 baseline 条件）。
输出：逐样本 ΔCE/ΔIoU 关系、逐条件象限表、逐 head 表 + 与筛选分数的相关。
不启动模型。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def load(path):
    payload = json.loads(Path(path).read_text())
    rows = payload["records"]
    by = {}
    for row in rows:
        by.setdefault(row["condition"], {})[row["dataset_index"]] = row
    return rows, by


def paired(by, name):
    base = by["baseline"]
    out = []
    for index, row in sorted(by[name].items()):
        if index not in base:
            continue
        out.append({
            "index": index,
            "d_ce": row["metrics"]["bbox_token_ce"] - base[index]["metrics"]["bbox_token_ce"],
            "d_iou": row["metrics"]["iou"] - base[index]["metrics"]["iou"],
        })
    return out


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def pearson(x, y):
    return float(np.corrcoef(np.asarray(x, float), np.asarray(y, float))[0, 1])


def report(tag, path, scores=None):
    rows, by = load(path)
    conditions = [c for c in by if c != "baseline"]
    per_condition = []
    all_ce, all_iou = [], []
    for name in conditions:
        pairs = paired(by, name)
        d_ce = [p["d_ce"] for p in pairs]
        d_iou = [p["d_iou"] for p in pairs]
        all_ce.extend(d_ce)
        all_iou.extend(d_iou)
        per_condition.append({
            "condition": name, "n": len(pairs),
            "d_ce_mean": float(np.mean(d_ce)), "d_iou_mean": float(np.mean(d_iou)),
            "d_ce_abs_mean": float(np.mean(np.abs(d_ce))),
            "d_iou_pos_fraction": float(np.mean([v > 0 for v in d_iou])),
            "spearman_within_condition": spearman(d_ce, d_iou),
        })
    per_condition.sort(key=lambda r: r["condition"])
    result = {
        "tag": tag, "path": str(path), "records": len(rows),
        "overall": {
            "n_pairs": len(all_ce),
            "pearson_d_ce_vs_d_iou": pearson(all_ce, all_iou),
            "spearman_d_ce_vs_d_iou": spearman(all_ce, all_iou),
            "spearman_d_ce_abs_vs_d_iou": spearman(np.abs(all_ce), all_iou),
        },
        "per_condition": per_condition,
    }
    print(f"=== {tag}  (pairs={result['overall']['n_pairs']})")
    print("  整体 Pearson(ΔCE,ΔIoU)=%.3f  Spearman=%.3f  Spearman(|ΔCE|,ΔIoU)=%.3f"
          % (result["overall"]["pearson_d_ce_vs_d_iou"], result["overall"]["spearman_d_ce_vs_d_iou"],
             result["overall"]["spearman_d_ce_abs_vs_d_iou"]))
    print("  %-22s %8s %8s %8s %8s %8s" % ("condition", "ΔCE", "ΔIoU", "|ΔCE|", "变好比例", "条件内ρ"))
    for row in per_condition:
        print("  %-22s %+8.4f %+8.4f %8.4f %8.2f %8.2f"
              % (row["condition"], row["d_ce_mean"], row["d_iou_mean"],
                 row["d_ce_abs_mean"], row["d_iou_pos_fraction"], row["spearman_within_condition"]))
    if scores:
        singles = [r for r in per_condition if r["condition"].startswith("single_")]
        print("  单头筛选分数 vs 干预结果：")
        sc, ce, iou = [], [], []
        for row in singles:
            label = row["condition"].replace("single_", "")
            value = scores.get(label)
            if value is None:
                continue
            sc.append(value)
            ce.append(row["d_ce_abs_mean"])
            iou.append(row["d_iou_mean"])
            print("    %-8s score=%.4f  |ΔCE|=%.4f  ΔIoU=%+.4f" % (label, value, row["d_ce_abs_mean"], row["d_iou_mean"]))
        if len(sc) >= 3:
            print("    n=%d  Spearman(score,|ΔCE|)=%.2f  Spearman(score,ΔIoU)=%.2f"
                  % (len(sc), spearman(sc, ce), spearman(sc, iou)))
            result["score_correlation"] = {
                "n": len(sc), "spearman_score_vs_abs_d_ce": spearman(sc, ce),
                "spearman_score_vs_d_iou": spearman(sc, iou), "heads": singles}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--r006", required=True)
    parser.add_argument("--legacy", required=True)
    parser.add_argument("--r006_heads_path", help="R-006 frozen_heads.json")
    parser.add_argument("--output")
    args = parser.parse_args()
    scores = None
    if args.r006_heads_path:
        frozen = json.loads(Path(args.r006_heads_path).read_text())["E_null_calibrated"]
        scores = {f"L{r['layer']:02d}H{r['head']:02d}": r["score"] for r in frozen}
    out = {
        "schema": "e012.ce-vs-iou-consistency/v1",
        "r006": report("R-006 query 五头", args.r006, scores),
        "legacy": report("旧 E-009 五头", args.legacy, None),
    }
    if args.output:
        Path(args.output).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
