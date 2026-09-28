"""Audited one-sample-per-record teacher artifacts for attention distillation."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

import numpy as np
import torch

from ..head_screening.metrics import normalized_box_occupancy
from ..head_screening.probes import consecutive_spans
from ..prompting.coordinates import parse_box
from .selected import Head, head_label


SCHEMA = "iploc-szy.fixed-attention-teacher/v1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class SampleGeometry:
    sample_id: str
    bbox_token_positions: Tuple[int, ...]
    prediction_rows: Tuple[int, ...]
    reference_span: Tuple[int, int, int, int]
    query_span: Tuple[int, int, int, int]
    reference_grid_thw: Tuple[int, int, int]
    query_grid_thw: Tuple[int, int, int]
    reference_occupancy: np.ndarray


def sample_geometries(
    input_ids: torch.Tensor,
    metadata: Sequence[Mapping[str, Any]],
    *,
    image_token_id: int,
    spatial_merge_size: int,
) -> List[SampleGeometry]:
    """Resolve and audit bbox rows, visual spans, merged grids, and GT occupancy."""
    if input_ids.ndim != 2 or len(metadata) != input_ids.shape[0]:
        raise ValueError("input_ids/metadata batch dimensions differ")
    output = []
    for row_index, row in enumerate(metadata):
        spans = consecutive_spans(input_ids[row_index].detach().cpu().tolist(), image_token_id)
        grids = row.get("image_grid_thw")
        if grids is None or len(grids) != len(spans) or len(spans) != 2:
            raise ValueError(
                f"sample {row.get('id')} requires exactly one reference and one query grid"
            )
        shaped = []
        normalized_grids = []
        for span, raw_grid in zip(spans, grids):
            temporal, height, width = map(int, raw_grid)
            if temporal != 1 or height % spatial_merge_size or width % spatial_merge_size:
                raise ValueError(f"sample {row.get('id')} has unsupported token grid")
            merged_h = height // spatial_merge_size
            merged_w = width // spatial_merge_size
            if span[1] - span[0] != merged_h * merged_w:
                raise ValueError(f"sample {row.get('id')} visual span/grid mismatch")
            shaped.append((span[0], span[1], merged_h, merged_w))
            normalized_grids.append((temporal, height, width))
        bbox_positions = tuple(map(int, row.get("bbox_token_positions") or ()))
        if not bbox_positions or bbox_positions[0] <= 0:
            raise ValueError(f"sample {row.get('id')} has invalid bbox token rows")
        prediction_rows = tuple(position - 1 for position in bbox_positions)
        if any(position >= input_ids.shape[1] for position in bbox_positions):
            raise ValueError(f"sample {row.get('id')} bbox position exceeds sequence")
        reference_answers = row.get("reference_answers") or ()
        reference_box = parse_box(reference_answers[0]) if len(reference_answers) == 1 else None
        if reference_box is None:
            raise ValueError(f"sample {row.get('id')} has invalid reference bbox")
        occupancy = normalized_box_occupancy(
            reference_box, shaped[0][2], shaped[0][3]
        ).astype(np.float32)
        output.append(
            SampleGeometry(
                sample_id=str(row["id"]),
                bbox_token_positions=bbox_positions,
                prediction_rows=prediction_rows,
                reference_span=shaped[0],
                query_span=shaped[1],
                reference_grid_thw=normalized_grids[0],
                query_grid_thw=normalized_grids[1],
                reference_occupancy=occupancy,
            )
        )
    return output


def ensemble_teacher(
    selected: Mapping[Head, Sequence[torch.Tensor]],
    sample_index: int,
    geometry: SampleGeometry,
    heads: Sequence[Head],
) -> Dict[str, np.ndarray]:
    """Average p-1 rows, normalize each head in-span, then ensemble equally."""
    start, stop, height, width = geometry.reference_span
    normalized_heads = []
    raw_heads = []
    for head in heads:
        probabilities = selected[head][sample_index]
        raw = probabilities[:, start:stop].float().mean(dim=0)
        if raw.numel() != height * width or not bool(torch.isfinite(raw).all()):
            raise RuntimeError(f"invalid selected map for {head_label(head)}")
        mass = raw.sum()
        if not bool(torch.isfinite(mass)) or float(mass.detach().item()) <= 0.0:
            raise RuntimeError(f"nonpositive reference mass for {head_label(head)}")
        raw_heads.append(raw)
        normalized_heads.append(raw / mass)
    raw_map = torch.stack(raw_heads).mean(dim=0)
    distribution = torch.stack(normalized_heads).mean(dim=0)
    occupancy = torch.as_tensor(
        geometry.reference_occupancy.reshape(-1),
        dtype=raw_map.dtype,
        device=raw_map.device,
    )
    values = {
        "distribution": distribution.reshape(height, width).detach().float().cpu().numpy(),
        "raw_reference_map": raw_map.reshape(height, width).detach().float().cpu().numpy(),
        "reference_occupancy": geometry.reference_occupancy,
        "reference_span_mass": np.asarray(float(raw_map.sum().detach().item()), dtype=np.float32),
        "reference_object_mass": np.asarray(
            float((raw_map * occupancy).sum().detach().item()), dtype=np.float32
        ),
    }
    if any(not np.isfinite(value).all() for value in values.values()):
        raise RuntimeError("teacher artifact contains non-finite values")
    return values


def write_teacher_record(
    root: Path,
    dataset_index: int,
    geometry: SampleGeometry,
    values: Mapping[str, np.ndarray],
) -> Dict[str, Any]:
    records_dir = root / "records"
    records_dir.mkdir(parents=True, exist_ok=True)
    path = records_dir / f"sample_{dataset_index:06d}.npz"
    if path.exists():
        raise FileExistsError(f"refusing to overwrite teacher record: {path}")
    temporary = path.with_suffix(".tmp.npz")
    np.savez_compressed(temporary, **values)
    os.replace(temporary, path)
    return {
        "dataset_index": int(dataset_index),
        "sample_id": geometry.sample_id,
        "artifact": str(path),
        "artifact_sha256": sha256(path),
        "bbox_token_positions": list(geometry.bbox_token_positions),
        "prediction_rows": list(geometry.prediction_rows),
        "reference_span": list(geometry.reference_span),
        "query_span": list(geometry.query_span),
        "reference_grid_thw": list(geometry.reference_grid_thw),
        "query_grid_thw": list(geometry.query_grid_thw),
    }


def load_teacher_record(
    root: Path,
    dataset_index: int,
    geometry: SampleGeometry,
) -> Optional[Dict[str, Any]]:
    """Validate and describe one existing record for strict resumable precompute."""
    path = root / "records" / f"sample_{dataset_index:06d}.npz"
    if not path.exists():
        return None
    with np.load(path, allow_pickle=False) as archive:
        values = {key: np.asarray(archive[key]) for key in archive.files}
    required = {
        "distribution",
        "raw_reference_map",
        "reference_occupancy",
        "reference_span_mass",
        "reference_object_mass",
    }
    shape = geometry.reference_span[2:]
    if set(values) != required or any(
        value.size == 0 or not np.isfinite(value).all() for value in values.values()
    ):
        raise ValueError(f"existing teacher record is invalid: {path}")
    if any(
        values[key].shape != shape
        for key in ("distribution", "raw_reference_map", "reference_occupancy")
    ):
        raise ValueError(f"existing teacher record grid shape is invalid: {path}")
    if not np.allclose(values["reference_occupancy"], geometry.reference_occupancy):
        raise ValueError(f"existing teacher record occupancy is invalid: {path}")
    if not np.isclose(values["distribution"].sum(), 1.0, atol=2e-5):
        raise ValueError(f"existing teacher distribution is not normalized: {path}")
    raw = values["raw_reference_map"]
    occupancy = values["reference_occupancy"]
    if not np.isclose(raw.sum(), values["reference_span_mass"], atol=2e-5):
        raise ValueError(f"existing teacher span mass is inconsistent: {path}")
    if not np.isclose(
        (raw * occupancy).sum(), values["reference_object_mass"], atol=2e-5
    ):
        raise ValueError(f"existing teacher object mass is inconsistent: {path}")
    return {
        "dataset_index": int(dataset_index),
        "sample_id": geometry.sample_id,
        "artifact": str(path),
        "artifact_sha256": sha256(path),
        "bbox_token_positions": list(geometry.bbox_token_positions),
        "prediction_rows": list(geometry.prediction_rows),
        "reference_span": list(geometry.reference_span),
        "query_span": list(geometry.query_span),
        "reference_grid_thw": list(geometry.reference_grid_thw),
        "query_grid_thw": list(geometry.query_grid_thw),
    }


def finalize_teacher_manifest(
    root: Path,
    *,
    records: Sequence[Mapping[str, Any]],
    expected_sample_ids: Sequence[str],
    teacher_heads: Sequence[Head],
    checkpoint: str,
    source_manifest: str,
) -> Path:
    sample_ids = [str(row["sample_id"]) for row in records]
    expected = list(map(str, expected_sample_ids))
    if len(records) != len(expected) or len(set(sample_ids)) != len(sample_ids):
        raise RuntimeError("teacher records are not one-to-one with the dataset")
    if set(sample_ids) != set(expected):
        missing = sorted(set(expected) - set(sample_ids))[:5]
        extra = sorted(set(sample_ids) - set(expected))[:5]
        raise RuntimeError(f"teacher sample_id mismatch: missing={missing} extra={extra}")
    ordered = sorted((dict(row) for row in records), key=lambda row: row["dataset_index"])
    if [row["dataset_index"] for row in ordered] != list(range(len(expected))):
        raise RuntimeError("teacher dataset indices are incomplete or duplicated")
    manifest = {
        "schema": SCHEMA,
        "checkpoint": str(checkpoint),
        "source_manifest": str(source_manifest),
        "teacher_heads": [head_label(head) for head in teacher_heads],
        "row_contract": "teacher_forced_query_bbox_pminus1/v1",
        "head_reduction": "mean_rows_then_normalize_each_head_then_equal_ensemble",
        "sample_count": len(ordered),
        "records": ordered,
    }
    path = root / "manifest.json"
    if path.exists():
        raise FileExistsError(f"refusing to overwrite teacher manifest: {path}")
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)
    return path


class FixedTeacherStore:
    """Fail-closed reader with dataset-wide sample_id and per-batch geometry audit."""

    def __init__(
        self,
        manifest_path: str,
        expected_sample_ids: Iterable[str],
        expected_heads: Sequence[Head],
    ) -> None:
        path = Path(manifest_path).resolve()
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema") != SCHEMA:
            raise ValueError(f"unsupported teacher schema: {payload.get('schema')}")
        if payload.get("teacher_heads") != [head_label(head) for head in expected_heads]:
            raise ValueError("teacher head list does not match the configured fixed teacher")
        records = payload.get("records") or []
        self.records = {str(row["sample_id"]): dict(row) for row in records}
        expected = list(map(str, expected_sample_ids))
        if len(self.records) != len(records) or set(self.records) != set(expected):
            raise ValueError("teacher manifest sample_ids do not match the training dataset")
        if int(payload.get("sample_count", -1)) != len(expected):
            raise ValueError("teacher manifest sample_count is inconsistent")
        for row in self.records.values():
            artifact = Path(row["artifact"])
            if not artifact.is_file() or sha256(artifact) != row["artifact_sha256"]:
                raise ValueError(f"teacher artifact is absent or hash-mismatched: {artifact}")

    def load(self, geometry: SampleGeometry) -> Dict[str, np.ndarray]:
        row = self.records.get(geometry.sample_id)
        if row is None:
            raise KeyError(f"teacher has no sample_id {geometry.sample_id!r}")
        audits = {
            "bbox_token_positions": geometry.bbox_token_positions,
            "prediction_rows": geometry.prediction_rows,
            "reference_span": geometry.reference_span,
            "query_span": geometry.query_span,
            "reference_grid_thw": geometry.reference_grid_thw,
            "query_grid_thw": geometry.query_grid_thw,
        }
        for key, expected in audits.items():
            if tuple(map(int, row[key])) != tuple(map(int, expected)):
                raise ValueError(
                    f"teacher geometry mismatch for {geometry.sample_id}: {key}"
                )
        with np.load(row["artifact"], allow_pickle=False) as archive:
            values = {key: np.asarray(archive[key]) for key in archive.files}
        required = {
            "distribution",
            "raw_reference_map",
            "reference_occupancy",
            "reference_span_mass",
            "reference_object_mass",
        }
        if set(values) != required or any(
            value.size == 0 or not np.isfinite(value).all() for value in values.values()
        ):
            raise ValueError(f"teacher values are invalid for {geometry.sample_id}")
        shape = geometry.reference_span[2:]
        if any(values[key].shape != shape for key in (
            "distribution", "raw_reference_map", "reference_occupancy"
        )):
            raise ValueError(f"teacher grid shape mismatch for {geometry.sample_id}")
        if not np.allclose(values["reference_occupancy"], geometry.reference_occupancy):
            raise ValueError(f"teacher bbox occupancy mismatch for {geometry.sample_id}")
        if not np.isclose(values["distribution"].sum(), 1.0, atol=2e-5):
            raise ValueError(f"teacher distribution is not normalized for {geometry.sample_id}")
        return values

