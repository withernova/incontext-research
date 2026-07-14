#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plot compact figures for E-001/E-002 token-intervention group meeting slides."""
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.dpi": 160,
})

def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, bbox_inches="tight")
    fig.savefig(OUT / name.replace(".png", ".pdf"), bbox_inches="tight")
    plt.close(fig)

# --- Fig 1: E-001 container expansion ---
metrics = ["面积比\n干预/基线", "面积增大\n比例", "IoU变化"]
vals = [1.222, 0.591, -0.083]
colors = ["#4C78A8", "#72B7B2", "#E45756"]
fig, ax = plt.subplots(figsize=(7.2, 4.2))
bars = ax.bar(metrics, vals, color=colors)
ax.axhline(0, color="black", lw=0.8)
ax.axhline(1, color="gray", lw=0.8, ls="--", label="面积比=1")
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v + (0.035 if v >= 0 else -0.055), f"{v:.3f}", ha="center", va="bottom" if v>=0 else "top")
ax.set_title("E-001：向外复制 object tokens 会扩大预测框")
ax.set_ylabel("数值")
ax.set_ylim(-0.18, 1.35)
ax.legend(frameon=False)
save(fig, "fig1_e001_container_expansion.png")

# --- Fig 2: R-014 dose effect ---
modes = ["baseline", "p25\nno-repeat", "p50\nno-repeat", "p75\nno-repeat", "p100\nno-repeat", "p100\nrepeat", "query\nshuffle"]
fpr = [0.148, 0.259, 0.259, 0.407, 0.444, 0.444, 0.000]
f1 = [0.931, 0.885, 0.885, 0.831, 0.818, 0.818, 0.981]
fig, ax = plt.subplots(figsize=(9.2, 4.8))
x = np.arange(len(modes))
bar_colors = ["#9E9E9E", "#FFCC80", "#FFB74D", "#FF8A65", "#E57373", "#BA68C8", "#64B5F6"]
bars = ax.bar(x, fpr, color=bar_colors)
ax.plot(x, f1, color="#2E7D32", marker="o", lw=2, label="F1")
for b, v in zip(bars, fpr):
    ax.text(b.get_x()+b.get_width()/2, v+0.015, f"{v:.3f}", ha="center")
for xi, v in zip(x, f1):
    ax.text(xi, v+0.018, f"{v:.3f}", ha="center", color="#2E7D32", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(modes)
ax.set_ylim(0, 1.08)
ax.set_ylabel("neg_FPR / F1")
ax.set_title("R-014：support-token contamination 的剂量效应")
ax.text(0.02, 0.94, "no-repeat: support tokens 不重复使用；其余 query tokens 保留", transform=ax.transAxes, fontsize=10)
ax.legend(frameon=False, loc="upper right")
save(fig, "fig2_r014_contamination_dose.png")

# --- Fig 3: replacement/contamination/shuffle comparison ---
labels = [
    "R-012\nreplace full",
    "R-014\np100 no-repeat",
    "R-014\np100 repeat",
    "R-014\nquery shuffle",
    "R-015\nsupport shuffle",
    "R-015\nquery shuffle",
    "R-015\nsupport+query shuffle",
    "R-015\nfull visual shuffle",
]
neg_fpr = [0.481, 0.444, 0.444, 0.000, 0.037, 0.037, 0.037, 1.000]
fig, ax = plt.subplots(figsize=(11.0, 5.0))
x = np.arange(len(labels))
colors = ["#D62728", "#E45756", "#B279A2", "#4C78A8", "#F58518", "#54A24B", "#72B7B2", "#000000"]
bars = ax.bar(x, neg_fpr, color=colors)
for b, v in zip(bars, neg_fpr):
    ax.text(b.get_x()+b.get_width()/2, v+0.025, f"{v:.3f}", ha="center")
ax.set_xticks(x); ax.set_xticklabels(labels, rotation=20, ha="right")
ax.set_ylim(0, 1.12)
ax.set_ylabel("negative false positive rate")
ax.set_title("E-002：reference-like token contamination 远强于 object-order shuffle")
ax.axhline(0.074, color="gray", ls="--", lw=1, label="R-015 baseline neg_FPR=0.074")
ax.legend(frameon=False)
save(fig, "fig3_e002_fpr_comparison.png")

# --- Fig 4: R-015 support/query shuffle separation ---
labels = ["baseline", "support\nshuffle", "query\nshuffle", "support+query\nshuffle", "full visual\nshuffle"]
fpr = [0.074, 0.037, 0.037, 0.037, 1.000]
f1 = [0.964, 0.982, 0.982, 0.982, 0.667]
fig, ax = plt.subplots(figsize=(8.4, 4.8))
x = np.arange(len(labels)); w = 0.36
b1 = ax.bar(x-w/2, fpr, w, label="neg_FPR", color="#E45756")
b2 = ax.bar(x+w/2, f1, w, label="F1", color="#4C78A8")
for bars in (b1, b2):
    for b in bars:
        v=b.get_height(); ax.text(b.get_x()+b.get_width()/2, v+0.018, f"{v:.3f}", ha="center", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylim(0, 1.12)
ax.set_title("R-015：support-only / query-only shuffle 均未破坏 POIL")
ax.set_ylabel("数值")
ax.legend(frameon=False)
save(fig, "fig4_r015_support_query_shuffle.png")

# --- Fig 5: synthesis schematic-like stacked statement ---
fig, ax = plt.subplots(figsize=(11, 4.4))
ax.axis("off")
items = [
    ("Container expansion", "E-001 R-004c：外圈复制 token → 面积比 1.222，59.1% 样本预测框变大", "#4C78A8"),
    ("Order shuffle", "R-015：support/query/support+query shuffle 的 neg_FPR 均为 0.037；不是主导机制", "#72B7B2"),
    ("Reference-like contamination", "R-014：no-repeat contamination 将 neg_FPR 从 0.148 提高到 0.444", "#E45756"),
    ("Global structure", "R-011/R-015：full visual shuffle 的 neg_FPR = 1.000，negative rejection 崩溃", "#000000"),
]
y = 0.86
for title, text, col in items:
    ax.add_patch(plt.Rectangle((0.03, y-0.075), 0.18, 0.11, color=col, alpha=0.9, transform=ax.transAxes))
    ax.text(0.12, y-0.02, title, color="white", weight="bold", ha="center", va="center", transform=ax.transAxes)
    ax.text(0.25, y-0.02, text, color="black", ha="left", va="center", transform=ax.transAxes, fontsize=12)
    y -= 0.20
ax.text(0.03, 0.04, "结论：当前证据更支持 containerized reference-matching：模型对内部 token 顺序相对鲁棒，\n但对全局视觉结构和 query object container 中的 support/reference-like evidence 高度敏感。", fontsize=13, weight="bold", transform=ax.transAxes)
save(fig, "fig5_synthesis_slide.png")

print(f"Wrote figures to: {OUT}")
for p in sorted(OUT.glob('fig*.png')):
    print(p)
