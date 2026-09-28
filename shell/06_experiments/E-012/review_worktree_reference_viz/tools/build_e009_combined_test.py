#!/usr/bin/env python3
"""Build E-009 GOT-val, TAO-validation, and combined post-hoc test manifests."""

from __future__ import annotations

import argparse
import configparser
import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json_list(path: Path) -> List[Dict[str, Any]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"expected non-empty JSON list: {path}")
    return rows


def _boxes(path: Path) -> List[List[float]]:
    result = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        x, y, width, height = [float(value) for value in line.replace("\t", ",").split(",")]
        result.append([x, y, x + width, y + height])
    return result


def _labels(path: Path, count: int, default: int) -> List[int]:
    if not path.is_file():
        return [default] * count
    values = [int(value) for value in path.read_text().splitlines() if value.strip()]
    if len(values) != count:
        raise ValueError(f"label/annotation length mismatch: {path}")
    return values


def _got_category(sequence_dir: Path) -> str:
    parser = configparser.ConfigParser()
    parser.read(sequence_dir / "meta_info.ini")
    if not parser.has_option("METAINFO", "object_class"):
        raise ValueError(f"missing GOT object_class: {sequence_dir}")
    return parser.get("METAINFO", "object_class").strip()


def build_got_val(got_root: Path) -> List[Dict[str, Any]]:
    rows = []
    for sequence_dir in sorted((got_root / "val").glob("GOT-10k_Val_*")):
        boxes = _boxes(sequence_dir / "groundtruth.txt")
        absence = _labels(sequence_dir / "absence.label", len(boxes), 0)
        cover = _labels(sequence_dir / "cover.label", len(boxes), 1)
        usable = [i for i, (absent, visible) in enumerate(zip(absence, cover)) if absent == 0 and visible > 0]
        if len(usable) < 2:
            continue
        support, query = usable[0], usable[-1]
        paths = [sequence_dir / f"{support + 1:08d}.jpg", sequence_dir / f"{query + 1:08d}.jpg"]
        if any(not path.is_file() for path in paths):
            raise FileNotFoundError(paths)
        rows.append({
            "element": "target-object",
            "image_path": [str(path.resolve()) for path in paths],
            "bbox": [boxes[support], boxes[query]],
            "role": ["reference", "positive-image"],
            "dataset": "GOT10k",
            "sequence": sequence_dir.name,
            "frame_indices": [support, query],
            "sampling": "first-last-valid-annotated-frame",
            "metadata": {"split": "test", "source_split": "official-validation", "category": _got_category(sequence_dir), "split_protocol": "e009-posthoc-combined-test/v1"},
        })
    if not rows:
        raise ValueError("GOT validation produced zero episodes")
    return rows


def build_tao_validation(tao_root: Path) -> List[Dict[str, Any]]:
    payload = json.loads((tao_root / "annotations" / "validation.json").read_text())
    images = {int(item["id"]): item for item in payload["images"]}
    video_names = {int(item["id"]): str(item["name"]) for item in payload["videos"]}
    by_video_images: Dict[int, List[Mapping[str, Any]]] = defaultdict(list)
    track_counts: Dict[int, Counter[int]] = defaultdict(Counter)
    annotations: Dict[Tuple[int, int], Mapping[str, Any]] = {}
    for image in images.values():
        by_video_images[int(image["video_id"])].append(image)
    for annotation in payload["annotations"]:
        image = images[int(annotation["image_id"])]
        video_id, track_id = int(image["video_id"]), int(annotation["track_id"])
        track_counts[video_id][track_id] += 1
        annotations[(int(image["id"]), track_id)] = annotation

    rows = []
    for video_id, counts in sorted(track_counts.items()):
        track_id, occurrences = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0]
        annotated = []
        for image in sorted(by_video_images[video_id], key=lambda item: int(item["frame_index"])):
            annotation = annotations.get((int(image["id"]), track_id))
            if annotation is not None:
                annotated.append((image, annotation))
        if len(annotated) < 2:
            continue
        chosen = [annotated[0], annotated[-1]]
        paths = [tao_root / "frames" / str(image["file_name"]) for image, _ in chosen]
        if any(not path.is_file() for path in paths):
            raise FileNotFoundError(paths)
        boxes = []
        for _, annotation in chosen:
            x, y, width, height = map(float, annotation["bbox"])
            boxes.append([x, y, x + width, y + height])
        rows.append({
            "element": "target-object",
            "image_path": [str(path.resolve()) for path in paths],
            "bbox": boxes,
            "role": ["reference", "positive-image"],
            "dataset": "TAO",
            "sequence": video_names[video_id],
            "frame_indices": [int(image["frame_index"]) for image, _ in chosen],
            "sampling": "most-frequent-track-first-last-annotated-frame",
            "metadata": {"split": "test", "source_split": "official-validation", "track_id": track_id, "track_occurrences": occurrences, "split_protocol": "e009-posthoc-combined-test/v1"},
        })
    if not rows:
        raise ValueError("TAO validation produced zero episodes")
    return rows


def _identities(rows: Iterable[Mapping[str, Any]]) -> Tuple[Set[str], Set[str]]:
    sequences, images = set(), set()
    for row in rows:
        sequences.add(f"{row.get('dataset')}::{row.get('sequence')}")
        images.update(map(str, row.get("image_path", [])))
    return sequences, images


def build_combined_test(train_manifest: Path, lasot_test: Path, got_root: Path, tao_root: Path, got_output: Path, tao_output: Path, combined_output: Path, audit_output: Path) -> Dict[str, Any]:
    outputs = (got_output, tao_output, combined_output, audit_output)
    existing = [str(path) for path in outputs if path.exists()]
    if existing:
        raise FileExistsError(f"refusing to overwrite test artifacts: {existing}")
    train = _read_json_list(train_manifest)
    lasot = _read_json_list(lasot_test)
    got = build_got_val(got_root)
    tao = build_tao_validation(tao_root)
    combined = lasot + got + tao
    train_seq, train_images = _identities(train)
    component = {"LaSOT": lasot, "GOT10k": got, "TAO": tao}
    overlap: Dict[str, Any] = {"train": {}, "between_test_components": {}}
    for name, rows in component.items():
        seq, images = _identities(rows)
        overlap["train"][name] = {"sequence": len(train_seq & seq), "image": len(train_images & images)}
    names = list(component)
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            left_seq, left_images = _identities(component[left]); right_seq, right_images = _identities(component[right])
            overlap["between_test_components"][f"{left}_{right}"] = {"sequence": len(left_seq & right_seq), "image": len(left_images & right_images)}
    if any(value for group in overlap.values() for pair in group.values() for value in pair.values()):
        raise RuntimeError(f"test leakage detected: {overlap}")

    for path, rows in ((got_output, got), (tao_output, tao), (combined_output, combined)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    audit = {
        "schema": "iploc-szy.e009-combined-posthoc-test/v1",
        "status": "complete",
        "protocol": "e009-posthoc-combined-test/v1",
        "claim_boundary": "Project-specific post-hoc held-out test combining LaSOT test600, GOT-10k official validation, and TAO official validation. It is not the exact IPLoc or FOCUS split. Aggregate metrics are sample-weighted; report per-dataset metrics as primary.",
        "counts": {"LaSOT": len(lasot), "GOT10k": len(got), "TAO": len(tao), "combined": len(combined)},
        "overlap": overlap,
        "sources": {"train_manifest": str(train_manifest.resolve()), "train_manifest_sha256": _sha256(train_manifest), "lasot_test": str(lasot_test.resolve()), "lasot_test_sha256": _sha256(lasot_test), "got_source_split": str((got_root / "val").resolve()), "tao_annotation": str((tao_root / "annotations" / "validation.json").resolve()), "tao_annotation_sha256": _sha256(tao_root / "annotations" / "validation.json")},
        "outputs": {},
    }
    for key, path in (("got_manifest", got_output), ("tao_manifest", tao_output), ("combined_manifest", combined_output)):
        audit["outputs"][key] = str(path.resolve()); audit["outputs"][key + "_sha256"] = _sha256(path)
    audit_output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    return audit


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-manifest", type=Path, required=True); parser.add_argument("--lasot-test", type=Path, required=True)
    parser.add_argument("--got-root", type=Path, required=True); parser.add_argument("--tao-root", type=Path, required=True)
    parser.add_argument("--got-output", type=Path, required=True); parser.add_argument("--tao-output", type=Path, required=True)
    parser.add_argument("--combined-output", type=Path, required=True); parser.add_argument("--audit-output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    audit = build_combined_test(*(getattr(args, name).resolve() for name in ("train_manifest", "lasot_test", "got_root", "tao_root", "got_output", "tao_output", "combined_output", "audit_output")))
    print(json.dumps({"counts": audit["counts"], "overlap": audit["overlap"]}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
