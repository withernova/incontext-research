import importlib.util
from pathlib import Path

import numpy as np
import pytest

_MODULE_PATH = Path(__file__).parents[1] / "iploc_szy" / "head_screening" / "dual_role_metrics.py"
_SPEC = importlib.util.spec_from_file_location("e012_dual_role_metrics", _MODULE_PATH)
_MODULE = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(_MODULE)

CONTRACT = _MODULE.CONTRACT
CONTRACT_SHA256 = _MODULE.CONTRACT_SHA256
central_difference = _MODULE.central_difference
compare_derivatives = _MODULE.compare_derivatives
coordinate_prediction_rows = _MODULE.coordinate_prediction_rows
coordinate_target_positions = _MODULE.coordinate_target_positions
damage_difference_in_difference = _MODULE.damage_difference_in_difference
edge_contribution = _MODULE.edge_contribution
role_contributions = _MODULE.role_contributions
reference_spatial_contribution_metrics = _MODULE.reference_spatial_contribution_metrics
target_specific_damage = _MODULE.target_specific_damage
target_preference_from_weights = _MODULE.target_preference_from_weights
target_vs_null_log = _MODULE.target_vs_null_log
validate_coordinate_positions = _MODULE.validate_coordinate_positions
validate_analysis_contract = _MODULE.validate_analysis_contract
run_r004_scaffold = _MODULE.run_r004_scaffold


def test_coordinate_positions_keep_all_subtokens_and_exclude_format_tokens():
    input_ids = [100, 10, 11, 90, 20, 91, 30, 31, 92, 40, 101]
    labels = [-100, 10, 11, -100, 20, -100, 30, 31, -100, 40, -100]
    fields = {"x1": [1, 2], "y1": [4], "x2": [6, 7], "y2": [9]}
    validated = validate_coordinate_positions(input_ids, labels, fields)
    assert coordinate_target_positions(validated) == (1, 2, 4, 6, 7, 9)
    assert coordinate_prediction_rows(validated) == (0, 1, 3, 5, 6, 8)


@pytest.mark.parametrize(
    "fields, message",
    [
        ({"x1": [0], "y1": [4], "x2": [6], "y2": [9]}, "valid p-1"),
        ({"x1": [1], "y1": [1], "x2": [6], "y2": [9]}, "overlapping"),
        ({"x1": [2, 1], "y1": [4], "x2": [6], "y2": [9]}, "sorted"),
        ({"x1": [1], "y1": [], "x2": [6], "y2": [9]}, "non-empty"),
    ],
)
def test_coordinate_positions_fail_closed(fields, message):
    ids = list(range(12))
    labels = ids.copy()
    with pytest.raises(ValueError, match=message):
        validate_coordinate_positions(ids, labels, fields)


def test_coordinate_positions_reject_unsupervised_target():
    ids = list(range(12))
    labels = ids.copy()
    labels[6] = -100
    fields = {"x1": [1], "y1": [4], "x2": [6], "y2": [9]}
    with pytest.raises(ValueError, match="unsupervised"):
        validate_coordinate_positions(ids, labels, fields)


def test_edge_contribution_preserves_signed_and_absolute_values():
    attention = np.array([[[[0.25, 0.75]]]])
    gradient = np.array([[[[2.0, -4.0]]]])
    signed, absolute = edge_contribution(attention, gradient)
    np.testing.assert_allclose(signed, [[[[0.5, -3.0]]]])
    np.testing.assert_allclose(absolute, [[[[0.5, 3.0]]]])


def test_target_preference_distinguishes_uniform_target_and_background():
    occupancy = np.array([0.0, 0.5, 1.0, 0.0])
    result = target_preference_from_weights(
        np.array([[0.25, 0.25, 0.25, 0.25], [0.0, 0.0, 4.0, 0.0],
                  [3.0, 0.0, 0.0, 0.0]]),
        occupancy,
    )
    np.testing.assert_allclose(result["target_preference"], [0.0, 1.0, 0.0])
    assert result["target_preference_raw"][2] < 0
    assert result["valid"].all()


def test_target_preference_marks_zero_mass_and_flat_grid_undefined():
    zero = target_preference_from_weights([[0.0, 0.0]], [0.0, 1.0])
    assert zero["invalid_zero_mass"].item()
    assert np.isnan(zero["target_preference"]).item()
    flat = target_preference_from_weights([[1.0, 1.0]], [1.0, 1.0])
    assert flat["invalid_spatial_grid"].item()
    assert np.isnan(flat["target_preference_raw"]).item()


def test_reference_metrics_sum_absolute_edges_before_spatial_normalization():
    # Two bbox rows have opposite signed contributions on reference token 0.
    attention = np.array([[[[0.5, 0.5, 0.0], [0.5, 0.5, 0.0]]]])
    gradient = np.array([[[[2.0, 1.0, 0.0], [-2.0, 1.0, 0.0]]]])
    result = reference_spatial_contribution_metrics(
        attention, gradient, [True, True, False], [1.0, 0.0, 0.0]
    )
    np.testing.assert_allclose(
        result["signed_contribution_by_reference_token"], [[[0.0, 1.0]]]
    )
    np.testing.assert_allclose(
        result["contribution_by_reference_token"], [[[2.0, 1.0]]]
    )
    np.testing.assert_allclose(result["reference_abs_contribution"], [[3.0]])
    np.testing.assert_allclose(
        result["contribution_spatial"]["distribution"], [[[2.0 / 3.0, 1.0 / 3.0]]]
    )
    np.testing.assert_allclose(
        result["contribution_spatial"]["target_preference"], [[1.0 / 3.0]]
    )


def test_role_contributions_are_per_role_and_fractional():
    # [layer=1, head=1, rows=2, keys=6]
    attention = np.ones((1, 1, 2, 6), dtype=np.float64)
    gradient = np.array([[[[1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6]]]], dtype=np.float64)
    masks = {
        "R": [True, True, True, False, False, False],
        "Q": [False, False, False, True, True, True],
    }
    occupancies = {
        "R": [1.0, 0.5, 0.0, 0.0, 0.0, 0.0],
        "Q": [0.0, 0.0, 0.0, 1.0, 0.5, 0.0],
    }
    result = role_contributions(attention, gradient, masks, occupancies)
    assert result["contract"] == CONTRACT
    reference = result["roles"]["R"]
    query = result["roles"]["Q"]
    np.testing.assert_allclose(reference["role_visual_abs_contrib"], [[12.0]])
    np.testing.assert_allclose(reference["target_contrib"], [[4.0]])
    np.testing.assert_allclose(reference["background_contrib"], [[8.0]])
    np.testing.assert_allclose(query["role_visual_abs_contrib"], [[30.0]])
    np.testing.assert_allclose(query["target_contrib"], [[13.0]])
    np.testing.assert_allclose(query["background_contrib"], [[17.0]])
    np.testing.assert_allclose(reference["tcr"], [[1.0 / 3.0]])
    assert not reference["all_contribution_denominator_zero"].any()
    assert not reference["role_contribution_denominator_zero"].any()


def test_role_contributions_reject_overlap_and_outside_occupancy():
    value = np.ones((1, 1, 1, 4))
    with pytest.raises(ValueError, match="disjoint"):
        role_contributions(value, value, {"R": [1, 1, 0, 0], "Q": [0, 1, 1, 0]},
                           {"R": [1, 0, 0, 0], "Q": [0, 1, 0, 0]})
    with pytest.raises(ValueError, match="outside"):
        role_contributions(value, value, {"R": [1, 1, 0, 0]},
                           {"R": [1, 0, 1, 0]})


def test_role_contributions_require_target_and_background_area():
    value = np.ones((1, 1, 1, 2))
    with pytest.raises(ValueError, match="both be positive"):
        role_contributions(value, value, {"Q": [1, 1]}, {"Q": [1.0, 1.0]})


def test_target_vs_null_uses_mean_null_density():
    target = np.array([[6.0]])
    null = np.array([[[2.0]], [[8.0]]])
    # target density=3; null densities are 1 and 2, mean=1.5; log ratio=log(2)
    score = target_vs_null_log(target, 2.0, null, [2.0, 4.0])
    np.testing.assert_allclose(score, [[np.log(2.0)]], rtol=1e-10)


def test_finite_difference_and_derivative_comparison():
    derivative = central_difference(0.8, 1.2, 0.1)
    assert derivative == pytest.approx(2.0)
    comparison = compare_derivatives(1.8, derivative)
    assert comparison["sign_agreement"] is True
    assert comparison["relative_error"] == pytest.approx(0.1)
    assert compare_derivatives(-1.0, 1.0)["sign_agreement"] is False


def test_target_specific_damage_and_control_did_are_samplewise():
    target = np.array([0.5, 0.2])
    background = np.array([[0.1, 0.3], [0.0, 0.1]])
    damage = target_specific_damage(target, background)
    np.testing.assert_allclose(damage, [0.3, 0.15])
    controls = np.array([[0.1, 0.2], [0.05, 0.15]])
    did = damage_difference_in_difference(damage, controls)
    np.testing.assert_allclose(did, [0.15, 0.05])


def test_analysis_contract_requires_frozen_parameters_and_pinned_hash():
    config = {
        "analysis": {
            "metric_contract": {"schema": CONTRACT, "sha256": CONTRACT_SHA256},
            "required_parameters": {"epsilon": 0.02, "indices": [1, 2]},
        }
    }
    result = validate_analysis_contract(config)
    assert result["contract"] == CONTRACT
    with pytest.raises(ValueError, match="not frozen"):
        validate_analysis_contract({
            "analysis": {
                "metric_contract": {"schema": CONTRACT, "sha256": CONTRACT_SHA256},
                "required_parameters": {"epsilon": None},
            }
        })
    with pytest.raises(ValueError, match="sha256"):
        validate_analysis_contract({
            "analysis": {
                "metric_contract": {"schema": CONTRACT, "sha256": "0" * 64},
                "required_parameters": {"epsilon": 0.02},
            }
        })


def test_r004_scaffold_refuses_to_masquerade_as_model_worker(tmp_path):
    config = {
        "analysis": {
            "metric_contract": {"schema": CONTRACT, "sha256": CONTRACT_SHA256},
            "required_parameters": {"epsilon": 0.02},
        }
    }
    with pytest.raises(RuntimeError, match="model-hook worker is not implemented"):
        run_r004_scaffold(config=config, snapshot_dir=tmp_path)


def test_metric_functions_reject_nonfinite_and_shape_mismatch():
    with pytest.raises(ValueError, match="shapes differ"):
        edge_contribution(np.ones((1, 1, 1, 2)), np.ones((1, 1, 2, 2)))
    with pytest.raises(ValueError, match="finite"):
        target_specific_damage([np.nan], [[0.0]])
    with pytest.raises(ValueError, match="background must"):
        target_specific_damage([1.0], [0.0])
