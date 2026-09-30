"""Render dependency-free SVG figures from the E-013 aggregate JSON."""

import json
import sys
from pathlib import Path


def svg_start(width, height, title):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
            '<rect width="100%" height="100%" fill="white"/>',
            f'<text x="45" y="36" font-size="22" font-family="sans-serif" font-weight="bold">{title}</text>']


def line(parts, x1, y1, x2, y2, color="#333", width=1, extra=""):
    parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}" {extra}/>')


def text(parts, x, y, value, size=13, color="#222", anchor="start"):
    parts.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" font-family="sans-serif" text-anchor="{anchor}">{value}</text>')


def circle(parts, x, y, radius, color):
    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{color}"/>')


def save(path, parts):
    path.write_text("\n".join(parts + ["</svg>"]) + "\n")


def axes(parts, left, top, right, bottom, yticks, ymap, xlabel, ylabel):
    line(parts, left, top, left, bottom)
    line(parts, left, bottom, right, bottom)
    for v in yticks:
        y = ymap(v)
        line(parts, left, y, right, y, "#e5e7eb")
        text(parts, left - 10, y + 4, f"{v:g}", 12, anchor="end")
    text(parts, (left + right) / 2, bottom + 48, xlabel, 14, anchor="middle")
    text(parts, left, top - 12, ylabel, 14)


def plot_curve(data, out):
    parts = svg_start(1100, 610, "Second-box selection by training step")
    left, right, top, bottom = 85, 1035, 80, 505
    xm = lambda s: left + (right - left) * s / 475
    ym = lambda p: bottom - (bottom - top) * p
    axes(parts, left, top, right, bottom, [0, .2, .4, .6, .8, 1], ym,
         "Training step (rollouts generated before update)", "P(selected box 2 | unique best box 2)")
    for s in range(0, 476, 50):
        x = xm(s)
        line(parts, x, bottom, x, bottom + 5)
        text(parts, x, bottom + 23, str(s), 12, anchor="middle")
    for row in data["rollout"]["step"]:
        if row["k2_n"]:
            circle(parts, xm(row["step"]), ym(row["p_selected_2"]), 2, "#bdc5cf")
    windows = [r for r in data["rollout"]["step_window_25"] if r["k2_n"]]
    points = [((r["step_start"] + min(r["step_end"], 469)) / 2, r) for r in windows]
    for (s1, a), (s2, b) in zip(points, points[1:]):
        line(parts, xm(s1), ym(a["p_selected_2"]), xm(s2), ym(b["p_selected_2"]), "#175cd3", 2.5)
    for s, row in points:
        x, y = xm(s), ym(row["p_selected_2"])
        lo, hi = row["p_selected_2_wilson95"]
        line(parts, x, ym(lo), x, ym(hi), "#6b9be8", 1.5)
        circle(parts, x, y, 4, "#175cd3")
    ev = data["evaluation"]
    if ev["available"] and ev["k2_n"]:
        x, y = xm(450), ym(ev["p_selected_2"])
        lo, hi = ev["p_selected_2_wilson95"]
        line(parts, x, ym(lo), x, ym(hi), "#d13d31", 2.5)
        circle(parts, x, y, 6, "#d13d31")
        text(parts, x - 10, max(top + 20, y - 22), f'fixed eval: {ev["selected_2_n"]}/{ev["k2_n"]}', 13, "#a42f26", "end")
    text(parts, left, 572, "Gray: raw step   Blue: 25-step pooled training rollouts + Wilson 95%   Red: existing step-450 evaluation", 13)
    save(out, parts)


def plot_margin(data, out):
    parts = svg_start(1100, 850, "Score margin and IoU-gap ranking")
    left, right = 85, 1035
    top, bottom = 85, 390
    xm = lambda s: left + (right - left) * s / 475
    ym = lambda v: bottom - (bottom - top) * (v + 1) / 2
    axes(parts, left, top, right, bottom, [-1, -.5, 0, .5, 1], ym,
         "Training step (25-step pools)", "Delta score = score2 - score1")
    line(parts, left, ym(0), right, ym(0), "#777", 1.5)
    windows = [r for r in data["rollout"]["step_window_25"] if r["k2_n"]]
    for row in windows:
        s = (row["step_start"] + min(row["step_end"], 469)) / 2
        x = xm(s)
        line(parts, x, ym(row["margin_q25"]), x, ym(row["margin_q75"]), "#87a9df", 5)
        circle(parts, x, ym(row["median_margin"]), 4, "#175cd3")
        text(parts, x, bottom + 21, str(row["step_start"]), 10, anchor="middle")
    text(parts, left, 440, "Dots: median margin; bars: interquartile range. Zero means score tie.", 13)

    top2, bottom2 = 500, 760
    ym2 = lambda p: bottom2 - (bottom2 - top2) * p
    axes(parts, left, top2, right, bottom2, [0, .25, .5, .75, 1], ym2,
         "Delta IoU = IoU2 - IoU1 (fixed bins)", "Ranking / selection rate")
    bins = data["rollout"]["iou_gap_bins"]
    width = (right - left) / len(bins)
    for i, row in enumerate(bins):
        cx = left + width * (i + .5)
        for offset, key, color in [(-16, "p_pair_correct", "#175cd3"), (16, "p_selected_2", "#d13d31")]:
            val = row[key] or 0
            parts.append(f'<rect x="{cx + offset - 12:.1f}" y="{ym2(val):.1f}" width="24" height="{bottom2 - ym2(val):.1f}" fill="{color}"/>')
        text(parts, cx, bottom2 + 18, f'{row["lo"]:g}-{row["hi"]:g}', 11, anchor="middle")
        text(parts, cx, top2 - 8, f'n={row["k2_n"]}', 11, anchor="middle")
    text(parts, 710, 474, "Blue: score2 > score1    Red: box 2 selected", 13)
    save(out, parts)


def plot_reward(data, out):
    parts = svg_start(1100, 620, "Training rollout reward and advantage by pairwise order")
    left, right, top, bottom = 85, 1035, 95, 490
    ym = lambda v: bottom - (bottom - top) * (v + 1) / 2.25
    axes(parts, left, top, right, bottom, [-1, -.5, 0, .5, 1], ym,
         "Reward component / group-normalized advantage", "Mean per rollout")
    line(parts, left, ym(0), right, ym(0), "#777", 1.4)
    labels = ["total", "iou", "brier", "ranking_loss", "advantage"]
    comp = data["rollout"]["ranking_reward"]
    a = comp["second_above_first"]
    b = comp["first_above_second"]
    for i, label in enumerate(labels):
        cx = left + (right - left) * (i + .5) / len(labels)
        for offset, group, color in [(-22, a, "#175cd3"), (22, b, "#d13d31")]:
            value = group["mean_advantage"] if label == "advantage" else group["components"][label]["mean"]
            y = ym(value)
            parts.append(f'<rect x="{cx + offset - 17:.1f}" y="{min(y, ym(0)):.1f}" width="34" height="{abs(ym(0) - y):.1f}" fill="{color}"/>')
            text(parts, cx + offset, y - 7 if value >= 0 else y + 17, f"{value:.2f}", 11, anchor="middle")
        text(parts, cx, bottom + 25, label, 12, anchor="middle")
    text(parts, left, 560, f'Blue: score2 > score1 (n={a["n"]})    Red: score1 > score2 (n={b["n"]}); score ties excluded', 13)
    text(parts, left, 582, f'Within-prompt mixed groups: {data["rollout"]["mixed_groups"]} / {data["rollout"]["total_k2_groups"]}; raw component means are observational.', 13)
    save(out, parts)


def main():
    source = Path(sys.argv[1])
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    data = json.loads(source.read_text())
    plot_curve(data, out / "training_curve.svg")
    plot_margin(data, out / "score_margin_and_iou_gap.svg")
    plot_reward(data, out / "reward_advantage.svg")


if __name__ == "__main__":
    main()
