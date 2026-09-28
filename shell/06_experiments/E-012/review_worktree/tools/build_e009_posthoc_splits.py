#!/usr/bin/env python3
"""Freeze post-hoc E-009 validation/test manifests without training overlap."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _load_rows(path: Path) -> List[Dict[str, Any]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"manifest must be a non-empty JSON list: {path}")
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"manifest rows must be objects: {path}")
    return rows


def _sequences(rows: Iterable[Dict[str, Any]]) -> Set[str]:
    result = set()
    for row in rows:
        dataset = str(row.get("dataset", ""))
        sequence = str(row.get("sequence", ""))
        if not dataset or not sequence:
            raise ValueError("every row must contain dataset and sequence")
        result.add(f"{dataset}::{sequence}")
    return result


def _images(rows: Iterable[Dict[str, Any]]) -> Set[str]:
    result = set()
    for row in rows:
        paths = row.get("image_path")
        if not isinstance(paths, list) or not paths:
            raise ValueError("every row must contain a non-empty image_path list")
        result.update(str(path) for path in paths)
    return result


def _with_split(row: Dict[str, Any], split: str) -> Dict[str, Any]:
    copied = dict(row)
    metadata = dict(copied.get("metadata") or {})
    metadata.update(
        {
            "split": split,
            "split_protocol": "e009-posthoc-lasot-val100-test600/v1",
        }
    )
    copied["metadata"] = metadata
    return copied


def _overlap(left: Set[str], right: Set[str]) -> int:
    return len(left & right)


def build_posthoc_splits(
    train_manifest: Path,
    source_pool: Path,
    val_output: Path,
    test_output: Path,
    audit_output: Path,
    *,
    val_size: int = 100,
    seed: int = 20260901,
) -> Dict[str, Any]:
    outputs = (val_output, test_output, audit_output)
    existing = [str(path) for path in outputs if path.exists()]
    if existing:
        raise FileExistsError(f"refusing to overwrite split artifacts: {existing}")

    train_rows = _load_rows(train_manifest)
    pool_rows = _load_rows(source_pool)
    if val_size < 1 or val_size >= len(pool_rows):
        raise ValueError("val_size must leave non-empty validation and test splits")
    if len(_sequences(pool_rows)) != len(pool_rows):
        raise ValueError("source pool contains duplicate dataset/sequence rows")

    selected_indices = sorted(random.Random(seed).sample(range(len(pool_rows)), val_size))
    selected = set(selected_indices)
    val_rows = [_with_split(pool_rows[index], "validation") for index in selected_indices]
    test_rows = [
        _with_split(row, "test")
        for index, row in enumerate(pool_rows)
        if index not in selected
    ]

    train_sequences, val_sequences, test_sequences = map(
        _sequences, (train_rows, val_rows, test_rows)
    )
    train_images, val_images, test_images = map(_images, (train_rows, val_rows, test_rows))
    overlap = {
        "sequence": {
            "train_val": _overlap(train_sequences, val_sequences),
            "train_test": _overlap(train_sequences, test_sequences),
            "val_test": _overlap(val_sequences, test_sequences),
        },
        "image": {
            "train_val": _overlap(train_images, val_images),
            "train_test": _overlap(train_images, test_images),
            "val_test": _overlap(val_images, test_images),
        },
    }
    if any(value for kind in overlap.values() for value in kind.values()):
        raise RuntimeError(f"split leakage detected: {overlap}")

    val_bytes = (json.dumps(val_rows, ensure_ascii=False, indent=2) + "\n").encode()
    test_bytes = (json.dumps(test_rows, ensure_ascii=False, indent=2) + "\n").encode()
    audit = {
        "schema": "iploc-szy.e009-posthoc-splits/v1",
        "status": "complete",
        "protocol": "e009-posthoc-lasot-val100-test600/v1",
        "claim_boundary": (
            "Project-specific post-hoc split preserving the 100 LaSOT rows already used "
            "for validation and reserving the remaining rows as test. It has no sequence "
            "or image overlap with the recorded E-009 training manifest, but is not the "
            "exact IPLoc or FOCUS protocol and cannot undo prior data exposure."
        ),
        "selection": {
            "method": "seeded_random_without_replacement_then_sorted",
            "seed": seed,
            "validation_size": val_size,
            "selected_source_indices": selected_indices,
        },
        "counts": {
            "train_rows": len(train_rows),
            "source_pool_rows": len(pool_rows),
            "validation_rows": len(val_rows),
            "test_rows": len(test_rows),
        },
        "overlap": overlap,
        "sources": {
            "train_manifest": str(train_manifest.resolve()),
            "train_manifest_sha256": _sha256(train_manifest),
            "source_pool": str(source_pool.resolve()),
            "source_pool_sha256": _sha256(source_pool),
        },
        "outputs": {
            "validation_manifest": str(val_output.resolve()),
            "validation_manifest_sha256": _sha256_bytes(val_bytes),
            "test_manifest": str(test_output.resolve()),
            "test_manifest_sha256": _sha256_bytes(test_bytes),
        },
    }
    audit_bytes = (json.dumps(audit, ensure_ascii=False, indent=2) + "\n").encode()
    for path in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
    val_output.write_bytes(val_bytes)
    test_output.write_bytes(test_bytes)
    audit_output.write_bytes(audit_bytes)
    return audit


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-manifest", type=Path, required=True)
    parser.add_argument("--source-pool", type=Path, required=True)
    parser.add_argument("--val-output", type=Path, required=True)
    parser.add_argument("--test-output", type=Path, required=True)
    parser.add_argument("--audit-output", type=Path, required=True)
    parser.add_argument("--val-size", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260901)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    audit = build_posthoc_splits(
        args.train_manifest.resolve(),
        args.source_pool.resolve(),
        args.val_output.resolve(),
        args.test_output.resolve(),
        args.audit_output.resolve(),
        val_size=args.val_size,
        seed=args.seed,
    )
    print(json.dumps({"counts": audit["counts"], "overlap": audit["overlap"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
