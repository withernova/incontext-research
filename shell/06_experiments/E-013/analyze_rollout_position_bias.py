"""Read-only E-013 rollout analysis of candidate position and reported score."""

import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path


def first_argmax(values):
    return max(range(len(values)), key=values.__getitem__)


def mean(values):
    return statistics.fmean(values) if values else None


def median(values):
    return statistics.median(values) if values else None


def summarize(rows):
    if not rows:
        return {"n": 0}
    by_sample = defaultdict(list)
    for row in rows:
        by_sample[row["sample_id"]].append(row)
    return {
        "n": len(rows),
        "unique_samples": len({row["sample_id"] for row in rows}),
        "mean_scores": [mean([row["scores"][i] for row in rows]) for i in range(3)],
        "median_scores": [median([row["scores"][i] for row in rows]) for i in range(3)],
        "mean_ious": [mean([row["ious"][i] for row in rows]) for i in range(3)],
        "score_selected_counts": dict(sorted(Counter(row["selected"] + 1 for row in rows).items())),
        "score_selects_gt_best_rate": mean([row["selected"] == row["best"] for row in rows]),
        "first_mean_iou": mean([row["ious"][0] for row in rows]),
        "selected_mean_iou": mean([row["ious"][row["selected"]] for row in rows]),
        "oracle_mean_iou": mean([max(row["ious"]) for row in rows]),
        "selected_minus_first_mean_iou": mean(
            [row["ious"][row["selected"]] - row["ious"][0] for row in rows]
        ),
        "sample_equal_weight": {
            "mean_scores": [mean([mean([row["scores"][i] for row in group])
                                   for group in by_sample.values()]) for i in range(3)],
            "score_selects_gt_best_rate": mean([
                mean([row["selected"] == row["best"] for row in group])
                for group in by_sample.values()
            ]),
            "selected_minus_first_mean_iou": mean([
                mean([row["ious"][row["selected"]] - row["ious"][0] for row in group])
                for group in by_sample.values()
            ]),
        },
    }


def main(root):
    files = [root / "grpo" / f"rollouts-rank{i}.jsonl" for i in range(4)]
    missing = [str(path) for path in files if not path.is_file()]
    if missing:
        raise SystemExit("Missing required rollout files: " + ", ".join(missing))

    audit = Counter()
    rows = []
    sample_counts = Counter()
    by_rank = {}
    for rank, path in enumerate(files):
        rank_count = 0
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Malformed JSON: rank {rank} line {line_number}") from exc
                rank_count += 1
                audit["all_records"] += 1
                if record.get("target_present") is not True:
                    audit["excluded_no_gt"] += 1
                    continue
                audit["gt_present_records"] += 1
                reward = record.get("reward")
                if not isinstance(reward, dict):
                    audit["excluded_missing_reward"] += 1
                    continue
                scores = reward.get("scores")
                ious = reward.get("candidate_ious")
                if not isinstance(scores, list) or not isinstance(ious, list):
                    audit["excluded_missing_arrays"] += 1
                    continue
                if len(scores) != 3 or len(ious) != 3 or reward.get("candidate_count") != 3:
                    audit["excluded_not_three_candidates"] += 1
                    continue
                if any(
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(value)
                    or not 0 <= value <= 1
                    for value in scores + ious
                ):
                    audit["excluded_bad_number"] += 1
                    continue
                if reward.get("valid") not in (1, 1.0, True):
                    audit["excluded_invalid_output"] += 1
                    continue
                best = first_argmax(ious)
                selected = first_argmax(scores)
                tied_best = sum(value == ious[best] for value in ious) > 1
                sample_id = record.get("sample_id")
                if not isinstance(sample_id, str) or not sample_id:
                    audit["excluded_missing_sample_id"] += 1
                    continue
                reported_selected = reward.get("selected_index")
                if reported_selected != selected:
                    audit["reported_selection_mismatch"] += 1
                if record.get("terminated") is not True:
                    audit["included_not_terminated"] += 1
                if tied_best:
                    audit["included_tied_gt_best"] += 1
                sample_counts[sample_id] += 1
                rows.append(
                    {"sample_id": sample_id, "scores": scores, "ious": ious,
                     "best": best, "selected": selected, "tied_best": tied_best}
                )
                audit["included_three_candidate_records"] += 1
        by_rank[str(rank)] = rank_count

    if not rows:
        raise SystemExit("No valid positive three-candidate rollout records; audit=" + str(dict(audit)))
    if audit["reported_selection_mismatch"]:
        raise SystemExit(
            "Reported selected_index disagrees with score argmax; inspect its indexing convention "
            "before interpreting selection. Count=" + str(audit["reported_selection_mismatch"])
        )

    unique_best = [row for row in rows if not row["tied_best"]]
    groups = {
        str(position + 1): summarize([row for row in unique_best if row["best"] == position])
        for position in range(3)
    }
    second = [row for row in unique_best if row["best"] == 1]
    clear_second = [
        row for row in second if row["ious"][1] - row["ious"][0] >= 0.1
    ]

    def second_diagnostic(items):
        if not items:
            return {"n": 0}
        gaps = [row["scores"][0] - row["scores"][1] for row in items]
        return {
            "n": len(items),
            "mean_s1_minus_s2": mean(gaps),
            "median_s1_minus_s2": median(gaps),
            "s1_gt_s2_rate": mean([gap > 0 for gap in gaps]),
            "s1_eq_s2_rate": mean([gap == 0 for gap in gaps]),
            "s2_gt_s1_rate": mean([gap < 0 for gap in gaps]),
            "select_first_rate": mean([row["selected"] == 0 for row in items]),
            "select_second_rate": mean([row["selected"] == 1 for row in items]),
            "mean_best_minus_first_iou": mean([row["ious"][1] - row["ious"][0] for row in items]),
        }

    selection_matrix = {
        str(best + 1): {str(selected + 1): sum(
            row["best"] == best and row["selected"] == selected for row in unique_best
        ) for selected in range(3)} for best in range(3)
    }
    return {
        "source": "four rank rollout files in supplied E-013 branch only",
        "unit": "rollout record; repeated sample_id values are not independent",
        "selection_rule": "highest reported score, first on ties",
        "gt_best_rule": "highest candidate IoU; unique-best records in main groups",
        "rank_record_counts": by_rank,
        "audit": dict(sorted(audit.items())),
        "unique_sample_count": len(sample_counts),
        "repeated_sample_count": sum(count > 1 for count in sample_counts.values()),
        "all_included": summarize(rows),
        "unique_best_by_position": groups,
        "selection_by_gt_best": selection_matrix,
        "second_best_diagnostic": second_diagnostic(second),
        "second_best_iou_advantage_at_least_0_1": second_diagnostic(clear_second),
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python analyze_rollout_position_bias.py <branch-directory>")
    print(json.dumps(main(Path(sys.argv[1])), ensure_ascii=False, indent=2, sort_keys=True))
