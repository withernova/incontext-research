#!/usr/bin/env python3
"""Filter non-positive reference/target boxes from one E-009 manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

from PIL import Image

from iploc_szy.prompting.coordinates import parse_box, pixel_to_normalized


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def unwrap(value: Any) -> Any:
    return value[0] if isinstance(value, list) and len(value) == 1 else value


def invalid_used_boxes(
    row: Mapping[str, Any], target_role: str = "positive-image"
) -> List[Dict[str, Any]]:
    paths = [unwrap(value) for value in row.get("image_path", [])]
    boxes = [unwrap(value) for value in row.get("bbox", [])]
    raw_roles = row.get("role") or row.get("data_role")
    if raw_roles is None:
        raw_roles = ["reference"] * (len(paths) - 1) + [target_role]
    roles = [unwrap(value) for value in raw_roles]
    if not paths or not (len(paths) == len(boxes) == len(roles)):
        raise ValueError("manifest row has inconsistent path/bbox/role lengths")

    invalid = []
    for position, (path, box, role) in enumerate(zip(paths, boxes, roles)):
        if role not in {"reference", target_role}:
            continue
        parsed = parse_box(box)
        reason = "unparseable"
        normalized = None
        image_size = None
        if parsed is not None:
            x1, y1, x2, y2 = parsed
            if x2 <= x1 or y2 <= y1:
                reason = "nonpositive_area"
            else:
                with Image.open(path) as image:
                    image_size = tuple(map(int, image.size))
                normalized = pixel_to_normalized(parsed, image_size)
                nx1, ny1, nx2, ny2 = normalized
                if nx2 <= nx1 or ny2 <= ny1:
                    reason = "nonpositive_after_normalization"
                elif min(1000, nx2) <= max(0, nx1) or min(1000, ny2) <= max(0, ny1):
                    reason = "zero_intersection_with_normalized_image_plane"
                else:
                    reason = ""
        if reason:
            invalid.append(
                {
                    "position": position,
                    "role": str(role),
                    "box": box,
                    "normalized_box": normalized,
                    "image_size": image_size,
                    "reason": reason,
                }
            )
    return invalid


def filter_manifest(
    source: Path,
    output: Path,
    audit_output: Path,
    *,
    target_role: str = "positive-image",
    expected_output_count: Optional[int] = None,
) -> Dict[str, Any]:
    existing = [str(path) for path in (output, audit_output) if path.exists()]
    if existing:
        raise FileExistsError(f"refusing to overwrite valid-bbox artifacts: {existing}")
    rows = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not rows or any(
        not isinstance(row, Mapping) for row in rows
    ):
        raise ValueError("source manifest must be a non-empty JSON object list")

    kept = []
    dropped = []
    for source_index, row in enumerate(rows):
        invalid = invalid_used_boxes(row, target_role)
        if invalid:
            dropped.append(
                {
                    "source_index": source_index,
                    "dataset": row.get("dataset"),
                    "sequence": row.get("sequence"),
                    "invalid_boxes": invalid,
                }
            )
        else:
            kept.append(dict(row))
    if not kept:
        raise ValueError("valid-bbox filter produced zero rows")
    if expected_output_count is not None and len(kept) != expected_output_count:
        raise ValueError(
            f"valid-bbox count mismatch: got {len(kept)}, "
            f"expected {expected_output_count}"
        )

    output_bytes = (json.dumps(kept, ensure_ascii=False, indent=2) + "\n").encode()
    audit = {
        "schema": "iploc-szy.e009-valid-bbox-filter/v1",
        "status": "complete",
        "target_role": target_role,
        "policy": "drop_rows_with_unparseable_nonpositive_or_zero_image_intersection_reference_or_target_box",
        "source": {
            "manifest": str(source.resolve()),
            "sha256": sha256_file(source),
            "rows": len(rows),
        },
        "output": {
            "manifest": str(output.resolve()),
            "sha256": sha256_bytes(output_bytes),
            "rows": len(kept),
        },
        "dropped_count": len(dropped),
        "dropped": dropped,
        "claim_boundary": (
            "The output preserves the source order and only removes rows whose "
            "reference or positive target bbox cannot define positive-area spatial "
            "occupancy within the normalized image plane. It does not replace rows or restore the intended last valid frame."
        ),
    }
    audit_bytes = (json.dumps(audit, ensure_ascii=False, indent=2) + "\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    audit_output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(output_bytes)
    audit_output.write_bytes(audit_bytes)
    return audit


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit-output", type=Path, required=True)
    parser.add_argument("--target-role", default="positive-image")
    parser.add_argument("--expected-output-count", type=int)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    audit = filter_manifest(
        args.source.resolve(),
        args.output.resolve(),
        args.audit_output.resolve(),
        target_role=args.target_role,
        expected_output_count=args.expected_output_count,
    )
    print(
        json.dumps(
            {
                "source_rows": audit["source"]["rows"],
                "output_rows": audit["output"]["rows"],
                "dropped_count": audit["dropped_count"],
                "dropped_source_indices": [
                    row["source_index"] for row in audit["dropped"]
                ],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
