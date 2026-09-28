"""Pure spatial metrics used by periodic attention-head screening.

The definitions are intentionally local to ``iploc_szy``.  They mirror the
R003 binary 8-connected component entropy and the R006-T003 S50 fractional
IoU readout without importing an experiment pipeline from ``iplocid``.
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np


def finite_attention(value: Any) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    if (
        array.ndim != 2
        or array.size == 0
        or not np.isfinite(array).all()
        or bool((array < 0).any())
    ):
        raise ValueError("attention map must be a finite nonnegative 2D array")
    return array


def component_token_entropy(value: Any, mean_multiplier: float = 1.0) -> float:
    """Entropy of 8-connected binary component token counts (R003/T003)."""
    array = finite_attention(value)
    mask = array > float(mean_multiplier) * float(array.mean())
    try:
        from scipy.ndimage import label
    except ImportError as exc:
        raise RuntimeError("scipy is required for head component entropy") from exc
    labels, count = label(mask, structure=np.ones((3, 3), dtype=np.int8))
    sizes = np.bincount(labels.ravel())[1 : count + 1].astype(np.float64)
    if not sizes.size:
        return float("inf")
    probabilities = sizes / sizes.sum()
    return float(-(probabilities * np.log(probabilities)).sum())


def chord_threshold(values: Sequence[float]) -> float:
    """Return the maximum-distance-to-chord elbow used by R003."""
    vector = np.asarray(values, dtype=np.float64)
    if vector.ndim != 1 or vector.size == 0 or not np.isfinite(vector).all():
        raise ValueError("threshold values must be a nonempty finite vector")
    if vector.size <= 2:
        return float(vector.min())
    y = np.sort(vector)
    x = np.arange(y.size, dtype=np.float64)
    line = np.asarray([x[-1] - x[0], y[-1] - y[0]], dtype=np.float64)
    norm = float(np.linalg.norm(line))
    if norm == 0.0:
        return float(y[0])
    vectors = np.stack((x - x[0], y - y[0]), axis=1)
    unit = line / norm
    distances = np.linalg.norm(vectors - np.outer(vectors @ unit, unit), axis=1)
    return float(y[int(np.argmax(distances))])


def normalize_attention(value: Any) -> np.ndarray:
    array = finite_attention(value)
    total = float(array.sum())
    if total <= 0.0:
        raise ValueError("attention map must have positive mass")
    return array / total


def retained_mass_support(value: Any, rho: float = 0.5) -> np.ndarray:
    if not 0.0 < float(rho) <= 1.0:
        raise ValueError("rho must be in (0, 1]")
    weights = normalize_attention(value)
    order = np.argsort(-weights.ravel(), kind="stable")
    count = int(
        np.searchsorted(
            np.cumsum(weights.ravel()[order]), float(rho), side="left"
        )
        + 1
    )
    support = np.zeros(weights.size, dtype=bool)
    support[order[:count]] = True
    return support.reshape(weights.shape)


def fractional_token_iou(support: Any, occupancy: Any) -> float:
    selected = np.asarray(support, dtype=bool)
    target = np.clip(np.asarray(occupancy, dtype=np.float64), 0.0, 1.0)
    if selected.shape != target.shape:
        raise ValueError("support and occupancy shapes differ")
    intersection = float(target[selected].sum())
    union = float(selected.sum() + target.sum() - intersection)
    return intersection / union if union > 0.0 else 0.0


def support50_fiou(attention: Any, occupancy: Any) -> float:
    return fractional_token_iou(retained_mass_support(attention, 0.5), occupancy)


def normalized_box_occupancy(box: Sequence[float], grid_h: int, grid_w: int) -> np.ndarray:
    """Fractional token occupancy for a box in the normalized 0--1000 plane."""
    if len(box) != 4 or grid_h <= 0 or grid_w <= 0:
        raise ValueError("box/grid shape is invalid")
    x1, y1, x2, y2 = map(float, box)
    if x2 <= x1 or y2 <= y1:
        raise ValueError("box must have positive area")
    output = np.zeros((grid_h, grid_w), dtype=np.float64)
    for row in range(grid_h):
        top = row * 1000.0 / grid_h
        bottom = (row + 1) * 1000.0 / grid_h
        for column in range(grid_w):
            left = column * 1000.0 / grid_w
            right = (column + 1) * 1000.0 / grid_w
            overlap = max(0.0, min(right, x2) - max(left, x1)) * max(
                0.0, min(bottom, y2) - max(top, y1)
            )
            output[row, column] = overlap / ((right - left) * (bottom - top))
    if float(output.sum()) <= 0.0:
        raise ValueError("box has zero occupancy on the token grid")
    return output
