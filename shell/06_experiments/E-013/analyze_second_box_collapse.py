"""Read-only offline diagnostics for an explicitly supplied E-013 training branch.

Run on the experiment server with Python 3; writes one JSON object to stdout.
"""

import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path


COMPONENTS = (
    "total", "iou", "coverage", "brier", "ranking_loss",
    "duplicate_penalty", "distractor_penalty", "score",
)


def finite_number(value):
    return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value)


def mean(values):
    return statistics.mean(values) if values else None


def percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    point = fraction * (len(ordered) - 1)
    low = math.floor(point)
    high = math.ceil(point)
    return ordered[low] + (ordered[high] - ordered[low]) * (point - low)


def wilson(successes, total):
    if not total:
        return None
    z = 1.959963984540054
    p = successes / total
    d = 1 + z * z / total
    c = (p + z * z / (2 * total)) / d
    h = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / d
    return [c - h, c + h]


def position_summary(rows):
    target = [r for r in rows if r["best"] == 1]
    hits = sum(r["selected"] == 1 for r in target)
    correct_pair = sum(r["margin"] > 0 for r in target)
    ties = sum(r["margin"] == 0 for r in target)
    return {
        "all_n": len(rows), "k2_n": len(target), "selected_2_n": hits,
        "selected_1_n": sum(r["selected"] == 0 for r in target),
        "selected_3_n": sum(r["selected"] == 2 for r in target),
        "p_selected_2": hits / len(target) if target else None,
        "p_selected_2_wilson95": wilson(hits, len(target)),
        "pair_correct_n": correct_pair,
        "p_pair_correct": correct_pair / len(target) if target else None,
        "pair_tie_n": ties,
        "top_score_tie_n": sum(r["scores_tied"] for r in target),
        "mean_margin": mean([r["margin"] for r in target]),
        "median_margin": statistics.median(r["margin"] for r in target) if target else None,
        "margin_q25": percentile([r["margin"] for r in target], 0.25),
        "margin_q75": percentile([r["margin"] for r in target], 0.75),
    }


def load_rollouts(branch):
    files = sorted((branch / "grpo").glob("rollouts-rank*.jsonl"))
    if not files:
        raise RuntimeError("No rollout JSONL files in supplied branch")
    audit = Counter()
    rows = []
    for path in files:
        with path.open() as handle:
            for line in handle:
                if not line.strip():
                    continue
                audit["raw"] += 1
                x = json.loads(line)
                reward = x.get("reward")
                if not isinstance(reward, dict):
                    audit["missing_reward"] += 1
                    continue
                if x.get("target_present") is not True:
                    audit["target_absent"] += 1
                    continue
                if reward.get("valid") is not True:
                    audit["invalid_output"] += 1
                    continue
                scores = reward.get("scores")
                ious = reward.get("candidate_ious")
                if not isinstance(scores, list) or not isinstance(ious, list) or len(scores) != 3 or len(ious) != 3:
                    audit["missing_three_candidates"] += 1
                    continue
                if not all(finite_number(v) and 0 <= v <= 1 for v in scores + ious):
                    audit["bad_scores_or_ious"] += 1
                    continue
                if not isinstance(x.get("step"), int) or not isinstance(x.get("sample_id"), str):
                    audit["missing_step_or_sample"] += 1
                    continue
                if not x.get("terminated"):
                    audit["not_terminated"] += 1
                best_value = max(ious)
                if ious.count(best_value) != 1:
                    audit["tied_best"] += 1
                    continue
                best = ious.index(best_value)
                selected = scores.index(max(scores))
                if reward.get("selected_index") != selected:
                    audit["selected_index_mismatch"] += 1
                    continue
                row = {
                    "step": x["step"], "sample_id": x["sample_id"],
                    "best": best, "selected": selected,
                    "margin": scores[1] - scores[0],
                    "iou_gap": ious[1] - ious[0],
                    "scores_tied": scores.count(max(scores)) != 1,
                    "advantage": x.get("advantage"),
                    "reward": {k: reward.get(k) for k in COMPONENTS},
                }
                rows.append(row)
                audit["included"] += 1
    return files, rows, dict(audit)


def rollout_analysis(rows):
    by_step = defaultdict(list)
    by_window = defaultdict(list)
    for row in rows:
        by_step[row["step"]].append(row)
        by_window[25 * (row["step"] // 25)].append(row)
    steps = [{"step": s, **position_summary(v)} for s, v in sorted(by_step.items())]
    windows = [{"step_start": s, "step_end": s + 24, **position_summary(v)}
               for s, v in sorted(by_window.items())]

    second = [r for r in rows if r["best"] == 1]
    edges = (0, 0.05, 0.1, 0.2, 0.4, 1.0000001)
    iou_bins = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        sub = [r for r in second if lo <= r["iou_gap"] < hi]
        iou_bins.append({"lo": lo, "hi": min(hi, 1), **position_summary(sub)})

    categories = {
        "second_above_first": [r for r in second if r["margin"] > 0],
        "first_above_second": [r for r in second if r["margin"] < 0],
        "equal": [r for r in second if r["margin"] == 0],
    }
    comparison = {}
    for label, sub in categories.items():
        comparison[label] = {
            "n": len(sub),
            "distinct_sample_ids": len({r["sample_id"] for r in sub}),
            "mean_advantage": mean([r["advantage"] for r in sub if finite_number(r["advantage"])]),
            "advantage_n": sum(finite_number(r["advantage"]) for r in sub),
            "components": {k: {"n": sum(finite_number(r["reward"][k]) for r in sub),
                               "mean": mean([r["reward"][k] for r in sub if finite_number(r["reward"][k])])}
                           for k in COMPONENTS},
        }

    groups = defaultdict(list)
    for r in second:
        groups[(r["step"], r["sample_id"])].append(r)
    group_diffs = []
    for group in groups.values():
        pos = [r for r in group if r["margin"] > 0]
        neg = [r for r in group if r["margin"] < 0]
        if not pos or not neg:
            continue
        d = {}
        for k in COMPONENTS:
            a = [r["reward"][k] for r in pos if finite_number(r["reward"][k])]
            b = [r["reward"][k] for r in neg if finite_number(r["reward"][k])]
            d[k] = mean(a) - mean(b) if a and b else None
        a = [r["advantage"] for r in pos if finite_number(r["advantage"])]
        b = [r["advantage"] for r in neg if finite_number(r["advantage"])]
        d["advantage"] = mean(a) - mean(b) if a and b else None
        group_diffs.append(d)

    random.seed(20260929)
    paired = {}
    for k in (*COMPONENTS, "advantage"):
        values = [d[k] for d in group_diffs if d[k] is not None]
        if values:
            boot = sorted(mean(random.choices(values, k=len(values))) for _ in range(2000))
            paired[k] = {"n_groups": len(values), "mean_difference": mean(values),
                         "bootstrap95": [boot[50], boot[1949]]}
        else:
            paired[k] = {"n_groups": 0, "mean_difference": None, "bootstrap95": None}
    return {"step": steps, "step_window_25": windows, "iou_gap_bins": iou_bins,
            "ranking_reward": comparison, "within_step_sample_group_difference": paired,
            "mixed_groups": len(group_diffs), "total_k2_groups": len(groups)}


def eval_analysis(eval_branch):
    path = eval_branch / "evaluation" / "predictions.jsonl"
    if not path.exists():
        return {"available": False}
    rows = []
    audit = Counter()
    with path.open() as handle:
        for line in handle:
            if not line.strip():
                continue
            audit["raw"] += 1
            x = json.loads(line)
            candidates = x.get("candidates")
            if not isinstance(candidates, list) or len(candidates) != 3:
                audit["not_three_candidates"] += 1
                continue
            scores = [c.get("score") for c in candidates]
            ious = [c.get("iou") for c in candidates]
            if not all(finite_number(v) and 0 <= v <= 1 for v in scores + ious):
                audit["bad_scores_or_ious"] += 1
                continue
            if ious.count(max(ious)) != 1:
                audit["tied_best"] += 1
                continue
            best = ious.index(max(ious))
            selected = scores.index(max(scores))
            if x.get("selected_candidate_index") != selected:
                audit["selected_index_mismatch"] += 1
                continue
            rows.append({"best": best, "selected": selected,
                         "margin": scores[1] - scores[0],
                         "iou_gap": ious[1] - ious[0],
                         "scores_tied": scores.count(max(scores)) != 1})
            audit["included"] += 1
    return {"available": True, "audit": dict(audit), **position_summary(rows)}


def main():
    branch = Path(sys.argv[1])
    eval_branch = Path(sys.argv[2])
    files, rows, audit = load_rollouts(branch)
    result = {
        "training_branch": branch.name,
        "rollout_files": [f.name for f in files],
        "rollout_audit": audit,
        "rollout_step_range": [min(r["step"] for r in rows), max(r["step"] for r in rows)],
        "rollout": rollout_analysis(rows),
        "evaluation_branch": eval_branch.name,
        "evaluation": eval_analysis(eval_branch),
        "scope": "Training rollout curve uses changing sampled prompts/candidates; evaluation is one fixed checkpoint only.",
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
