import json
from pathlib import Path

import numpy as np
import pytest

from iploc_szy.head_screening.eval_stratified_reference_maps import (
    checked_json,
    distribution_metrics,
    equal_head_ensemble,
    read_predictions,
    select_iou_extremes,
    sha256,
)


def _rows():
    rows = []
    for dataset, offset in (("LaSOT", 0), ("GOT10k", 10), ("TAO", 20)):
        for position, iou in enumerate((0.0, 0.1, 0.5, 0.8, 0.9, 1.0)):
            rows.append({
                "dataset": dataset,
                "dataset_index": offset + position,
                "id": f"{offset + position}-1",
                "iou": iou,
            })
    return rows


def test_select_iou_extremes_is_balanced_deterministic_and_disjoint():
    selected = select_iou_extremes(_rows(), 2, ("LaSOT", "GOT10k", "TAO"))
    assert len(selected) == 12
    assert [(row["dataset_index"], row["stratum"]) for row in selected[:4]] == [
        (0, "low_iou"), (1, "low_iou"), (5, "high_iou"), (4, "high_iou")
    ]
    for dataset in ("LaSOT", "GOT10k", "TAO"):
        subset = [row for row in selected if row["dataset"] == dataset]
        assert [row["stratum"] for row in subset].count("low_iou") == 2
        assert [row["stratum"] for row in subset].count("high_iou") == 2
        assert len({row["dataset_index"] for row in subset}) == 4


def test_equal_head_ensemble_normalizes_each_head_before_equal_weighting():
    first = np.asarray([[1.0, 1.0], [0.0, 0.0]])
    second = np.asarray([[0.0, 0.0], [2.0, 6.0]])
    ensemble = equal_head_ensemble([first, second])
    expected = 0.5 * (first / first.sum() + second / second.sum())
    np.testing.assert_allclose(ensemble, expected)
    assert ensemble.sum() == pytest.approx(1.0)


def test_distribution_metrics_reports_conditional_mass_enrichment_and_pointing():
    distribution = np.asarray([[0.6, 0.1], [0.2, 0.1]])
    occupancy = np.asarray([[1.0, 0.0], [0.0, 0.0]])
    metrics = distribution_metrics(distribution, distribution * 0.2, occupancy)
    assert metrics["conditional_gt_mass"] == pytest.approx(0.6)
    assert metrics["gt_area_fraction"] == pytest.approx(0.25)
    assert metrics["gt_enrichment"] == pytest.approx(2.4)
    assert metrics["pointing_token_overlaps_gt"] is True
    assert metrics["reference_span_mass"] == pytest.approx(0.2)


def test_artifact_hashes_and_prediction_identity_fail_closed(tmp_path: Path):
    payload = tmp_path / "payload.json"
    payload.write_text('{"status":"completed"}\n', encoding="utf-8")
    assert checked_json(payload, sha256(payload))["status"] == "completed"
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        checked_json(payload, "0" * 64)

    predictions = tmp_path / "predictions.jsonl"
    rows = _rows()[:2]
    predictions.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    assert len(read_predictions(predictions, sha256(predictions))) == 2
    rows[1]["dataset_index"] = rows[0]["dataset_index"]
    predictions.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    with pytest.raises(ValueError, match="unique dataset indices"):
        read_predictions(predictions, sha256(predictions))
