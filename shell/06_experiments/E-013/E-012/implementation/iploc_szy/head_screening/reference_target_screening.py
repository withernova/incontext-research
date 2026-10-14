"""R-005 Reference target-grounded screening and selector freezing.

The model hook produces one record per sample.  This module performs the
sample-first aggregation shared by offline checks and the eventual GPU worker.
It intentionally receives all thresholds explicitly: calibration must freeze
them before this selector is called.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np


SCHEMA = "e012.reference-target-screening/v1"


def _stack(records: Sequence[Mapping[str, object]], key: str,
           *, allow_nan: bool = False) -> np.ndarray:
    values = [np.asarray(record[key]) for record in records]
    if not values:
        raise ValueError("screening records must be non-empty")
    shape = values[0].shape
    if len(shape) != 2 or any(value.shape != shape for value in values):
        raise ValueError(f"{key} must have a common [layers,heads] shape")
    result = np.stack(values)
    if key.endswith("_valid"):
        return result.astype(bool)
    result = result.astype(np.float64)
    if np.isinf(result).any() or (not allow_nan and np.isnan(result).any()):
        raise ValueError(f"{key} must be finite; validity is stored separately")
    return result


def _rank(score: np.ndarray, eligible: np.ndarray, top_k: int) -> list[dict[str, object]]:
    if score.shape != eligible.shape or score.ndim != 2:
        raise ValueError("rank score and eligibility must be [layers,heads]")
    pairs = [(layer, head) for layer, head in np.ndindex(score.shape)
             if eligible[layer, head] and np.isfinite(score[layer, head])]
    pairs.sort(key=lambda item: (-float(score[item]), item[0], item[1]))
    return [dict(rank=rank, layer=layer, head=head, score=float(score[layer, head]))
            for rank, (layer, head) in enumerate(pairs[:top_k], 1)]


def _masked_mean(values: np.ndarray, valid: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    count = valid.sum(axis=0)
    total = np.where(valid, values, 0.0).sum(axis=0)
    mean = np.full(count.shape, np.nan, dtype=np.float64)
    np.divide(total, count, out=mean, where=count > 0)
    return mean, count


def aggregate_reference_screening(
    records: Sequence[Mapping[str, object]],
    *,
    tau_c: float,
    tau_a: float,
    tau_d: float,
    qualification_frequency_min: float,
    top_k: int,
    legacy_iou_threshold: float = 0.5,
) -> dict[str, object]:
    """Aggregate sample records and freeze four comparable head lists.

    ``C_R`` is normalized by the maximum head contribution within each sample
    for continuous ranking only.  The strict qualification gate always uses
    the unnormalized ``C_R`` and all three explicit thresholds.  Undefined
    spatial metrics never pass and remain in the total-sample denominator.
    """
    thresholds = [tau_c, tau_a, tau_d, qualification_frequency_min,
                  legacy_iou_threshold]
    if not np.isfinite(thresholds).all():
        raise ValueError("all thresholds must be finite")
    if tau_c < 0 or not 0 <= tau_a <= 1 or not 0 <= tau_d <= 1:
        raise ValueError("C_R/Target Preference thresholds are invalid")
    if not 0 <= qualification_frequency_min <= 1:
        raise ValueError("qualification_frequency_min must be in [0,1]")
    if not 0 < legacy_iou_threshold <= 1 or type(top_k) is not int or top_k < 1:
        raise ValueError("legacy_iou_threshold/top_k are invalid")

    c_r = _stack(records, "reference_abs_contribution")
    t_a = _stack(records, "attention_target_preference", allow_nan=True)
    t_d = _stack(records, "contribution_target_preference", allow_nan=True)
    valid_a = _stack(records, "attention_valid")
    valid_d = _stack(records, "contribution_valid")
    if (np.any(c_r < 0) or np.any((t_a[np.isfinite(t_a)] < 0) | (t_a[np.isfinite(t_a)] > 1))
            or np.any((t_d[np.isfinite(t_d)] < 0) | (t_d[np.isfinite(t_d)] > 1))):
        raise ValueError("contribution and clipped Target Preference values are out of range")
    if np.any(valid_a & ~np.isfinite(t_a)) or np.any(valid_d & ~np.isfinite(t_d)):
        raise ValueError("valid Target Preference entries must be finite")

    sample_max = c_r.max(axis=(1, 2), keepdims=True)
    normalized_c = np.zeros_like(c_r)
    np.divide(c_r, sample_max, out=normalized_c, where=sample_max > 0)
    spatial_valid = valid_a & valid_d
    strict_sample = (spatial_valid & (c_r >= tau_c) & (t_a >= tau_a)
                     & (t_d >= tau_d))
    strict_frequency = strict_sample.mean(axis=0)
    strict_eligible = strict_frequency >= qualification_frequency_min

    combined_sample = normalized_c * np.sqrt(t_a * t_d)
    attention_sample = normalized_c * t_a
    mean_c = c_r.mean(axis=0)
    mean_attention, attention_count = _masked_mean(attention_sample, valid_a)
    mean_combined, combined_count = _masked_mean(combined_sample, spatial_valid)

    legacy_gradient = _stack(records, "legacy_gradient")
    spatial_iou = _stack(records, "spatial_iou")
    if np.any(legacy_gradient < 0) or np.any((spatial_iou < 0) | (spatial_iou > 1)):
        raise ValueError("legacy gradient/IoU values are out of range")
    legacy_valid = spatial_iou >= legacy_iou_threshold
    legacy_score, legacy_count = _masked_mean(legacy_gradient, legacy_valid)

    shape = c_r.shape[1:]
    any_head = np.ones(shape, dtype=bool)
    selectors = {
        "c_r_only": _rank(mean_c, any_head, top_k),
        "legacy_gradient_iou": _rank(legacy_score, legacy_count > 0, top_k),
        "c_r_target_attention": _rank(mean_attention, attention_count > 0, top_k),
        "target_grounded_combined": _rank(mean_combined, strict_eligible, top_k),
    }
    return {
        "schema": SCHEMA,
        "n_total": len(records),
        "shape": {"layers": shape[0], "heads": shape[1]},
        "thresholds": {
            "tau_c": float(tau_c), "tau_a": float(tau_a), "tau_d": float(tau_d),
            "qualification_frequency_min": float(qualification_frequency_min),
            "legacy_iou_threshold": float(legacy_iou_threshold), "top_k": top_k,
        },
        "validity": {
            "attention_valid_count": valid_a.sum(axis=0),
            "contribution_valid_count": valid_d.sum(axis=0),
            "joint_valid_count": spatial_valid.sum(axis=0),
            "strict_qualification_frequency": strict_frequency,
        },
        "head_metrics": {
            "reference_abs_contribution_mean": mean_c,
            "c_r_target_attention_mean": mean_attention,
            "combined_score_mean": mean_combined,
            "legacy_score_mean_when_iou_passes": legacy_score,
        },
        "selectors": selectors,
    }


def json_ready(value: object) -> object:
    """Convert NumPy results to strict JSON-compatible values."""
    if isinstance(value, np.ndarray):
        return json_ready(value.tolist())
    if isinstance(value, np.generic):
        return json_ready(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    return value


def run_r005_from_records(*, config: Mapping[str, object], snapshot_dir: object) -> dict[str, object]:
    """Analysis entrypoint for frozen per-sample Reference records.

    The GPU collector and this analysis are deliberately separated: reranking
    or changing thresholds never requires another model forward.  The input is
    immutable JSON with ``schema``, ``records`` and a ``split`` on every record.
    """
    del snapshot_dir
    analysis = dict(config.get("analysis") or {})
    required = dict(analysis.get("required_parameters") or {})
    expected = {
        "input_records", "input_records_sha256", "tau_c", "tau_a", "tau_d",
        "qualification_frequency_min", "top_k", "legacy_iou_threshold",
    }
    if set(required) != expected:
        raise ValueError(f"R005 required_parameters must be exactly {sorted(expected)}")
    missing = sorted(key for key, value in required.items() if value is None)
    if missing:
        raise ValueError(f"R005 parameters are not frozen: {missing}")
    source = Path(str(required["input_records"])).resolve()
    raw = source.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != required["input_records_sha256"]:
        raise ValueError("R005 input record SHA-256 mismatch")
    payload = json.loads(raw)
    if payload.get("schema") != "e012.reference-target-screening-records/v1":
        raise ValueError("R005 input record schema mismatch")
    rows = payload.get("records")
    if not isinstance(rows, list) or not rows:
        raise ValueError("R005 records must be a non-empty list")
    discovery = [row for row in rows if row.get("split") == "discovery"]
    confirmation = [row for row in rows if row.get("split") == "confirmation"]
    if not discovery or not confirmation:
        raise ValueError("R005 requires non-empty discovery and confirmation splits")
    discovery_ids = {str(row.get("component_id") or "") for row in discovery}
    confirmation_ids = {str(row.get("component_id") or "") for row in confirmation}
    if "" in discovery_ids | confirmation_ids or discovery_ids & confirmation_ids:
        raise ValueError("component IDs must be present and split-disjoint")

    kwargs = {key: required[key] for key in (
        "tau_c", "tau_a", "tau_d", "qualification_frequency_min", "top_k",
        "legacy_iou_threshold",
    )}
    selected = aggregate_reference_screening(discovery, **kwargs)
    confirmed = aggregate_reference_screening(confirmation, **kwargs)
    frozen_pairs = {
        name: [(item["layer"], item["head"]) for item in ranking]
        for name, ranking in selected["selectors"].items()
    }
    confirmation_metrics = confirmed["head_metrics"]
    confirmation_validity = confirmed["validity"]
    frozen_confirmation = {}
    for name, pairs in frozen_pairs.items():
        frozen_confirmation[name] = [
            {
                "layer": layer,
                "head": head,
                "reference_abs_contribution_mean": float(
                    confirmation_metrics["reference_abs_contribution_mean"][layer, head]
                ),
                "combined_score_mean": float(
                    confirmation_metrics["combined_score_mean"][layer, head]
                ) if np.isfinite(confirmation_metrics["combined_score_mean"][layer, head]) else None,
                "joint_valid_count": int(
                    confirmation_validity["joint_valid_count"][layer, head]
                ),
                "strict_qualification_frequency": float(
                    confirmation_validity["strict_qualification_frequency"][layer, head]
                ),
            }
            for layer, head in pairs
        ]
    result = {
        "schema": SCHEMA,
        "status": "completed",
        "input_records": str(source),
        "input_records_sha256": digest,
        "discovery_samples": len(discovery),
        "confirmation_samples": len(confirmation),
        "component_overlap": 0,
        "discovery": selected,
        "frozen_confirmation": frozen_confirmation,
        "claim_boundary": "screening and independent confirmation only; no causal claim",
    }
    output = Path(str(config["work_dir"])).resolve()
    output.mkdir(parents=True, exist_ok=True)
    destination = output / "summary.json"
    if destination.exists():
        raise FileExistsError(destination)
    destination.write_text(json.dumps(json_ready(result), ensure_ascii=False,
                                      indent=2, allow_nan=False) + "\n")
    return {"summary": str(destination), "status": "completed"}
