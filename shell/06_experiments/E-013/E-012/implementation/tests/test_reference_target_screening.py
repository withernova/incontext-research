import importlib.util
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest


MODULE = Path(__file__).parents[1] / "iploc_szy/head_screening/reference_target_screening.py"
SPEC = importlib.util.spec_from_file_location("e012_reference_target_screening", MODULE)
SCREENING = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(SCREENING)


def record(c, ta, td, va=None, vd=None, legacy=None, iou=None):
    array = np.asarray(c, dtype=float)
    return {
        "reference_abs_contribution": array,
        "attention_target_preference": np.asarray(ta, dtype=float),
        "contribution_target_preference": np.asarray(td, dtype=float),
        "attention_valid": np.ones_like(array, dtype=bool) if va is None else va,
        "contribution_valid": np.ones_like(array, dtype=bool) if vd is None else vd,
        "legacy_gradient": array if legacy is None else np.asarray(legacy, dtype=float),
        "spatial_iou": np.zeros_like(array) if iou is None else np.asarray(iou, dtype=float),
    }


def test_four_selectors_separate_qualification_from_ranking():
    records = [
        record([[10, 8, 2]], [[0.2, 0.9, 1.0]], [[0.9, 0.9, 1.0]],
               legacy=[[10, 8, 2]], iou=[[0.8, 0.2, 0.9]]),
        record([[10, 8, 2]], [[0.2, 0.8, 1.0]], [[0.9, 0.8, 1.0]],
               legacy=[[10, 8, 2]], iou=[[0.8, 0.2, 0.9]]),
    ]
    result = SCREENING.aggregate_reference_screening(
        records, tau_c=5, tau_a=0.7, tau_d=0.7,
        qualification_frequency_min=1.0, top_k=2,
    )
    selectors = result["selectors"]
    assert selectors["c_r_only"][0]["head"] == 0
    assert selectors["legacy_gradient_iou"][0]["head"] == 0
    assert selectors["c_r_target_attention"][0]["head"] == 1
    assert [item["head"] for item in selectors["target_grounded_combined"]] == [1]


def test_undefined_samples_stay_in_total_denominator_and_cannot_pass():
    valid = np.array([[True, False]])
    records = [record([[4, 9]], [[0.9, 1.0]], [[0.9, 1.0]], va=valid, vd=valid),
               record([[4, 9]], [[0.9, 1.0]], [[0.9, 1.0]], va=valid, vd=valid)]
    result = SCREENING.aggregate_reference_screening(
        records, tau_c=1, tau_a=0.5, tau_d=0.5,
        qualification_frequency_min=0.5, top_k=2,
    )
    assert result["n_total"] == 2
    assert result["validity"]["joint_valid_count"].tolist() == [[2, 0]]
    assert [item["head"] for item in result["selectors"]["target_grounded_combined"]] == [0]


def test_nan_is_allowed_only_for_entries_marked_invalid():
    invalid = record([[1]], [[np.nan]], [[np.nan]], va=[[False]], vd=[[False]], iou=[[1]])
    result = SCREENING.aggregate_reference_screening(
        [invalid], tau_c=0, tau_a=0, tau_d=0,
        qualification_frequency_min=0.5, top_k=1,
    )
    assert result["validity"]["joint_valid_count"].item() == 0
    assert result["selectors"]["target_grounded_combined"] == []
    invalid["attention_valid"] = [[True]]
    with pytest.raises(ValueError, match="valid Target Preference"):
        SCREENING.aggregate_reference_screening(
            [invalid], tau_c=0, tau_a=0, tau_d=0,
            qualification_frequency_min=0.5, top_k=1,
        )


def test_sample_first_normalization_prevents_large_scale_sample_domination():
    records = [record([[1000, 1]], [[0.1, 1]], [[0.1, 1]]),
               record([[1, 1]], [[1, 1]], [[1, 1]])]
    result = SCREENING.aggregate_reference_screening(
        records, tau_c=0, tau_a=0, tau_d=0,
        qualification_frequency_min=0, top_k=2,
    )
    combined = result["head_metrics"]["combined_score_mean"]
    # Without sample-first normalization head 0 would outweigh head 1 by about
    # 50x. Each sample instead contributes one equal-weight normalized score.
    assert combined[0, 0] / combined[0, 1] < 1.2


@pytest.mark.parametrize("kwargs", [
    {"tau_c": -1, "tau_a": 0, "tau_d": 0, "qualification_frequency_min": 0, "top_k": 1},
    {"tau_c": 0, "tau_a": 1.1, "tau_d": 0, "qualification_frequency_min": 0, "top_k": 1},
    {"tau_c": 0, "tau_a": 0, "tau_d": 0, "qualification_frequency_min": 2, "top_k": 1},
])
def test_thresholds_fail_closed(kwargs):
    with pytest.raises(ValueError):
        SCREENING.aggregate_reference_screening(
            [record([[1]], [[1]], [[1]], iou=[[1]])], **kwargs
        )


def test_json_ready_removes_numpy_values():
    value = SCREENING.json_ready({"array": np.array([1, 2]), "scalar": np.float64(3)})
    assert value == {"array": [1, 2], "scalar": 3.0}


def test_r005_entrypoint_freezes_discovery_and_checks_disjoint_confirmation(tmp_path):
    rows = []
    for split, component in (("discovery", "d1"), ("confirmation", "c1")):
        item = record([[3, 1]], [[0.9, 0.2]], [[0.8, 0.2]], iou=[[0.2, 0.8]])
        item = {key: np.asarray(value).tolist() for key, value in item.items()}
        item.update(split=split, component_id=component)
        rows.append(item)
    source = tmp_path / "records.json"
    source.write_text(json.dumps({
        "schema": "e012.reference-target-screening-records/v1", "records": rows
    }))
    work = tmp_path / "work"
    required = dict(input_records=str(source),
        input_records_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        tau_c=1, tau_a=0.5, tau_d=0.5,
        qualification_frequency_min=1, top_k=1, legacy_iou_threshold=0.5)
    result = SCREENING.run_r005_from_records(
        config={"work_dir": str(work), "analysis": {"required_parameters": required}},
        snapshot_dir=tmp_path,
    )
    summary = json.loads(Path(result["summary"]).read_text())
    assert summary["component_overlap"] == 0
    assert summary["discovery"]["selectors"]["target_grounded_combined"][0]["head"] == 0
    assert summary["frozen_confirmation"]["target_grounded_combined"][0]["head"] == 0


def test_r005_entrypoint_rejects_component_leakage(tmp_path):
    item = record([[1]], [[1]], [[1]], iou=[[1]])
    base = {key: np.asarray(value).tolist() for key, value in item.items()}
    rows = [{**base, "split": split, "component_id": "shared"}
            for split in ("discovery", "confirmation")]
    source = tmp_path / "records.json"
    source.write_text(json.dumps({
        "schema": "e012.reference-target-screening-records/v1", "records": rows
    }))
    required = dict(input_records=str(source),
        input_records_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        tau_c=0, tau_a=0, tau_d=0,
        qualification_frequency_min=0, top_k=1, legacy_iou_threshold=0.5)
    with pytest.raises(ValueError, match="split-disjoint"):
        SCREENING.run_r005_from_records(
            config={"work_dir": str(tmp_path / "work"),
                    "analysis": {"required_parameters": required}},
            snapshot_dir=tmp_path,
        )
