"""Prepare an independent, deterministic LaSOT positive-pair screening manifest."""
import hashlib
import json
import random
from pathlib import Path

from PIL import Image


def prepare_manifest(root, destination, samples, seed):
    root, destination = Path(root), Path(destination)
    if destination.exists():
        raise FileExistsError(f"refusing to replace manifest: {destination}")
    sequences = sorted(p for p in root.iterdir() if (p / "groundtruth.txt").is_file())
    random.Random(seed).shuffle(sequences)
    records, rejected = [], []
    for sequence in sequences:
        try:
            annotation = sequence / "groundtruth.txt"
            boxes = [[float(v) for v in line.replace(",", " ").split()]
                     for line in annotation.read_text().splitlines() if line.strip()]
            images = sorted((sequence / "img").glob("*.jpg"))
            flags = []
            for name in ("full_occlusion.txt", "out_of_view.txt"):
                flags.append([int(v) for v in (sequence / name).read_text().replace(",", " ").split()])
            if any(len(v) != len(boxes) for v in [images, *flags]):
                raise ValueError("annotation/image/visibility lengths differ")
            valid = [i for i, box in enumerate(boxes) if len(box) == 4
                     and box[2] > 0 and box[3] > 0 and not any(f[i] for f in flags)]
            if len(valid) < 2:
                raise ValueError("fewer than two visible positive frames")
            # First visible frame supplies the example; temporal midpoint supplies query.
            reference = valid[0]
            query = min(valid[1:], key=lambda i: (abs(i - (len(boxes) - 1) / 2), i))
            selected = [reference, query]
            xyxy = []
            for i in selected:
                x, y, w, h = boxes[i]
                with Image.open(images[i]) as image:
                    image.verify()
                with Image.open(images[i]) as image:
                    width, height = image.size
                if not (0 <= x < x + w <= width and 0 <= y < y + h <= height):
                    raise ValueError("selected box is outside image; no silent clipping")
                xyxy.append([x, y, x + w, y + h])
            records.append(dict(
                element=sequence.name.rsplit("-", 1)[0], dataset="LaSOTTesting",
                image_path=[str(images[i]) for i in selected], bbox=xyxy,
                role=["reference", "positive-image"],
                source=dict(sequence_cluster=sequence.name,
                            frame_indices_zero_based=selected,
                            annotation_sha256=hashlib.sha256(annotation.read_bytes()).hexdigest())))
        except (ValueError, OSError) as error:
            rejected.append(dict(sequence=sequence.name, reason=str(error)))
        if len(records) == samples:
            break
    if len(records) != samples:
        raise ValueError(f"only {len(records)}/{samples} valid pairs; no manifest written")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(records, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    provenance = dict(schema="iploc-szy.lasot-screen-manifest/v1", root=str(root),
                      samples=samples, seed=seed, selection="seeded_sequence_shuffle",
                      frame_policy="first_visible_reference_and_visible_temporal_midpoint_query",
                      rejected=rejected, manifest_sha256=hashlib.sha256(destination.read_bytes()).hexdigest())
    destination.with_suffix(".provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    return provenance
