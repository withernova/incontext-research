#!/usr/bin/env python3
"""Safely extract tracking data and build train-only FOCUS-style manifests."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import zipfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path, PurePosixPath
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

Box = List[float]


def _focus_indices(frame_count: int, shots: int) -> Tuple[List[int], int]:
    """Sample supports uniformly through the penultimate frame; query is final."""
    if shots < 1:
        raise ValueError("shots must be positive")
    if frame_count < shots + 1:
        raise ValueError(f"need at least {shots + 1} annotated frames, got {frame_count}")
    last_support = frame_count - 2
    support = [0] if shots == 1 else [round(i * last_support / (shots - 1)) for i in range(shots)]
    if len(set(support)) != shots:
        raise ValueError("uniform support sampling produced duplicate frames")
    return support, frame_count - 1


def _xywh_to_xyxy(box: Sequence[float]) -> Box:
    x, y, width, height = (float(value) for value in box)
    return [x, y, x + width, y + height]


def _read_boxes(path: Path) -> List[Box]:
    boxes: List[Box] = []
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        values = [float(value) for value in stripped.replace("\t", ",").split(",")]
        if len(values) != 4:
            raise ValueError(f"{path}:{line_number}: expected four bbox values")
        boxes.append(_xywh_to_xyxy(values))
    return boxes


def _record(dataset: str, sequence: str, image_paths: Sequence[Path], boxes: Sequence[Box], shots: int, metadata: Optional[Mapping[str, object]] = None) -> Dict[str, object]:
    support, query = _focus_indices(len(image_paths), shots)
    chosen = support + [query]
    result: Dict[str, object] = {
        "element": "target-object",
        "image_path": [str(image_paths[index].resolve()) for index in chosen],
        "bbox": [boxes[index] for index in chosen],
        "role": ["reference"] * shots + ["positive-image"],
        "dataset": dataset,
        "sequence": sequence,
        "frame_indices": chosen,
        "sampling": "focus-uniform-full-span-final-query",
    }
    if metadata:
        result["metadata"] = dict(metadata)
    return result


def _record_from_numbered_frames(
    dataset: str,
    sequence: str,
    image_dir: Path,
    boxes: Sequence[Box],
    shots: int,
    metadata: Optional[Mapping[str, object]] = None,
) -> Dict[str, object]:
    """Build a record from standard 1-indexed tracking filenames without a file scan."""
    support, query = _focus_indices(len(boxes), shots)
    chosen = support + [query]
    result: Dict[str, object] = {
        "element": "target-object",
        "image_path": [str((image_dir / f"{index + 1:08d}.jpg").resolve()) for index in chosen],
        "bbox": [boxes[index] for index in chosen],
        "role": ["reference"] * shots + ["positive-image"],
        "dataset": dataset,
        "sequence": sequence,
        "frame_indices": chosen,
        "sampling": "focus-uniform-full-span-final-query",
    }
    if metadata:
        result["metadata"] = dict(metadata)
    return result


def _safe_members(archive: Path) -> None:
    """Reject absolute paths, parent traversal, and archived symbolic links."""
    with zipfile.ZipFile(archive) as handle:
        for info in handle.infolist():
            member = PurePosixPath(info.filename)
            if member.is_absolute() or ".." in member.parts:
                raise ValueError(f"unsafe archive member in {archive}: {info.filename}")
            mode = info.external_attr >> 16
            if mode and (mode & 0o170000) == 0o120000:
                raise ValueError(f"symlink archive member in {archive}: {info.filename}")


def _extract_one(archive: Path, destination: Path, marker_root: Path) -> str:
    identity = f"{archive.resolve()}|{archive.stat().st_size}|{archive.stat().st_mtime_ns}"
    marker = marker_root / (archive.name + ".json")
    if marker.exists():
        current = json.loads(marker.read_text())
        if current.get("identity") == identity and current.get("status") == "complete":
            return "skipped"
    _safe_members(archive)
    destination.mkdir(parents=True, exist_ok=True)
    # unzip validates member CRCs while extracting. A marker is written only
    # after a zero exit status, so an interrupted/corrupt archive remains resumable.
    subprocess.run(["unzip", "-q", "-n", str(archive), "-d", str(destination)], check=True)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps({"status": "complete", "identity": identity, "archive": str(archive.resolve()), "destination": str(destination.resolve())}, indent=2) + "\n")
    return "extracted"


def extract_all(source_root: Path, output_root: Path, workers: int = 1, in_place: bool = False) -> Dict[str, int]:
    jobs: List[Tuple[Path, Path, Path]] = []
    got = source_root / "GOT10k"
    got_output = got.resolve() if in_place else output_root / "GOT10k"
    lasot_output = (source_root / "LaSOT/LaSOT").resolve() if in_place else output_root / "LaSOT"
    tao = source_root / "TAO/TAO-Amodal"
    tao_output = tao.resolve() if in_place else output_root / "TAO"
    jobs.extend([(got / "val_data.zip", got_output, got_output / ".focus_extract_markers"), (got / "test_data.zip", got_output, got_output / ".focus_extract_markers")])
    jobs.extend((archive, got_output / "train", got_output / ".focus_extract_markers") for archive in sorted((got / "train_data").glob("*.zip")))
    jobs.extend((archive, lasot_output, lasot_output / ".focus_extract_markers") for archive in sorted((source_root / "LaSOT/LaSOT/zip").glob("*.zip")))
    for split in ("train", "val", "test"):
        for archive in sorted((tao / "frames" / split).glob("*.zip")):
            jobs.append((archive, tao_output / "frames" / split / archive.stem, tao_output / ".focus_extract_markers" / split))
    if not jobs:
        raise FileNotFoundError(f"no dataset archives found below {source_root}")
    if workers < 1:
        raise ValueError("workers must be positive")
    for archive, _, _ in jobs:
        if not archive.is_file():
            raise FileNotFoundError(archive)
    counts: Counter[str] = Counter()
    completed = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pending = {
            pool.submit(_extract_one, archive, destination, marker): (archive, destination)
            for archive, destination, marker in jobs
        }
        for future in as_completed(pending):
            archive, destination = pending[future]
            status = future.result()
            completed += 1
            counts[status] += 1
            print(f"[{completed}/{len(jobs)}] {status}: {archive} -> {destination}", flush=True)
    if not in_place:
        shutil.copytree(tao / "annotations", tao_output / "annotations", dirs_exist_ok=True)
    counts["archives"] = len(jobs)
    return dict(counts)


def _single_target_records(root: Path, dataset: str, shots: int) -> Iterable[Dict[str, object]]:
    if dataset == "GOT10k":
        sequence_dirs = sorted((root / "train").glob("GOT-10k_Train_*"))
    else:
        sequence_dirs = sorted(path.parent for path in root.glob("*/*/groundtruth.txt"))
    for sequence_dir in sequence_dirs:
        annotation = sequence_dir / "groundtruth.txt"
        if not annotation.is_file():
            continue
        image_dir = sequence_dir if dataset == "GOT10k" else sequence_dir / "img"
        boxes = _read_boxes(annotation)
        if len(boxes) >= shots + 1:
            yield _record_from_numbered_frames(
                dataset, sequence_dir.name, image_dir, boxes, shots
            )


def _read_categories(path: Path) -> set[str]:
    """Read the explicitly frozen LaSOT training-category list."""
    categories = {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    if not categories:
        raise ValueError(f"LaSOT training-category list is empty: {path}")
    return categories


def _lasot_train_records(
    root: Path,
    shots: int,
    categories: Optional[set[str]],
) -> List[Dict[str, object]]:
    """Return only explicitly declared LaSOT train categories.

    LaSOTTesting must never be silently repurposed as training data. A caller
    must supply the frozen category split when an actual LaSOT training root is
    available; otherwise LaSOT contributes zero records.
    """
    if categories is None:
        return []
    if "testing" in root.name.lower():
        raise ValueError(f"refusing LaSOT testing root as training data: {root}")
    records = _single_target_records(root, "LaSOT", shots)
    return [
        record
        for record in records
        if str(record["sequence"]).rsplit("-", 1)[0] in categories
    ]


def _tao_records(root: Path, split: str, shots: int) -> Iterable[Dict[str, object]]:
    payload = json.loads((root / "annotations" / f"{split}.json").read_text())
    images = {int(item["id"]): item for item in payload["images"]}
    by_video_track: Dict[int, Counter[int]] = defaultdict(Counter)
    annotations: Dict[Tuple[int, int], Mapping[str, object]] = {}
    for annotation in payload["annotations"]:
        image = images[int(annotation["image_id"])]
        video_id, track_id = int(image["video_id"]), int(annotation["track_id"])
        by_video_track[video_id][track_id] += 1
        annotations[(int(annotation["image_id"]), track_id)] = annotation
    video_names = {int(item["id"]): str(item["name"]) for item in payload["videos"]}
    by_video_images: Dict[int, List[Mapping[str, object]]] = defaultdict(list)
    for image in images.values():
        by_video_images[int(image["video_id"])].append(image)
    for video_id, track_counts in sorted(by_video_track.items()):
        track_id, occurrences = sorted(track_counts.items(), key=lambda item: (-item[1], item[0]))[0]
        annotated = []
        for image in sorted(by_video_images[video_id], key=lambda item: int(item["frame_index"])):
            annotation = annotations.get((int(image["id"]), track_id))
            if annotation is not None:
                annotated.append((image, annotation))
        if len(annotated) < shots + 1:
            continue
        paths = [root / "frames" / str(image["file_name"]) for image, _ in annotated]
        boxes = [_xywh_to_xyxy(annotation["bbox"]) for _, annotation in annotated]
        yield _record(
            "TAO",
            video_names[video_id],
            paths,
            boxes,
            shots,
            {"track_id": track_id, "track_occurrences": occurrences, "split": split},
        )


def build_manifests(
    root: Path,
    manifest_dir: Path,
    shots: int,
    in_place: bool = False,
    lasot_train_root: Optional[Path] = None,
    lasot_train_categories: Optional[Path] = None,
) -> Dict[str, int]:
    manifest_dir.mkdir(parents=True, exist_ok=True)
    got_root = root / "GOT10k"
    tao_root = root / "TAO/TAO-Amodal" if in_place else root / "TAO"
    if (lasot_train_root is None) != (lasot_train_categories is None):
        raise ValueError(
            "LaSOT training requires both --lasot-train-root and "
            "--lasot-train-categories; otherwise it is excluded"
        )
    categories = _read_categories(lasot_train_categories) if lasot_train_categories else None
    got10k_train = (
        list(_single_target_records(got_root, "GOT10k", shots))
        if (got_root / "train").is_dir()
        else []
    )
    tao_train = (
        list(_tao_records(tao_root, "train", shots))
        if (tao_root / "annotations" / "train.json").is_file()
        else []
    )
    datasets = {
        "got10k_train": got10k_train,
        "lasot_train": (
            _lasot_train_records(lasot_train_root.resolve(), shots, categories)
            if lasot_train_root
            else []
        ),
        "tao_train": tao_train,
    }
    counts: Dict[str, int] = {}
    for name, rows in datasets.items():
        path = manifest_dir / f"{name}_{shots}shot_focus.json"
        path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
        counts[name] = len(rows)
        print(f"manifest: {path} ({len(rows)} records)", flush=True)
    combined = (
        datasets["got10k_train"]
        + datasets["lasot_train"]
        + datasets["tao_train"]
    )
    path = manifest_dir / f"train_only_{shots}shot_focus.json"
    path.write_text(json.dumps(combined, indent=2, ensure_ascii=False) + "\n")
    counts["train_only"] = len(combined)
    return counts


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("extract", "manifest", "all"))
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--manifest-dir", type=Path)
    parser.add_argument(
        "--lasot-train-root",
        type=Path,
        help="Explicit LaSOT training root; do not point this at LaSOTTesting.",
    )
    parser.add_argument(
        "--lasot-train-categories",
        type=Path,
        help="Frozen LaSOT train-category list; omit to exclude LaSOT entirely.",
    )
    parser.add_argument("--shots", type=int, default=4)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--in-place", action="store_true", help="extract into the symlink targets under pubdata")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    source_root, output_root = args.source_root.resolve(), args.output_root.resolve()
    if source_root == output_root or source_root in output_root.parents:
        raise ValueError("output root must not overwrite the archive source tree")
    summary: Dict[str, object] = {}
    if args.command in {"extract", "all"}:
        summary["extract"] = extract_all(source_root, output_root, args.workers, args.in_place)
    if args.command in {"manifest", "all"}:
        manifest_dir = (args.manifest_dir or output_root / "manifests").resolve()
        manifest_source_root = source_root if args.in_place else output_root
        summary["manifest"] = build_manifests(
            manifest_source_root,
            manifest_dir,
            args.shots,
            args.in_place,
            args.lasot_train_root,
            args.lasot_train_categories,
        )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
