"""Bounding-box metrics for generated localization answers."""

from typing import Any, Dict, List, Optional, Sequence

from ..prompting.coordinates import parse_box
from ..registry import EVALUATORS


def box_iou(first: Any, second: Any) -> float:
    """Compute xyxy intersection over union; invalid boxes receive zero."""
    first_box = parse_box(first)
    second_box = parse_box(second)
    if first_box is None or second_box is None:
        return 0.0

    intersection_width = max(
        0.0,
        min(first_box[2], second_box[2]) - max(first_box[0], second_box[0]),
    )
    intersection_height = max(
        0.0,
        min(first_box[3], second_box[3]) - max(first_box[1], second_box[1]),
    )
    intersection = intersection_width * intersection_height
    first_area = max(0.0, first_box[2] - first_box[0]) * max(
        0.0, first_box[3] - first_box[1]
    )
    second_area = max(0.0, second_box[2] - second_box[0]) * max(
        0.0, second_box[3] - second_box[1]
    )
    union = first_area + second_area - intersection
    return intersection / union if union > 0 else 0.0


@EVALUATORS.register_module()
class LocalizationEvaluator:
    """Aggregate parse rate, mean IoU, and thresholded localization accuracy."""

    def __init__(self, iou_thresholds: Sequence[float] = (0.3, 0.5, 0.7)) -> None:
        self.thresholds = tuple(float(value) for value in iou_thresholds)
        self.rows: List[Dict[str, Any]] = []

    def process(
        self,
        prediction: Any,
        target: Any,
        sample_id: Optional[str] = None,
    ) -> None:
        """Add one generated prediction and its target to the accumulator."""
        self.rows.append(
            {
                "id": sample_id,
                "prediction": prediction,
                "target": target,
                "iou": box_iou(prediction, target),
                "parsed": parse_box(prediction) is not None,
            }
        )

    @staticmethod
    def _percentile(sorted_values: Sequence[float], quantile: float) -> float:
        """Linearly interpolate a percentile without adding a dependency."""
        if not sorted_values:
            return 0.0
        position = (len(sorted_values) - 1) * quantile
        lower = int(position)
        upper = min(lower + 1, len(sorted_values) - 1)
        fraction = position - lower
        return sorted_values[lower] * (1.0 - fraction) + sorted_values[upper] * fraction

    @classmethod
    def _distribution(cls, values: Sequence[float]) -> Dict[str, Any]:
        sorted_values = sorted(float(value) for value in values)
        edges = (0.0, 0.1, 0.25, 0.5, 0.75, 1.0000001)
        bins = {}
        for left, right in zip(edges[:-1], edges[1:]):
            label = f"[{left:.2f},{min(right, 1.0):.2f}{']' if right > 1.0 else ')'}"
            bins[label] = sum(left <= value < right for value in sorted_values)
        return {
            "count": len(sorted_values),
            "min": sorted_values[0] if sorted_values else 0.0,
            "q25": cls._percentile(sorted_values, 0.25),
            "median": cls._percentile(sorted_values, 0.5),
            "q75": cls._percentile(sorted_values, 0.75),
            "max": sorted_values[-1] if sorted_values else 0.0,
            "bins": bins,
        }

    def evaluate(self) -> Dict[str, Any]:
        """Return aggregate metrics plus a non-mean IoU distribution."""
        sample_count = len(self.rows)
        if sample_count == 0:
            base: Dict[str, Any] = {"samples": 0, "parse_rate": 0.0, "miou": 0.0}
            base.update({f"acc_iou_{t}": 0.0 for t in self.thresholds})
            base["iou_distribution"] = self._distribution([])
            return base

        metrics: Dict[str, float] = {
            "samples": sample_count,
            "parse_rate": sum(row["parsed"] for row in self.rows) / sample_count,
            "miou": sum(row["iou"] for row in self.rows) / sample_count,
        }
        for threshold in self.thresholds:
            metrics[f"acc_iou_{threshold}"] = (
                sum(row["iou"] >= threshold for row in self.rows) / sample_count
            )
        metrics["iou_distribution"] = self._distribution(
            [row["iou"] for row in self.rows]
        )
        return metrics
