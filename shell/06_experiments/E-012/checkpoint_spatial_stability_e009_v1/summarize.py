"""汇总本次四阶段的既有选头输出；不读取任何祖先 Run。"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys

import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("root", type=Path)
parser.add_argument("--steps", type=int, nargs="+", default=[83, 577, 1153, 1729])
parser.add_argument("--roles", choices=("query", "reference"), nargs="+", default=["query", "reference"])
parser.add_argument("--prefix", default="")
args = parser.parse_args()
root = args.root
steps, roles = tuple(args.steps), tuple(args.roles)
assert len(set(steps)) == len(steps) and len(steps) >= 2
prefix = args.prefix + "_" if args.prefix else ""
references = {
    "query": ("gradient-gated-spatial-frequency-r001-v2", "cc76ff624e85382ee300f75082ff6c0f0fa894ea7697ecc3b743d92008b9e99a"),
    "reference": ("reference-gradient-gated-spatial-frequency-r001-v1", "b835bf0a05d49c88d7766381baa848d2bcf5120cb71f171d78919391e7a2a2bf"),
}


def read(path):
    return json.loads(path.read_text())


def jaccard(a, b):
    a, b = set(a), set(b)
    assert a and b
    return len(a & b) / len(a | b)


def ranking(matrix):
    matrix = np.asarray(matrix)
    return [f"L{l:02d}H{h:02d}" for l, h in sorted(np.ndindex(matrix.shape), key=lambda v: (-matrix[v], v))]


summaries, records, hashes = {}, {}, {}
ref_summaries = {}
for role, (name, digest) in references.items():
    path = root.parent / name / "summary.json"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    ref_summaries[role] = read(path)

for step, role in itertools.product(steps, roles):
    folder = root / f"step_{step}_{role}"
    s, r = read(folder / "summary.json"), read(folder / "records.json")
    assert s["status"] == r["status"] == "completed"
    assert s["smoke_samples_per_dataset"] is None
    assert s["first_sample_forward_parity"] == "passed"
    assert s["parameters"]["role"] == role
    assert f"step_{step:06d}" in s["checkpoint"]["requested_path"]
    assert "/experiments/E-012/checkpoints/" in s["checkpoint"]["requested_path"]
    expected = ref_summaries[role]
    assert s["source"]["selected_indices"] == expected["source"]["selected_indices"]
    assert s["source"]["manifest_sha256"] == expected["source"]["manifest_sha256"]
    excluded_key = "excluded_invalid_gt" if role == "query" else "excluded_invalid_reference_gt"
    excluded = {v["dataset_index"] for v in expected[excluded_key]}
    assert {v["dataset_index"] for v in s["excluded_invalid_gt"]} == excluded
    expected_indices = set(expected["source"]["selected_indices"]) - excluded
    rows = r["records"]
    assert len(rows) == len(expected_indices) == s["analyzed_samples"]
    assert {v["dataset_index"] for v in rows} == expected_indices
    counts = Counter()
    for v in rows:
        assert v["role"] == role and len(v["gradient_candidates"]) == 50
        assert len(v["selected_heads"]) == len(set(v["selected_heads"])) == 10
        assert v["visual_token_count"] == np.prod(v["token_grid"])
        assert np.isfinite(v["bbox_token_ce"])
        assert all(f"{role}_visual_mass" in item and np.isfinite(item["gradient_absolute"]) for item in v["gradient_candidates"])
        counts.update(v["selected_heads"])
    ordered = ranking(s["frequency_count_matrices"]["all"])
    assert ordered[:10] == s["selected_heads"]
    assert all(counts[name] == np.asarray(s["frequency_count_matrices"]["all"])[int(name[1:3]), int(name[4:])] for name in ordered)
    assert s["frequency_denominators"] == expected["frequency_denominators"]
    summaries[step, role] = s
    records[step, role] = {v["dataset_index"]: {k: v[k] for k in ("sample_id", "dataset", "selected_heads")} for v in rows}
    hashes[folder.name] = hashlib.sha256((folder / "summary.json").read_bytes()).hexdigest()

assert len({s["code_sha256"] for s in summaries.values()}) == 1
assert len({s["seed"] for s in summaries.values()}) == 1
assert len({summaries[step, roles[0]]["checkpoint"]["adapter_weights_sha256"] for step in steps}) == len(steps)
if set(roles) == {"query", "reference"}:
    assert all(summaries[step, "query"]["checkpoint"] == summaries[step, "reference"]["checkpoint"] for step in steps)

pairs = []
for role in roles:
    for a, b in itertools.combinations(steps, 2):
        sa, sb = summaries[a, role], summaries[b, role]
        ra, rb = records[a, role], records[b, role]
        assert ra.keys() == rb.keys()
        assert all(ra[i]["sample_id"] == rb[i]["sample_id"] for i in ra)
        row = dict(role=role, step_a=a, step_b=b, top_k_jaccard={}, shared_top10=sorted(set(sa["selected_heads"]) & set(sb["selected_heads"])), only_a_top10=sorted(set(sa["selected_heads"]) - set(sb["selected_heads"])), only_b_top10=sorted(set(sb["selected_heads"]) - set(sa["selected_heads"])))
        order_a, order_b = (ranking(s["frequency_count_matrices"]["all"]) for s in (sa, sb))
        for k in (5, 10, 50):
            row["top_k_jaccard"][str(k)] = jaccard(order_a[:k], order_b[:k])
        row["sample_top10_jaccard_mean"] = float(np.mean([jaccard(ra[i]["selected_heads"], rb[i]["selected_heads"]) for i in ra]))
        row["dataset_top10_jaccard"] = {name: jaccard(ranking(sa["frequency_count_matrices"][name])[:10], ranking(sb["frequency_count_matrices"][name])[:10]) for name in ("LaSOT", "GOT10k", "TAO")}
        pairs.append(row)

stages = []
for step in steps:
    for role in roles:
        s = summaries[step, role]
        stages.append(dict(step=step, role=role, analyzed_samples=s["analyzed_samples"], bbox_token_ce_mean=s["bbox_token_ce_mean"], selected_heads=s["selected_heads"], ranking_top10=s["ranking"][:10], reference_top10_jaccard=jaccard(s["selected_heads"], ref_summaries[role]["selected_heads"])))
cross_role = {str(step): jaccard(summaries[step, "query"]["selected_heads"], summaries[step, "reference"]["selected_heads"]) for step in steps} if set(roles) == {"query", "reference"} else {}
result = dict(scope=dict(steps=steps, roles=roles, preliminary=bool(args.prefix)), status="completed", integrity="passed", explicit_references={role: value[0] for role, value in references.items()}, summary_sha256=hashes, stages=stages, checkpoint_pairs=pairs, within_checkpoint_query_reference_top10_jaccard=cross_role, claim_boundary="固定样本与算法下的跨 checkpoint 选头稳定性；不是因果、定位精度或独立留出泛化证据。引用 run 使用另一条 E-011 训练轨迹，不属于本次 E-009 阶段序列。")
(root / f"{prefix}comparison.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")

lines = [f"# E-012：E-009 {len(steps)} 个阶段选头稳定性（{', '.join(roles)}）", "", "四个 checkpoint 完整复制并逐文件验证 SHA-256；复用现有入口，对每个 checkpoint 重新计算梯度。", "", "| step | 角色 | 样本数 | bbox CE | Top-10 |", "|---:|---|---:|---:|---|"]
for s in stages:
    lines.append(f'| {s["step"]} | {s["role"]} | {s["analyzed_samples"]} | {s["bbox_token_ce_mean"]:.6f} | {", ".join(s["selected_heads"])} |')
lines += ["", "| 阶段比较 | " + " | ".join(role + " Top-10 Jaccard" for role in roles) + " |", "|---|" + "---:|" * len(roles)]
for a, b in itertools.combinations(steps, 2):
    values = [next(p["top_k_jaccard"]["10"] for p in pairs if p["role"] == role and p["step_a"] == a and p["step_b"] == b) for role in roles]
    lines.append(f"| {a} → {b} | " + " | ".join(f"{v:.4f}" for v in values) + " |")
for role in roles:
    lines += ["", role + " Top-10 并集的入选次数：", "", "| head | " + " | ".join(str(step) for step in steps) + " |", "|---|" + "---:|" * len(steps)]
    union = set().union(*(set(summaries[step, role]["selected_heads"]) for step in steps))
    for head in sorted(union):
        values = [int(np.asarray(summaries[step, role]["frequency_count_matrices"]["all"])[int(head[1:3]), int(head[4:])]) for step in steps]
        lines.append("| " + head + " | " + " | ".join(str(v) for v in values) + " |")
lines += ["", f"检查：本报告纳入的 {len(steps) * len(roles)} 组均全部完成；query 每组 686 条（LaSOT 296 / GOT10k 90 / TAO 300），reference 完整分析的目标为每组 690 条（300 / 90 / 300）。样本身份、排除规则、checkpoint 哈希、36×32 频率矩阵与逐样本记录一致，首样本前向一致性检查通过。", "", "固定参数：逐样本梯度 Top-50、空间 Top-10、视觉 mass 中位数门控、熵与 2×fIoU、累计 mass=0.5、全局 Top-10；seed=20260910；BF16 底座、eager attention。", "", "结论边界：" + result["claim_boundary"], "", "显式参考：" + "；".join(value[0] for value in references.values()) + "。没有使用额外 Solid run（任务提供的列表为空）。", "", "更完整的 Top-5/10/50、逐样本 Jaccard 和分数据集比较见 comparison.json。"]
(root / f"{prefix}report.md").write_text("\n".join(lines) + "\n")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, len(roles), figsize=(4.5 * len(roles), 4), constrained_layout=True)
axes = np.atleast_1d(axes).tolist()
for axis, role in zip(axes, roles):
    matrix = np.eye(len(steps))
    for pair in pairs:
        if pair["role"] == role:
            i, j = steps.index(pair["step_a"]), steps.index(pair["step_b"])
            matrix[i, j] = matrix[j, i] = pair["top_k_jaccard"]["10"]
    plot = axis.imshow(matrix, vmin=0, vmax=1, cmap="Blues")
    axis.set(title=f"{role}: global Top-10 Jaccard", xticks=range(len(steps)), yticks=range(len(steps)), xticklabels=steps, yticklabels=steps, xlabel="training step", ylabel="training step")
    for i, j in np.ndindex(matrix.shape):
        axis.text(j, i, f"{matrix[i,j]:.2f}", ha="center", va="center", color="white" if matrix[i,j] > .55 else "black")
fig.colorbar(plot, ax=axes, shrink=.8)
fig.savefig(root / f"{prefix}checkpoint_top10_jaccard.png", dpi=200)
plt.close(fig)
print(json.dumps(dict(status="completed", integrity="passed", checkpoint_pairs=pairs), ensure_ascii=False))
