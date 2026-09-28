"""Pure metric primitives for the E-012 Query/Reference head contract.

This module deliberately contains no model hooks or dataset assumptions.  It
implements the shape-checked, fail-closed calculations shared by R-004--R-010.
The canonical definitions are documented in
``shell/06_experiments/E-012/dual_role_metric_contract.md``.
"""

from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np


CONTRACT = "e012.dual-role-head-metrics/v1"
CONTRACT_SHA256 = "bab83a1f801b158f7fbe7a027760e1e937185c439b778107e83f6ece1e3c5f06"


def validate_analysis_contract(config: Mapping[str, object]) -> dict[str, object]:
    """Validate the shared E-012 analysis envelope without inventing defaults."""
    analysis = dict(config.get("analysis") or {})
    metric_contract = dict(analysis.get("metric_contract") or {})
    if metric_contract.get("schema") != CONTRACT:
        raise ValueError(f"analysis.metric_contract.schema must equal {CONTRACT!r}")
    if metric_contract.get("sha256") != CONTRACT_SHA256:
        raise ValueError("analysis.metric_contract.sha256 differs from the frozen contract")
    required = analysis.get("required_parameters")
    if not isinstance(required, Mapping) or not required:
        raise ValueError("analysis.required_parameters must be a non-empty mapping")
    missing = sorted(str(key) for key, value in required.items() if value is None)
    if missing:
        raise ValueError(f"required analysis parameters are not frozen: {missing}")
    return {
        "contract": CONTRACT,
        "contract_sha256": CONTRACT_SHA256,
        "required_parameters": dict(required),
    }


def run_r004_scaffold(*, config: Mapping[str, object], snapshot_dir: object) -> dict[str, object]:
    """Fail closed until the reviewed R-004 model-hook implementation exists."""
    del snapshot_dir
    envelope = validate_analysis_contract(config)
    raise RuntimeError(
        "R-004 model-hook worker is not implemented; the current delivery only "
        f"validates the shared launcher/config/metric envelope ({envelope['contract']})"
    )


def _finite_array(value: object, name: str, ndim: int | None = None) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    if ndim is not None and array.ndim != ndim:
        raise ValueError(f"{name} must have ndim={ndim}, got {array.ndim}")
    if array.size == 0 or not np.isfinite(array).all():
        raise ValueError(f"{name} must be non-empty and finite")
    return array


def validate_coordinate_positions(
    input_ids: Sequence[int],
    labels: Sequence[int],
    coordinate_positions: Mapping[str, Sequence[int]],
) -> dict[str, tuple[int, ...]]:
    """Validate x1/y1/x2/y2 target-token positions and their p-1 rows.

    A coordinate may contain multiple subtokens.  Positions are target-token
    positions, not prediction rows; callers must use ``position - 1`` for the
    logits row.  ``labels`` may use -100 outside the supervised suffix.
    """
    required = ("x1", "y1", "x2", "y2")
    ids = tuple(int(v) for v in input_ids)
    target = tuple(int(v) for v in labels)
    if len(ids) != len(target):
        raise ValueError("input_ids and labels must have equal length")
    normalized: dict[str, tuple[int, ...]] = {}
    used: set[int] = set()
    for field in required:
        raw = tuple(int(v) for v in coordinate_positions.get(field, ()))
        if not raw or tuple(sorted(raw)) != raw or len(set(raw)) != len(raw):
            raise ValueError(f"{field} positions must be sorted, unique and non-empty")
        if any(position <= 0 or position >= len(ids) for position in raw):
            raise ValueError(f"{field} positions must have valid p-1 prediction rows")
        if used.intersection(raw):
            raise ValueError("coordinate fields have overlapping token positions")
        if any(target[position] != ids[position] for position in raw):
            raise ValueError(f"{field} contains an unsupervised or mismatched target token")
        used.update(raw)
        normalized[field] = raw
    return normalized


def coordinate_target_positions(coordinate_positions: Mapping[str, Sequence[int]]) -> tuple[int, ...]:
    """Return all coordinate target positions in x1,y1,x2,y2 order."""
    validated = {field: tuple(int(v) for v in coordinate_positions.get(field, ()))
                 for field in ("x1", "y1", "x2", "y2")}
    if any(not positions for positions in validated.values()):
        raise ValueError("all four coordinate fields are required")
    return tuple(position for field in validated for position in validated[field])


def coordinate_prediction_rows(coordinate_positions: Mapping[str, Sequence[int]]) -> tuple[int, ...]:
    """Convert validated coordinate target positions to logits rows."""
    return tuple(position - 1 for position in coordinate_target_positions(coordinate_positions))


def edge_contribution(
    attention: object,
    dloss_dattention: object,
) -> tuple[np.ndarray, np.ndarray]:
    """Return signed and absolute ``A * dL/dA`` edge contributions.

    Both inputs must have shape ``[layers, heads, prediction_rows, keys]``.
    """
    a = _finite_array(attention, "attention", ndim=4)
    grad = _finite_array(dloss_dattention, "dloss_dattention", ndim=4)
    if a.shape != grad.shape:
        raise ValueError("attention and dloss_dattention shapes differ")
    signed = a * grad
    return signed, np.abs(signed)


def target_preference_from_weights(
    weights: object,
    occupancy: object,
) -> dict[str, object]:
    """Normalize spatial weights and compute clipped/raw Target Preference.

    ``weights`` has shape ``[..., reference_tokens]`` and need not already sum
    to one. ``occupancy`` has shape ``[reference_tokens]``. Zero weight and a
    spatially non-discriminative occupancy grid (``max(g) == mean(g)``) are
    represented as invalid with NaN scores; no epsilon is used to invent a
    spatial distribution.
    """
    values = _finite_array(weights, "weights")
    g = _finite_array(occupancy, "occupancy", ndim=1)
    if values.ndim < 1 or values.shape[-1] != g.size:
        raise ValueError("weights last dimension must match occupancy")
    if np.any(values < 0):
        raise ValueError("spatial weights must be non-negative")
    if np.any(g < 0) or np.any(g > 1):
        raise ValueError("occupancy must be in [0,1]")

    mass = values.sum(axis=-1)
    mass_valid = mass > 0
    distribution = np.full(values.shape, np.nan, dtype=np.float64)
    np.divide(values, mass[..., None], out=distribution,
              where=mass_valid[..., None])
    baseline = float(g.mean())
    upper = float(g.max())
    spatial_valid = upper > baseline
    valid = mass_valid & spatial_valid
    target_mass = np.full(mass.shape, np.nan, dtype=np.float64)
    if spatial_valid:
        target_mass[mass_valid] = np.sum(
            distribution[mass_valid] * g, axis=-1
        )
    raw = np.full(mass.shape, np.nan, dtype=np.float64)
    raw[valid] = (target_mass[valid] - baseline) / (upper - baseline)
    clipped = np.full(mass.shape, np.nan, dtype=np.float64)
    clipped[valid] = np.clip(raw[valid], 0.0, 1.0)
    return {
        "weight_mass": mass,
        "distribution": distribution,
        "target_mass": target_mass,
        "uniform_baseline": baseline,
        "grid_upper_bound": upper,
        "valid": valid,
        "invalid_zero_mass": ~mass_valid,
        "invalid_spatial_grid": np.full(mass.shape, not spatial_valid, dtype=bool),
        "target_preference_raw": raw,
        "target_preference": clipped,
    }


def reference_spatial_contribution_metrics(
    attention: object,
    dloss_dattention: object,
    reference_mask: Sequence[bool],
    reference_occupancy: object,
) -> dict[str, object]:
    """Compute per-head ``C_R``, ``T(a)`` and ``T(d)`` within one sample.

    Inputs have shape ``[layers, heads, bbox_prediction_rows, keys]``. Rows are
    aggregated before Reference normalization. Contribution aggregation is
    ``sum_r |A * dL/dA|`` for every Reference token, so signed effects from
    different bbox rows cannot cancel.
    """
    a = _finite_array(attention, "attention", ndim=4)
    signed, absolute = edge_contribution(a, dloss_dattention)
    mask = np.asarray(reference_mask, dtype=bool)
    if mask.shape != (a.shape[-1],) or not bool(mask.any()):
        raise ValueError("reference_mask must be non-empty and match keys")
    g_all = _finite_array(reference_occupancy, "reference_occupancy", ndim=1)
    if g_all.shape == (a.shape[-1],):
        if bool((g_all[~mask] != 0).any()):
            raise ValueError("reference occupancy must be zero outside its mask")
        g = g_all[mask]
    elif g_all.shape == (int(mask.sum()),):
        g = g_all
    else:
        raise ValueError("reference occupancy must match keys or Reference tokens")

    reference_attention_by_token = a[..., mask].sum(axis=2)
    reference_contribution_by_token = absolute[..., mask].sum(axis=2)
    attention_spatial = target_preference_from_weights(
        reference_attention_by_token, g
    )
    contribution_spatial = target_preference_from_weights(
        reference_contribution_by_token, g
    )
    return {
        "shape": {
            "layers": a.shape[0],
            "heads": a.shape[1],
            "prediction_rows": a.shape[2],
            "reference_tokens": int(mask.sum()),
        },
        "reference_attention_mass": attention_spatial["weight_mass"],
        "reference_abs_contribution": contribution_spatial["weight_mass"],
        "attention_by_reference_token": reference_attention_by_token,
        "contribution_by_reference_token": reference_contribution_by_token,
        "signed_contribution_by_reference_token": signed[..., mask].sum(axis=2),
        "attention_spatial": attention_spatial,
        "contribution_spatial": contribution_spatial,
    }


def role_contributions(
    attention: object,
    dloss_dattention: object,
    role_masks: Mapping[str, Sequence[bool]],
    occupancies: Mapping[str, object],
    *,
    eps: float = 1e-12,
) -> dict[str, object]:
    """Compute per-sample Query/Reference contribution summaries.

    Inputs use shape ``[layers, heads, rows, keys]``.  Each role mask and
    occupancy uses shape ``[keys]``.  Aggregation is intentionally *within one
    sample first*: sums over rows and keys are returned for later equal-weight
    sample averaging.
    """
    if eps <= 0 or not np.isfinite(eps):
        raise ValueError("eps must be finite and positive")
    a = _finite_array(attention, "attention", ndim=4)
    _, absolute = edge_contribution(a, dloss_dattention)
    layers, heads, rows, keys = a.shape
    result: dict[str, object] = {
        "contract": CONTRACT,
        "shape": [layers, heads, rows, keys],
        "roles": {},
    }
    all_contribution = absolute.sum(axis=(2, 3))
    seen_keys = np.zeros(keys, dtype=bool)
    for role, raw_mask in role_masks.items():
        mask = np.asarray(raw_mask, dtype=bool)
        occupancy = _finite_array(occupancies[role], f"{role}_occupancy", ndim=1)
        if mask.shape != (keys,) or occupancy.shape != (keys,):
            raise ValueError(f"{role} mask/occupancy must have shape [{keys}]")
        if not bool(mask.any()) or bool((seen_keys & mask).any()):
            raise ValueError("role masks must be non-empty and disjoint")
        if np.any(occupancy < 0) or np.any(occupancy > 1):
            raise ValueError(f"{role} occupancy must be in [0,1]")
        if bool((occupancy[~mask] != 0).any()):
            raise ValueError(f"{role} occupancy must be zero outside its role mask")
        seen_keys |= mask
        role_edges = absolute[:, :, :, mask]
        role_total = role_edges.sum(axis=(2, 3))
        target = (absolute[:, :, :, mask] * occupancy[mask][None, None, None, :]).sum(axis=(2, 3))
        background = (absolute[:, :, :, mask] * (1.0 - occupancy[mask])[None, None, None, :]).sum(axis=(2, 3))
        target_area = float(occupancy[mask].sum())
        background_area = float((1.0 - occupancy[mask]).sum())
        if target_area <= 0 or background_area <= 0:
            raise ValueError(f"{role} target and background areas must both be positive")
        target_density = target / (target_area + eps)
        background_density = background / (background_area + eps)
        result["roles"][role] = {
            "role_visual_abs_contrib": role_total,
            "role_share": role_total / (all_contribution + eps),
            "all_contribution_denominator_zero": all_contribution == 0,
            "target_contrib": target,
            "background_contrib": background,
            "tcr": target / (target + background + eps),
            "role_contribution_denominator_zero": (target + background) == 0,
            "log_tce": np.log((target_density + eps) / (background_density + eps)),
            "target_area": target_area,
            "background_area": background_area,
        }
    return result


def target_vs_null_log(
    target_contribution: object,
    target_area: float,
    null_contributions: object,
    null_areas: object,
    *,
    eps: float = 1e-12,
) -> np.ndarray:
    """Compare target contribution density to the mean density of frozen nulls."""
    target = _finite_array(target_contribution, "target_contribution")
    null = _finite_array(null_contributions, "null_contributions")
    areas = _finite_array(null_areas, "null_areas", ndim=1)
    if target_area <= 0 or null.ndim < 1 or null.shape[0] != areas.size:
        raise ValueError("target/null areas are invalid")
    if np.any(areas <= 0):
        raise ValueError("null areas must be positive")
    null_density = np.mean(null / (areas.reshape((-1,) + (1,) * (null.ndim - 1)) + eps), axis=0)
    return np.log((target / (target_area + eps) + eps) / (null_density + eps))


def central_difference(loss_minus: float, loss_plus: float, epsilon: float) -> float:
    """Compute the fixed, non-renormalized central finite difference."""
    if not np.isfinite([loss_minus, loss_plus, epsilon]).all() or epsilon <= 0:
        raise ValueError("finite-difference inputs must be finite and epsilon > 0")
    return float((loss_plus - loss_minus) / (2.0 * epsilon))


def compare_derivatives(autograd: float, finite_difference_value: float, *, floor: float = 1e-8) -> dict[str, object]:
    """Return signed agreement and symmetric relative error for R-004."""
    if not np.isfinite([autograd, finite_difference_value, floor]).all() or floor <= 0:
        raise ValueError("derivative comparison inputs are invalid")
    return {
        "signed_derivative": float(autograd),
        "central_difference": float(finite_difference_value),
        "sign_agreement": bool(autograd * finite_difference_value > 0),
        "relative_error": float(abs(autograd - finite_difference_value)
                                 / max(abs(autograd), abs(finite_difference_value), floor)),
    }


def target_specific_damage(delta_ce_target: object, delta_ce_background: object) -> np.ndarray:
    """Return target-removal CE damage minus mean matched-background damage."""
    target = _finite_array(delta_ce_target, "delta_ce_target")
    background = _finite_array(delta_ce_background, "delta_ce_background")
    if background.ndim != 2 or target.shape != (background.shape[0],):
        raise ValueError("background must be [samples, background_repeats]")
    return target - background.mean(axis=1)


def damage_difference_in_difference(candidate: object, controls: object) -> np.ndarray:
    """Return candidate target-specific damage minus mean control damage."""
    candidate_array = _finite_array(candidate, "candidate_damage", ndim=1)
    control_array = _finite_array(controls, "control_damage", ndim=2)
    if control_array.shape[0] != candidate_array.shape[0]:
        raise ValueError("candidate and control sample counts differ")
    return candidate_array - control_array.mean(axis=1)
