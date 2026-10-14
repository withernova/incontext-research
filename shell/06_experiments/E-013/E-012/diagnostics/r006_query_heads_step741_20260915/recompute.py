"""按指定分支的自然预测，对已归档的 GT teacher-forced attention 分组。

只做离线统计；不加载模型、不改变选头、不修改治理状态。
python recompute.py --attention /tmp/e012_r006_review/baseline_attention.json \
    --predictions /tmp/e012_r006_review/predictions.jsonl --output <directory>
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

HEADS = ["L24H13", "L23H30", "L26H20", "L21H11", "L23H13"]
SEED = 20260915
REPLICATES = 10000
ATTENTION_HASH = "76b47106e4916eef2de0c98630470e3251ada373877696463f620020710b3b07"
PREDICTION_HASH = "c013e704d50ba7fa039d7c6a8e23b62c3b01bacbb6362c8e10598d940601326c"
METRICS = ["conditional_gt_mass", "log_gt_enrichment", "pointing_hit",
           "span_mass", "gt_area_fraction", "mean_head_absolute_gt_mass"]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def group_summary(values):
    values = np.asarray(values, dtype=float)
    if len(values) == 0:
        return {"n": 0, "mean": None, "median": None}
    assert np.isfinite(values).all()
    return {"n": len(values), "mean": float(values.mean()),
            "median": float(np.median(values))}


def compare(rows, key, correct_threshold=0.5, error_threshold=0.5):
    # 已校验每个 component 只有一条记录，所以样本抽样等价于 component 抽样。
    correct = np.array([r[key] for r in rows if r["iou"] >= correct_threshold], float)
    error = np.array([r[key] for r in rows if r["iou"] < error_threshold], float)
    result = {"correct": group_summary(correct), "error": group_summary(error)}
    if not len(correct) or not len(error):
        result.update(delta_correct_minus_error=None, ci95_mean_delta=None,
                      reason="至少一组为空，不估计组差异")
        return result
    rng = np.random.default_rng(SEED)
    boot = (rng.choice(correct, (REPLICATES, len(correct))).mean(1)
            - rng.choice(error, (REPLICATES, len(error))).mean(1))
    result.update(delta_correct_minus_error=float(correct.mean() - error.mean()),
                  ci95_mean_delta=np.quantile(boot, [.025, .975]).tolist())
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attention", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert sha256(args.attention) == ATTENTION_HASH, "attention 源文件发生变化"
    assert sha256(args.predictions) == PREDICTION_HASH, "prediction 源文件发生变化"
    attention = json.loads(args.attention.read_text())
    predictions = [json.loads(line) for line in args.predictions.read_text().splitlines()]
    by_index = {r["dataset_index"]: r for r in predictions}
    assert len(by_index) == len(predictions) == 1766
    assert attention["heads"] == HEADS
    assert attention["samples"] == len(attention["records"]) == 118
    assert len({r["dataset_index"] for r in attention["records"]}) == 118
    assert len({r["component_id"] for r in attention["records"]}) == 118
    rows = []
    for record in attention["records"]:
        pred = by_index[record["dataset_index"]]
        assert record["sample_id"] == pred["id"]
        assert record["dataset"] == pred["dataset"]
        assert record["split"] == "confirmation"
        assert pred["parsed"] and np.isfinite(pred["iou"])
        role = record["roles"]["reference"]
        ensemble = role["ensemble"]
        heads = role["heads"]
        assert 0 < ensemble["gt_area_fraction"] < 1
        assert np.isclose(ensemble["gt_enrichment"],
                          ensemble["conditional_gt_mass"] / ensemble["gt_area_fraction"])
        assert np.isclose(ensemble["log_gt_enrichment"], np.log(ensemble["gt_enrichment"]))
        # Ensemble 是各 head 条件分布的均值；核查线性的 mass 统计。
        for key in ("conditional_gt_mass", "span_mass"):
            assert np.isclose(ensemble[key], np.mean([heads[h][key] for h in HEADS]),
                              rtol=1e-5, atol=1e-8)
        row = {"dataset_index": record["dataset_index"], "sample_id": record["sample_id"],
               "dataset": record["dataset"], "sequence": pred["sequence"],
               "component_id": record["component_id"], "iou": pred["iou"],
               "correct_iou050": pred["iou"] >= .5,
               "reference_grid_h": role["grid_hw"][0], "reference_grid_w": role["grid_hw"][1],
               **{k: float(ensemble[k]) for k in METRICS if k in ensemble}}
        # 先按 head 计算全序列 attention 中的 GT mass，再等权平均；
        # 不使用 ensemble span mean × conditional mean，以免引入交叉项。
        row["mean_head_absolute_gt_mass"] = float(np.mean([
            heads[h]["span_mass"] * heads[h]["conditional_gt_mass"] for h in HEADS]))
        for head in HEADS:
            for metric in ("conditional_gt_mass", "log_gt_enrichment", "pointing_hit", "span_mass"):
                row[f"{head}/{metric}"] = float(heads[head][metric])
        rows.append(row)
    assert len({(r["dataset"], r["sequence"]) for r in rows}) == 118
    full_iou = np.array([p["iou"] for p in predictions])
    summary = {
        "schema": "e012.r006-query-head-reference-outcome-reanalysis/v1",
        "status": "offline_reanalysis_completed_on_available_118",
        "heads": HEADS, "attention_rows": attention["attention_rows"],
        "checkpoint": attention["checkpoint_path"],
        "checkpoint_adapter_sha256": attention["checkpoint_adapter_sha256"],
        "manifest_sha256": attention["manifest_sha256"],
        "assignments_sha256": attention["assignments_sha256"],
        "input_sha256": {"attention": ATTENTION_HASH, "predictions": PREDICTION_HASH},
        "method": {"correct": "IoU >= 0.5", "error": "IoU < 0.5",
                   "aggregation": "先对5个head的reference条件分布等权平均，再样本等权；原始GT mass另按head乘积后平均",
                   "bootstrap": "在正确/错误组内独立有放回抽样；每条记录对应唯一sequence/component",
                   "seed": SEED, "replicates": REPLICATES,
                   "ci": "未作多重比较校正的描述性95% percentile CI"},
        "integrity": {"matched_by_dataset_index_sample_id_dataset": 118,
                      "unique_sequences": 118, "unique_components": 118,
                      "attention_hash_matches_remote_integrity": True,
                      "predictions_hash_matches_remote": True,
                      "missing_attention_in_full_eval": 1648},
        "full_eval": {"n": 1766, "correct": int((full_iou >= .5).sum()),
                      "error": int((full_iou < .5).sum()), "miou": float(full_iou.mean()),
                      "acc_iou050": float((full_iou >= .5).mean())},
        "ensemble": {k: compare(rows, k) for k in METRICS},
        "per_head": {h: {k: compare(rows, f"{h}/{k}") for k in
                         ("conditional_gt_mass", "log_gt_enrichment", "pointing_hit", "span_mass")}
                     for h in HEADS},
        "by_dataset": {d: {k: compare([r for r in rows if r["dataset"] == d], k)
                           for k in METRICS} for d in sorted({r["dataset"] for r in rows})},
        "strict_error_iou_lt010": {k: compare(rows, k, error_threshold=.1) for k in METRICS},
        "strict_correct_iou_ge075": {k: compare(rows, k, correct_threshold=.75) for k in METRICS},
        "limitations": ["仅118条confirmation有归档attention，不能代表1766全量比较",
                        "attention采用GT teacher-forced坐标rows，不是归档自然预测的生成rows",
                        "正确/错误组的reference GT面积与dataset组成不同，相关性不等于因果",
                        "attention记录未完整提供重放精度/量化/图像token预算，不能确认与自然评估完全同设置",
                        "仅18条错误；GOT10k子集中没有错误；多head比较只作描述"]}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "statistics.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2,
                                                         allow_nan=False) + "\n")
    with (args.output / "joined_samples.csv").open("w") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"full_eval": summary["full_eval"], "ensemble": summary["ensemble"],
                      "by_dataset": {d: x["conditional_gt_mass"] for d, x in summary["by_dataset"].items()}},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
