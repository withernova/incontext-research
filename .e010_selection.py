"""Pure head-selection helpers for IPLoc-ID reliability audits."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Sequence, Tuple

import numpy as np

Head = Tuple[int, int]


@dataclass(frozen=True)
class SelectionResult:
    ranked_heads: Tuple[Head, ...]
    frequency: Mapping[Head, int]
    eligible_heads: Tuple[Head, ...]


def _array(value) -> np.ndarray:
    out = np.asarray(value, dtype=np.float64)
    if out.ndim != 2 or out.size == 0 or not np.isfinite(out).all() or (out < 0).any():
        raise ValueError("attention map must be a finite nonnegative 2D array")
    return out


def image_attention_sum(value) -> float:
    return float(_array(value).sum())


def spatial_component_entropy(value, mean_multiplier: float = 1.0) -> float:
    """Entropy of 8-connected positive components after mean thresholding."""
    arr = _array(value)
    active = np.maximum(arr - float(mean_multiplier) * float(arr.mean()), 0.0)
    total = float(active.sum())
    if total <= 0:
        return float("inf")
    try:
        from scipy.ndimage import label
    except ImportError as exc:
        raise RuntimeError("scipy is required for component entropy") from exc
    labels, count = label(active > 0, structure=np.ones((3, 3), dtype=np.int8))
    masses = np.asarray([active[labels == index].sum() for index in range(1, count + 1)], dtype=np.float64)
    probabilities = masses[masses > 0] / total
    return float(-(probabilities * np.log(probabilities)).sum())


def chord_threshold(values: Sequence[float]) -> float:
    vals = np.asarray(values, dtype=np.float64)
    if vals.ndim != 1 or vals.size == 0 or not np.isfinite(vals).all():
        raise ValueError("threshold values must be a nonempty finite vector")
    if vals.size <= 2:
        return float(vals.min())
    y = np.sort(vals)
    x = np.arange(y.size, dtype=np.float64)
    line = np.array([x[-1] - x[0], y[-1] - y[0]], dtype=np.float64)
    norm = float(np.linalg.norm(line))
    if norm == 0:
        return float(y[0])
    vectors = np.stack((x - x[0], y - y[0]), axis=1)
    unit = line / norm
    distances = np.linalg.norm(vectors - np.outer(vectors @ unit, unit), axis=1)
    return float(y[int(np.argmax(distances))])


def select_fixed_heads(
    samples: Sequence[Mapping[Head, object]], *, per_sample: int = 10,
    mean_multiplier: float = 1.0, excluded_layers: Iterable[int] = (0, 1),
) -> SelectionResult:
    if not samples:
        raise ValueError("no samples supplied")
    heads = set(samples[0])
    if not heads or any(set(sample) != heads for sample in samples):
        raise ValueError("every sample must contain the same nonempty head set")
    excluded = set(map(int, excluded_layers))
    means = {head: float(np.mean([image_attention_sum(sample[head]) for sample in samples])) for head in heads}
    threshold = chord_threshold(list(means.values()))
    eligible = tuple(sorted(head for head in heads if head[0] not in excluded and means[head] >= threshold))
    if not eligible:
        raise ValueError("image-attention threshold left no eligible heads")
    frequency: Counter[Head] = Counter()
    for sample in samples:
        ranked = sorted(eligible, key=lambda head: (spatial_component_entropy(sample[head], mean_multiplier), head))
        frequency.update(ranked[: min(int(per_sample), len(ranked))])
    ranked_heads = tuple(sorted(eligible, key=lambda head: (-frequency[head], head)))
    return SelectionResult(ranked_heads, dict(frequency), eligible)


def fixed_top(result: SelectionResult, count: int) -> Tuple[Head, ...]:
    if count <= 0 or count > len(result.ranked_heads):
        raise ValueError("requested head count is outside the ranked list")
    return result.ranked_heads[:count]


def layer_matched_random(heads: Sequence[Head], universe: Iterable[Head], seed: int) -> Tuple[Head, ...]:
    rng = np.random.default_rng(int(seed)); pool = set(universe); chosen = []
    for layer, _ in heads:
        candidates = sorted(head for head in pool if head[0] == layer)
        if not candidates:
            raise ValueError(f"no unused random-control head in layer {layer}")
        pick = candidates[int(rng.integers(len(candidates)))]
        chosen.append(pick); pool.remove(pick)
    return tuple(chosen)
