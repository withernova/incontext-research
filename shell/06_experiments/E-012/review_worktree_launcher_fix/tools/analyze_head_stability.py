#!/usr/bin/env python3
"""Compare fixed Top-k head sets from ordered standalone screening runs."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--screen",
        action="append",
        required=True,
        metavar="LABEL=LATEST_JSON",
        help="ordered checkpoint label and head_screening/latest.json path",
    )
    parser.add_argument("--output", required=True, help="summary JSON path")
    return parser.parse_args(argv)


def parse_screen(value: str) -> Tuple[str, Path]:
    label, separator, raw_path = value.partition("=")
    if not separator or not label or not raw_path:
        raise ValueError(f"--screen must be LABEL=PATH, got {value!r}")
    return label, Path(raw_path).resolve()


def jaccard(first: Iterable[str], second: Iterable[str]) -> float:
    first_set, second_set = set(first), set(second)
    union = first_set | second_set
    return len(first_set & second_set) / len(union) if union else 1.0


def sample_identity(payload: Mapping[str, Any]) -> List[Tuple[int, str]]:
    records = payload.get("probe_records")
    if not isinstance(records, list) or not records:
        raise ValueError("screen has no non-empty probe_records")
    identity = []
    for record in records:
        if "dataset_index" not in record or "sample_id" not in record:
            raise ValueError("probe record is missing dataset_index or sample_id")
        identity.append((int(record["dataset_index"]), str(record["sample_id"])))
    return sorted(identity)


def selected_sets(payload: Mapping[str, Any]) -> Dict[str, Dict[str, List[str]]]:
    raw = payload.get("selected_sets")
    if not isinstance(raw, Mapping) or not raw:
        raise ValueError("screen has no selected_sets")
    output: Dict[str, Dict[str, List[str]]] = {}
    for role, counts in raw.items():
        if not isinstance(counts, Mapping) or not counts:
            raise ValueError(f"selected_sets[{role!r}] is empty")
        output[str(role)] = {}
        for count, heads in counts.items():
            expected = int(count)
            values = list(map(str, heads))
            if len(values) != expected or len(set(values)) != expected:
                raise ValueError(
                    f"selected_sets[{role!r}][{count!r}] is not a unique Top-{expected}"
                )
            output[str(role)][str(count)] = values
    return output


def compatibility_signature(payload: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "schema": payload.get("schema"),
        "row_contract": payload.get("row_contract"),
        "head_shape": payload.get("head_shape"),
        "parameters": payload.get("parameters"),
        "sample_identity": sample_identity(payload),
        "selected_roles_and_counts": {
            role: sorted(counts, key=int)
            for role, counts in selected_sets(payload).items()
        },
    }


def load_screens(values: Sequence[str]) -> List[Dict[str, Any]]:
    if len(values) < 2:
        raise ValueError("at least two ordered --screen values are required")
    loaded = []
    labels = set()
    for value in values:
        label, path = parse_screen(value)
        if label in labels:
            raise ValueError(f"duplicate screen label: {label}")
        labels.add(label)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("status") != "completed":
            raise ValueError(f"screen {label!r} is not completed")
        record_count = int(payload.get("records", -1))
        if record_count <= 0 or record_count != len(payload.get("probe_records", [])):
            raise ValueError(f"screen {label!r} has inconsistent record counts")
        loaded.append(
            {
                "label": label,
                "path": str(path),
                "payload": payload,
                "sets": selected_sets(payload),
                "signature": compatibility_signature(payload),
            }
        )
    baseline = loaded[0]["signature"]
    for screen in loaded[1:]:
        if screen["signature"] != baseline:
            raise ValueError(
                f"screen {screen['label']!r} is not comparable with "
                f"{loaded[0]['label']!r}"
            )
    return loaded


def summarize_set_series(
    labels: Sequence[str], sets: Sequence[Sequence[str]]
) -> Dict[str, Any]:
    adjacent = []
    for index in range(1, len(sets)):
        adjacent.append(
            {
                "from": labels[index - 1],
                "to": labels[index],
                "jaccard": jaccard(sets[index - 1], sets[index]),
                "intersection": sorted(set(sets[index - 1]) & set(sets[index])),
            }
        )
    frequencies = Counter(head for values in sets for head in values)
    all_intersection = set(sets[0]).intersection(*map(set, sets[1:]))
    union = set().union(*map(set, sets))
    exact_matches = sum(set(values) == set(sets[0]) for values in sets[1:])
    return {
        "per_checkpoint": [
            {"checkpoint": label, "heads": list(values)}
            for label, values in zip(labels, sets)
        ],
        "adjacent": adjacent,
        "adjacent_jaccard_min": min(item["jaccard"] for item in adjacent),
        "adjacent_jaccard_mean": sum(item["jaccard"] for item in adjacent)
        / len(adjacent),
        "exact_match_to_first_fraction": exact_matches / (len(sets) - 1),
        "all_checkpoint_intersection": sorted(all_intersection),
        "all_checkpoint_union": sorted(union),
        "head_frequency": [
            {"head": head, "checkpoints": count, "fraction": count / len(sets)}
            for head, count in sorted(
                frequencies.items(), key=lambda item: (-item[1], item[0])
            )
        ],
    }


def analyze(screens: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    labels = [str(screen["label"]) for screen in screens]
    first_sets = screens[0]["sets"]
    roles = {}
    for role, counts in first_sets.items():
        roles[role] = {}
        for count in sorted(counts, key=int):
            series = [screen["sets"][role][count] for screen in screens]
            roles[role][count] = summarize_set_series(labels, series)
    signature = screens[0]["signature"]
    return {
        "schema": "iploc-szy.cross-checkpoint-head-stability/v1",
        "status": "completed",
        "checkpoint_order": labels,
        "screen_count": len(screens),
        "comparability": {
            "passed": True,
            "screen_schema": signature["schema"],
            "row_contract": signature["row_contract"],
            "head_shape": signature["head_shape"],
            "parameters": signature["parameters"],
            "sample_count": len(signature["sample_identity"]),
            "sample_identity_equal": True,
        },
        "roles": roles,
        "claim_boundary": (
            "Descriptive cross-checkpoint stability of fixed teacher-forced attention "
            "head sets on one frozen manifest. It does not establish causal head function, "
            "generalization to the reserved test split, or automatic checkpoint selection."
        ),
    }


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    screens = load_screens(args.screen)
    summary = analyze(screens)
    write_json(Path(args.output), summary)
    print(json.dumps(summary, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
