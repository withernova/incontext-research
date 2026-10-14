"""score–effect alignment：H_old ∪ H_new 逐头消融的表格与四个关系。

输入：
  --records     oldnew-union10 消融的 records.json
  --heads       inputs/old_new_union10_heads_v1.json（含旧空间分数与 G/T_a/T_d）
输出：逐头表（7 列）+ 四个关系的 Spearman + 联合/随机对照汇总。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def load(path):
    payload = json.loads(Path(path).read_text())
    by = {}
    for row in payload["records"]:
        by.setdefault(row["condition"], {})[row["dataset_index"]] = row
    return payload, by


def paired(by, name, key, base="baseline"):
    out = []
    for index, row in sorted(by[name].items()):
        if index in by[base]:
            out.append(row["metrics"][key] - by[base][index]["metrics"][key])
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
    return float(np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(y)))[0, 1])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", required=True)
    parser.add_argument("--heads", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    payload, by = load(args.records)
    head_spec = json.loads(Path(args.heads).read_text())
    meta = {entry["label"]: entry for entry in head_spec["candidate_heads"]}
    n_samples = len(by["baseline"])

    rows = []
    for label, entry in meta.items():
        name = "single_" + label
        if name not in by:
            continue
        d_ce = paired(by, name, "bbox_token_ce")
        d_iou = paired(by, name, "iou")
        d_tf = paired(by, name, "teacher_forced_iou")
        rows.append({
            "head": label, "group": entry["group"],
            "old_freq": entry["old_screening_frequency"],
            "old_mean_mass": entry["old_mean_image_attention_sum"],
            "old_mean_entropy": entry["old_mean_component_entropy"],
            "G_ce": entry["r006_G_abs_contribution_C"],
            "T_a": entry["r006_T_a"], "T_d": entry["r006_T_d"],
            "d_ce": float(d_ce.mean()), "d_iou": float(d_iou.mean()),
            "d_iou_ci95": list(bootstrap_ci(d_iou)),
            "d_iou_se": float(d_iou.std(ddof=1) / np.sqrt(d_iou.size)),
            "d_tf_iou": float(d_tf.mean()), "d_tf_iou_ci95": list(bootstrap_ci(d_tf)),
            "d_tf_iou_se": float(d_tf.std(ddof=1) / np.sqrt(d_tf.size)),
            "n": int(d_iou.size),
        })

    def col(key):
        return [row[key] for row in rows]

    relations = {
        "旧 freq vs ΔmIoU": spearman(col("old_freq"), col("d_iou")),
        "旧 mean_mass vs ΔmIoU": spearman(col("old_mean_mass"), col("d_iou")),
        "旧 mean_entropy vs ΔmIoU": spearman(col("old_mean_entropy"), col("d_iou")),
        "G^CE vs |ΔCE|": spearman(col("G_ce"), [abs(v) for v in col("d_ce")]),
        "G^CE vs ΔmIoU": spearman(col("G_ce"), col("d_iou")),
        "T_a vs ΔmIoU": spearman(col("T_a"), col("d_iou")),
        "T_d vs ΔmIoU": spearman(col("T_d"), col("d_iou")),
        "|ΔCE| vs ΔmIoU": spearman([abs(v) for v in col("d_ce")], col("d_iou")),
        "G^CE vs ΔTF-IoU": spearman(col("G_ce"), col("d_tf_iou")),
        "旧 freq vs ΔTF-IoU": spearman(col("old_freq"), col("d_tf_iou")),
        "T_a vs ΔTF-IoU": spearman(col("T_a"), col("d_tf_iou")),
        "T_d vs ΔTF-IoU": spearman(col("T_d"), col("d_tf_iou")),
    }

    joint = None
    if "top10_joint" in by:
        d = paired(by, "top10_joint", "iou")
        joint = {"n": int(d.size), "d_iou": float(d.mean()), "ci95": list(bootstrap_ci(d)),
                 "d_ce": float(paired(by, "top10_joint", "bbox_token_ce").mean()),
                 "d_tf_iou": float(paired(by, "top10_joint", "teacher_forced_iou").mean())}
    randoms = {name: {"d_iou": float(paired(by, name, "iou").mean()),
                      "d_ce": float(paired(by, name, "bbox_token_ce").mean())}
               for name in by if name.startswith("random_seed_")}

    print(f"样本数 n={n_samples}（每头 {rows[0]['n'] if rows else 0}）")
    print("%-8s %-4s %5s %8s %7s %8s %7s %7s | %8s %10s %16s | %9s" %
          ("head", "grp", "freq", "oldMass", "oldEnt", "G^CE", "T_a", "T_d", "ΔCE", "ΔmIoU", "ΔmIoU 95% CI", "ΔTF-IoU"))
    for row in rows:
        print("%-8s %-4s %5d %8.4f %7.3f %8.5f %7.4f %7.4f | %+8.4f %+10.4f [%+.4f,%+.4f] | %+9.4f" % (
            row["head"], row["group"][:3], row["old_freq"], row["old_mean_mass"], row["old_mean_entropy"],
            row["G_ce"], row["T_a"], row["T_d"], row["d_ce"], row["d_iou"],
            row["d_iou_ci95"][0], row["d_iou_ci95"][1], row["d_tf_iou"]))
    print("\n关系（n=%d 个头）" % len(rows))
    for name, value in relations.items():
        print("  %-26s Spearman=%+.3f" % (name, value))
    if joint:
        print("\n10 头联合：ΔmIoU=%+.4f CI=[%+.4f,%+.4f]  ΔCE=%+.4f  ΔTF-IoU=%+.4f" % (
            joint["d_iou"], joint["ci95"][0], joint["ci95"][1], joint["d_ce"], joint["d_tf_iou"]))
    for name, value in randoms.items():
        print("  %s ΔmIoU=%+.4f ΔCE=%+.4f" % (name, value["d_iou"], value["d_ce"]))

    if args.output:
        Path(args.output).write_text(json.dumps({
            "schema": "e012.score-effect-alignment/v1", "n_samples": n_samples,
            "records": args.records, "heads": rows, "relations": relations,
            "joint": joint, "random_controls": randoms}, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
