#!/usr/bin/env python3
"""Build a frozen category-held-out LaSOT FOCUS validation manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _categories(path: Path) -> Set[str]:
    values = {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    if not values:
        raise ValueError(f"category file is empty: {path}")
    return values


def _boxes(path: Path) -> List[List[float]]:
    result = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        values = [float(value) for value in line.replace("\t", ",").split(",")]
        if len(values) != 4:
            raise ValueError(f"{path}:{line_number}: expected xywh")
        x, y, width, height = values
        result.append([x, y, x + width, y + height])
    return result


def _indices(frame_count: int, shots: int) -> Tuple[List[int], int]:
    if shots < 1 or frame_count < shots + 1:
        raise ValueError("sequence has too few annotated frames")
    last_support = frame_count - 2
    support = (
        [0]
        if shots == 1
        else [round(index * last_support / (shots - 1)) for index in range(shots)]
    )
    if len(set(support)) != shots:
        raise ValueError("support sampling produced duplicate frames")
    return support, frame_count - 1


def _record(sequence_dir: Path, shots: int) -> Dict[str, Any]:
    boxes = _boxes(sequence_dir / "groundtruth.txt")
    support, query = _indices(len(boxes), shots)
    selected = support + [query]
    image_dir = sequence_dir / "img"
    image_paths = [image_dir / f"{index + 1:08d}.jpg" for index in selected]
    missing = [str(path) for path in image_paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing selected LaSOT frame: {missing[0]}")
    category = sequence_dir.name.rsplit("-", 1)[0]
    return {
        "element": "target-object",
        "image_path": [str(path.resolve()) for path in image_paths],
        "bbox": [boxes[index] for index in selected],
        "role": ["reference"] * shots + ["positive-image"],
        "dataset": "LaSOT",
        "sequence": sequence_dir.name,
        "frame_indices": selected,
        "sampling": "focus-uniform-full-span-final-query",
        "metadata": {
            "split": "validation",
            "category": category,
            "split_protocol": "e009-lasot-project-frozen-35-35/v1",
        },
    }


def build_validation_manifest(
    lasot_root: Path,
    train_manifest: Path,
    train_categories_path: Path,
    output: Path,
    audit_output: Path,
    *,
    shots: int = 1,
    expected_categories: int = 70,
    expected_train_categories: int = 35,
    expected_sequences_per_category: int = 20,
) -> Dict[str, Any]:
    paths = [lasot_root, train_manifest, train_categories_path]
    if not lasot_root.is_dir() or any(not path.is_file() for path in paths[1:]):
        raise FileNotFoundError("LaSOT root, train manifest, or category file is missing")
    if output.exists() or audit_output.exists():
        raise FileExistsError("refusing to overwrite validation manifest artifacts")

    train_categories = _categories(train_categories_path)
    category_sequences = {
        category_dir.name: sorted(category_dir.glob("*/groundtruth.txt"))
        for category_dir in lasot_root.iterdir()
        if category_dir.is_dir()
    }
    category_sequences = {
        category: paths for category, paths in category_sequences.items() if paths
    }
    available_categories = set(category_sequences)
    if len(available_categories) != expected_categories:
        raise ValueError(
            f"expected {expected_categories} LaSOT categories, "
            f"got {len(available_categories)}"
        )
    if len(train_categories) != expected_train_categories:
        raise ValueError(
            f"expected {expected_train_categories} train categories, "
            f"got {len(train_categories)}"
        )
    if not train_categories <= available_categories:
        raise ValueError("frozen train categories are absent from the LaSOT root")
    invalid_counts = {
        category: len(paths)
        for category, paths in category_sequences.items()
        if len(paths) != expected_sequences_per_category
    }
    if invalid_counts:
        raise ValueError(f"unexpected LaSOT sequence counts: {invalid_counts}")

    train_rows = json.loads(train_manifest.read_text(encoding="utf-8"))
    manifest_train_sequences = {
        str(row["sequence"])
        for row in train_rows
        if row.get("dataset") == "LaSOT"
    }
    manifest_train_categories = {
        sequence.rsplit("-", 1)[0] for sequence in manifest_train_sequences
    }
    if manifest_train_categories != train_categories:
        raise ValueError(
            "train manifest LaSOT categories do not match the frozen category file"
        )

    validation_categories = sorted(available_categories - train_categories)
    records = []
    for category in validation_categories:
        for annotation in category_sequences[category]:
            records.append(_record(annotation.parent, shots))
    validation_sequences = {str(row["sequence"]) for row in records}
    overlap = manifest_train_sequences & validation_sequences
    if overlap:
        raise RuntimeError(f"train/validation sequence leakage: {sorted(overlap)[:5]}")

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, output)
    audit = {
        "schema": "iploc-szy.focus-validation-split/v1",
        "status": "complete",
        "split_protocol": "e009-lasot-project-frozen-35-35/v1",
        "claim_boundary": (
            "Category- and sequence-held-out LaSOT validation for E-009. "
            "This project-frozen split is not attributed to the FOCUS authors."
        ),
        "shots": shots,
        "sampling": "focus-uniform-full-span-final-query",
        "train_manifest": str(train_manifest.resolve()),
        "train_manifest_sha256": _sha256(train_manifest),
        "train_categories_file": str(train_categories_path.resolve()),
        "train_categories_sha256": _sha256(train_categories_path),
        "validation_manifest": str(output.resolve()),
        "validation_manifest_sha256": _sha256(output),
        "counts": {
            "all_categories": len(available_categories),
            "train_categories": len(train_categories),
            "validation_categories": len(validation_categories),
            "train_lasot_sequences": len(manifest_train_sequences),
            "validation_sequences": len(validation_sequences),
            "sequence_overlap": len(overlap),
            "validation_records": len(records),
        },
        "train_categories": sorted(train_categories),
        "validation_categories": validation_categories,
    }
    audit_output.parent.mkdir(parents=True, exist_ok=True)
    temporary_audit = audit_output.with_suffix(audit_output.suffix + ".tmp")
    temporary_audit.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary_audit, audit_output)
    return audit


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lasot-root", type=Path, required=True)
    parser.add_argument("--train-manifest", type=Path, required=True)
    parser.add_argument("--train-categories", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit-output", type=Path, required=True)
    parser.add_argument("--shots", type=int, default=1)
    parser.add_argument("--expected-categories", type=int, default=70)
    parser.add_argument("--expected-train-categories", type=int, default=35)
    parser.add_argument("--expected-sequences-per-category", type=int, default=20)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    audit = build_validation_manifest(
        args.lasot_root.resolve(),
        args.train_manifest.resolve(),
        args.train_categories.resolve(),
        args.output.resolve(),
        args.audit_output.resolve(),
        shots=args.shots,
        expected_categories=args.expected_categories,
        expected_train_categories=args.expected_train_categories,
        expected_sequences_per_category=args.expected_sequences_per_category,
    )
    print(json.dumps(audit["counts"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
