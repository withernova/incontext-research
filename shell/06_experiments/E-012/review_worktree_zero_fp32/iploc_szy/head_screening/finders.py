"""Config-built head finders adapted from E010-R003 and R006-T003."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple

import numpy as np

from ..registry import HEAD_FINDERS
from .metrics import (
    chord_threshold,
    component_token_entropy,
    support50_fiou,
)

Head = Tuple[int, int]


def head_name(head: Head) -> str:
    return f"L{head[0]}H{head[1]:02d}"


def _json_float(value: float):
    return float(value) if np.isfinite(value) else None


@HEAD_FINDERS.register_module()
class R003T003HeadFinder:
    """Produce R003 query/reference diagnostics and a T003 reference set.

    R003 branches never read GT.  The T003 branch explicitly uses the
    reference target occupancy during discovery, with the frozen reward
    ``-H_norm + 2 * max(0, S50-fIoU - 0.1)`` by default.
    """

    schema = "iploc-szy.head-screening.r003-t003/v1"

    def __init__(
        self,
        per_sample: int = 10,
        mean_multiplier: float = 1.0,
        excluded_layers: Sequence[int] = (0, 1),
        fixed_head_counts: Sequence[int] = (3, 5),
        entropy_weight: float = 1.0,
        iou_reward_weight: float = 2.0,
        iou_threshold: float = 0.1,
    ) -> None:
        self.per_sample = int(per_sample)
        self.mean_multiplier = float(mean_multiplier)
        self.excluded_layers = tuple(sorted({int(value) for value in excluded_layers}))
        self.fixed_head_counts = tuple(sorted({int(value) for value in fixed_head_counts}))
        self.entropy_weight = float(entropy_weight)
        self.iou_reward_weight = float(iou_reward_weight)
        self.iou_threshold = float(iou_threshold)
        if self.per_sample <= 0 or self.mean_multiplier <= 0.0:
            raise ValueError("per_sample and mean_multiplier must be positive")
        if not self.fixed_head_counts or min(self.fixed_head_counts) <= 0:
            raise ValueError("fixed_head_counts must contain positive integers")
        if self.entropy_weight < 0.0 or self.iou_reward_weight < 0.0:
            raise ValueError("reward weights must be nonnegative")
        if not 0.0 <= self.iou_threshold <= 1.0:
            raise ValueError("iou_threshold must be in [0, 1]")

    def find(self, records: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        if not records:
            raise ValueError("head screening received zero records")
        query_maps, reference_maps, reference_targets, shape = self._load(records)
        r003_query = self._r003_select(query_maps, shape)
        r003_reference = self._r003_select(reference_maps, shape)
        t003_reference = self._t003_select(reference_maps, reference_targets, shape)
        return {
            "schema": self.schema,
            "status": "completed",
            "records": len(records),
            "head_shape": {"layers": shape[0], "heads_per_layer": shape[1]},
            "row_contract": "teacher_forced_query_bbox_pminus1/v1",
            "roles": {
                "r003_query_nogt": r003_query,
                "r003_reference_nogt": r003_reference,
                "t003_reference_gt_reward": t003_reference,
            },
            "selected_sets": {
                "query": r003_query["fixed_heads"],
                "reference": t003_reference["fixed_heads"],
            },
            "parameters": {
                "r003": {
                    "per_sample": self.per_sample,
                    "mean_multiplier": self.mean_multiplier,
                    "excluded_layers": list(self.excluded_layers),
                },
                "t003": {
                    "reward_form": "thresholded_iou_bonus",
                    "iou_metric": "support50_fiou",
                    "entropy_weight": self.entropy_weight,
                    "iou_reward_weight": self.iou_reward_weight,
                    "iou_threshold": self.iou_threshold,
                    "rank_score": (
                        "-normalized_entropy + iou_reward_weight * "
                        "max(0, support50_fiou-iou_threshold)"
                    ),
                },
                "fixed_head_counts": list(self.fixed_head_counts),
            },
            "claim_boundary": (
                "Training-time teacher-forced attention diagnostic. R003 natural-response "
                "semantics are not claimed; T003 uses training GT in discovery; selected "
                "heads are neither causal nor an automatic phase-transition authority."
            ),
        }

    def _load(self, records):
        query_maps = []
        reference_maps = []
        reference_targets = []
        shape = None
        for record in records:
            artifact = Path(str(record["artifact"]))
            with np.load(artifact) as payload:
                query = payload["q_to_q"].astype(np.float64)
                reference = payload["q_to_r"].astype(np.float64)
                target = payload["reference_target"].astype(np.float64)
            if query.ndim != 4 or reference.ndim != 4:
                raise ValueError("head maps must have [layer, head, height, width] shape")
            if query.shape[:2] != reference.shape[:2]:
                raise ValueError("query/reference head dimensions differ")
            if reference.shape[-2:] != target.shape:
                raise ValueError("reference map and target grid shapes differ")
            if (
                not np.isfinite(query).all()
                or not np.isfinite(reference).all()
                or bool((query < 0).any())
                or bool((reference < 0).any())
                or not np.isfinite(target).all()
                or float(target.sum()) <= 0.0
            ):
                raise ValueError("head screening artifact contains invalid values")
            current_shape = tuple(map(int, query.shape[:2]))
            if shape is None:
                shape = current_shape
            elif current_shape != shape:
                raise ValueError("head dimensions changed between probe samples")
            query_maps.append(query)
            reference_maps.append(reference)
            reference_targets.append(target)
        return query_maps, reference_maps, reference_targets, shape

    def _r003_select(self, arrays: Sequence[np.ndarray], shape: Tuple[int, int]):
        layers, heads_per_layer = shape
        head_count = layers * heads_per_layer
        sums = np.asarray(
            [array.reshape(head_count, -1).sum(axis=1) for array in arrays],
            dtype=np.float64,
        )
        entropies = np.asarray(
            [
                [
                    component_token_entropy(item, self.mean_multiplier)
                    for item in array.reshape(head_count, *array.shape[-2:])
                ]
                for array in arrays
            ],
            dtype=np.float64,
        )
        mean_sums = sums.mean(axis=0)
        threshold = chord_threshold(mean_sums.tolist())
        layer_ids = np.repeat(np.arange(layers), heads_per_layer)
        eligible = np.flatnonzero(
            (mean_sums >= threshold)
            & ~np.isin(layer_ids, np.asarray(self.excluded_layers))
        )
        if not eligible.size:
            raise ValueError("R003 image-attention gate left no eligible heads")
        frequency = np.zeros(head_count, dtype=np.int64)
        for row in entropies:
            order = eligible[np.lexsort((eligible, row[eligible]))]
            frequency[order[: min(self.per_sample, len(order))]] += 1
        ranked = eligible[np.lexsort((eligible, -frequency[eligible]))]
        fixed = self._fixed_sets(ranked, layers, heads_per_layer)
        ranking = []
        for index in ranked:
            ranking.append(
                {
                    "head": head_name(divmod(int(index), heads_per_layer)),
                    "selection_frequency": int(frequency[index]),
                    "mean_image_attention_sum": float(mean_sums[index]),
                    "mean_component_entropy": _json_float(float(entropies[:, index].mean())),
                }
            )
        return {
            "gt_used_in_ranking": False,
            "eligible_head_count": int(len(eligible)),
            "image_attention_threshold": float(threshold),
            "fixed_heads": fixed,
            "ranking": ranking,
        }

    def _t003_select(
        self,
        arrays: Sequence[np.ndarray],
        targets: Sequence[np.ndarray],
        shape: Tuple[int, int],
    ):
        layers, heads_per_layer = shape
        head_count = layers * heads_per_layer
        top1_frequency: Counter[int] = Counter()
        top10_frequency: Counter[int] = Counter()
        reward_sums = np.zeros(head_count, dtype=np.float64)
        iou_sums = np.zeros(head_count, dtype=np.float64)
        entropy_sums = np.zeros(head_count, dtype=np.float64)
        for array, target in zip(arrays, targets):
            flattened = array.reshape(head_count, *array.shape[-2:])
            entropy = np.asarray(
                [component_token_entropy(item, self.mean_multiplier) for item in flattened],
                dtype=np.float64,
            )
            normalized_entropy = entropy / np.log(float(flattened[0].size))
            iou = np.asarray(
                [support50_fiou(item, target) for item in flattened], dtype=np.float64
            )
            reward = (
                -self.entropy_weight * normalized_entropy
                + self.iou_reward_weight * np.maximum(0.0, iou - self.iou_threshold)
            )
            order = np.asarray(
                sorted(range(head_count), key=lambda index: (-reward[index], index)),
                dtype=np.int64,
            )
            top1_frequency[int(order[0])] += 1
            top10_frequency.update(map(int, order[:10]))
            reward_sums += reward
            iou_sums += iou
            entropy_sums += normalized_entropy
        ranked_positive = [
            head
            for head, _ in sorted(
                top1_frequency.items(), key=lambda item: (-item[1], item[0])
            )
        ]
        if len(ranked_positive) < max(self.fixed_head_counts):
            raise RuntimeError(
                "T003 produced fewer unique per-sample Top-1 heads than required; "
                f"got {len(ranked_positive)}, need {max(self.fixed_head_counts)}"
            )
        fixed = self._fixed_sets(
            np.asarray(ranked_positive, dtype=np.int64), layers, heads_per_layer
        )
        count = float(len(arrays))
        ranking = []
        for index in sorted(
            range(head_count),
            key=lambda head: (
                -top1_frequency[head],
                -top10_frequency[head],
                -(reward_sums[head] / count),
                head,
            ),
        ):
            ranking.append(
                {
                    "head": head_name(divmod(index, heads_per_layer)),
                    "top1_frequency": int(top1_frequency[index]),
                    "top10_frequency": int(top10_frequency[index]),
                    "mean_reward": _json_float(float(reward_sums[index] / count)),
                    "mean_support50_fiou": float(iou_sums[index] / count),
                    "mean_normalized_entropy": _json_float(
                        float(entropy_sums[index] / count)
                    ),
                }
            )
        return {
            "gt_used_in_ranking": True,
            "fixed_heads": fixed,
            "unique_top1_heads": len(top1_frequency),
            "ranking": ranking,
        }

    def _fixed_sets(
        self, ranked: Iterable[int], layers: int, heads_per_layer: int
    ) -> Dict[str, Sequence[str]]:
        ranked = list(map(int, ranked))
        output = {}
        for count in self.fixed_head_counts:
            if len(ranked) < count:
                raise ValueError(f"cannot select Top-{count} from {len(ranked)} heads")
            output[str(count)] = [
                head_name(divmod(index, heads_per_layer)) for index in ranked[:count]
            ]
        return output


@HEAD_FINDERS.register_module()
class R003QueryHeadFinder(R003T003HeadFinder):
    """Select Query heads on ordinary reference/query samples for GT supervision.

    Reuses the R003 query selector without requiring a T003 reference ranking.
    The input and teacher-forced rows retain the dual-image protocol.
    """

    def find(self, records: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        if not records:
            raise ValueError("head screening received zero records")
        query_maps, _, _, shape = self._load(records)
        query = self._r003_select(query_maps, shape)
        return {
            "schema": "iploc-szy.head-screening.r003-query/v1",
            "status": "completed",
            "records": len(records),
            "head_shape": {"layers": shape[0], "heads_per_layer": shape[1]},
            "row_contract": "teacher_forced_query_bbox_pminus1/v1",
            "selected_sets": {"query": query["fixed_heads"]},
            "roles": {"r003_query_nogt": query},
            "parameters": {"per_sample": self.per_sample,
                           "mean_multiplier": self.mean_multiplier,
                           "excluded_layers": self.excluded_layers,
                           "fixed_head_counts": self.fixed_head_counts},
        }
