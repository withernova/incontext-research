"""独立复核：step741 baseline 上 query 五头对 reference 图像的 GT 集中度按预测正误分组。

只读本任务显式引用的两份产物：
  1. R-006-query-r005-ref3-transfer-step247-3ep-v1/attention_compare_step741_v1/baseline/records.json
  2. E-009 .../20260915T071307686259Z--baseline-eval-741-new-ft/evaluation/predictions.jsonl

不启动模型、不写远端、不改治理状态。输出 independent_recheck.json。
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

HEADS = ["L24H13", "L23H30", "L26H20", "L21H11", "L23H13"]
METRICS = ["conditional_gt_mass", "log_gt_enrichment", "span_mass", "pointing_hit"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bootstrap_diff(a, b, replicates=10000, seed=20260915):
    rng = np.random.default_rng(seed)
    a, b = np.asarray(a, float), np.asarray(b, float)
    draws = np.empty(replicates)
    for i in range(replicates):
        draws[i] = (a[rng.integers(0, a.size, a.size)].mean()
                    - b[rng.integers(0, b.size, b.size)].mean())
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def block(values, correct, key):
    a = [v for v, c in zip(values, correct) if c]
    b = [v for v, c in zip(values, correct) if not c]
    lo, hi = bootstrap_diff(a, b)
    return {
        key: {
            "correct_n": len(a), "incorrect_n": len(b),
            "correct_mean": float(np.mean(a)), "incorrect_mean": float(np.mean(b)),
            "correct_median": float(np.median(a)), "incorrect_median": float(np.median(b)),
            "diff_mean_correct_minus_incorrect": float(np.mean(a) - np.mean(b)),
            "diff_ci95": [lo, hi], "ci_excludes_zero": bool(lo > 0 or hi < 0),
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attention", required=True)
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    attention_path, predictions_path = Path(args.attention), Path(args.predictions)
    payload = json.loads(attention_path.read_text())
    records = payload["records"]
    predictions = {}
    for line in predictions_path.read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            predictions[int(row["dataset_index"])] = row

    joined, missing = [], []
    for record in records:
        index = int(record["dataset_index"])
        if index not in predictions:
            missing.append(index)
            continue
        iou = predictions[index]["iou"]
        joined.append({"dataset_index": index, "dataset": record["dataset"],
                       "target_size_bin": record.get("target_size_bin"),
                       "component_id": record["component_id"], "iou": float(iou),
                       "parsed": bool(predictions[index]["parsed"]),
                       "correct": bool(predictions[index]["parsed"] and iou >= 0.5),
                       "only_wrong_lt0.1": bool(iou < 0.1),
                       "only_right_ge0.75": bool(iou >= 0.75),
                       "reference": record["roles"]["reference"],
                       "reference_share": float(record["reference_share_of_two_visual_spans"])})

    def series(rows, role_head, metric):
        out = []
        for row in rows:
            block_data = row["reference"]
            if role_head == "ensemble":
                out.append(float(block_data["ensemble"][metric]))
            else:
                out.append(float(block_data["heads"][role_head][metric]))
        return out

    result = {
        "schema": "e012.independent-recheck/v1",
        "inputs": {
            "attention": str(attention_path), "attention_sha256": sha256(attention_path),
            "predictions": str(predictions_path), "predictions_sha256": sha256(predictions_path),
            "records": len(records), "prediction_rows": len(predictions),
            "joined": len(joined), "missing_indices": missing,
            "unique_joined_indices": len({r["dataset_index"] for r in joined}),
            "unique_components": len({r["component_id"] for r in joined}),
        },
        "correctness": {
            "correct": sum(r["correct"] for r in joined),
            "incorrect": sum(not r["correct"] for r in joined),
        },
        "primary": {},
        "per_head": {},
        "sensitivity": {},
        "by_dataset": {},
        "reference_share_of_two_visual_spans": {},
    }

    correct = [r["correct"] for r in joined]
    for metric in METRICS:
        result["primary"].update(block(series(joined, "ensemble", metric), correct, metric))
    result["reference_share_of_two_visual_spans"] = block(
        [r["reference_share"] for r in joined], correct, "reference_share")["reference_share"]

    for head in HEADS:
        result["per_head"][head] = {}
        for metric in ("conditional_gt_mass", "log_gt_enrichment", "span_mass"):
            result["per_head"][head].update(
                block(series(joined, head, metric), correct, metric))

    # 收紧定义：错误收紧到 IoU<0.1，正确收紧到 IoU>=0.75；两组都用全部 118 条做分母。
    tight = [r for r in joined if r["correct"] or r["only_wrong_lt0.1"]]
    result["sensitivity"]["incorrect_lt0.1_vs_correct"] = {
        "n": len(tight),
        "conditional_gt_mass": block(series(tight, "ensemble", "conditional_gt_mass"),
                                     [r["correct"] for r in tight], "gt_mass")["gt_mass"],
        "log_gt_enrichment": block(series(tight, "ensemble", "log_gt_enrichment"),
                                   [r["correct"] for r in tight], "log_enrichment")["log_enrichment"],
    }
    result["sensitivity"]["iou_ge0.75_vs_rest"] = {
        "n": len(joined),
        "conditional_gt_mass": block(series(joined, "ensemble", "conditional_gt_mass"),
                                     [r["only_right_ge0.75"] for r in joined], "gt_mass")["gt_mass"],
        "log_gt_enrichment": block(series(joined, "ensemble", "log_gt_enrichment"),
                                   [r["only_right_ge0.75"] for r in joined], "log_enrichment")["log_enrichment"],
    }
    bins = sorted({r["target_size_bin"] for r in joined})
    result["by_target_size_bin"] = {}
    for name in bins:
        subset = [r for r in joined if r["target_size_bin"] == name]
        labels = [r["correct"] for r in subset]
        if len(set(labels)) < 2:
            result["by_target_size_bin"][name] = {"n": len(subset),
                                                  "correct": int(sum(labels)),
                                                  "note": "single class; no difference estimate"}
            continue
        result["by_target_size_bin"][name] = {
            "n": len(subset), "correct": int(sum(labels)),
            "conditional_gt_mass": block(series(subset, "ensemble", "conditional_gt_mass"), labels, "gt_mass")["gt_mass"],
        }

    for dataset in sorted({r["dataset"] for r in joined}):
        subset = [r for r in joined if r["dataset"] == dataset]
        labels = [r["correct"] for r in subset]
        if len(set(labels)) < 2:
            result["by_dataset"][dataset] = {"n": len(subset), "correct": int(sum(labels)),
                                             "note": "single class; no difference estimate"}
            continue
        result["by_dataset"][dataset] = {
            "n": len(subset), "correct": int(sum(labels)),
            "conditional_gt_mass": block(series(subset, "ensemble", "conditional_gt_mass"), labels, "gt_mass")["gt_mass"],
            "log_gt_enrichment": block(series(subset, "ensemble", "log_gt_enrichment"), labels, "log_enrichment")["log_enrichment"],
        }

    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
