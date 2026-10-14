from pathlib import Path

import numpy as np

from iploc_szy.head_screening.finders import R003T003HeadFinder
from iploc_szy.head_screening.hooks import HeadScreeningHook, set_jaccard
from iploc_szy.head_screening.metrics import (
    component_token_entropy,
    normalized_box_occupancy,
    support50_fiou,
)
from iploc_szy.head_screening.probes import consecutive_spans, unique_subsequence


def test_r003_component_entropy_uses_binary_eight_connected_token_counts():
    connected = np.asarray([[3.0, 3.0, 0.0], [0.0, 3.0, 0.0], [0.0, 0.0, 0.0]])
    split = np.asarray([[3.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 3.0]])
    assert component_token_entropy(connected) == 0.0
    assert np.isclose(component_token_entropy(split), np.log(2.0))


def test_fractional_occupancy_and_support50_iou():
    target = normalized_box_occupancy([0, 0, 500, 500], 2, 2)
    attention = np.asarray([[10.0, 1.0], [1.0, 1.0]])
    assert target.tolist() == [[1.0, 0.0], [0.0, 0.0]]
    assert support50_fiou(attention, target) == 1.0


def test_r003_t003_finder_keeps_roles_and_gt_boundary(tmp_path: Path):
    maps = np.ones((3, 2, 2, 2), dtype=np.float32)
    maps[1, 0] = np.asarray([[10.0, 1.0], [1.0, 1.0]])
    target = np.asarray([[1.0, 0.0], [0.0, 0.0]], dtype=np.float32)
    records = []
    for index in range(2):
        artifact = tmp_path / f"sample_{index}.npz"
        np.savez_compressed(
            artifact,
            q_to_q=maps,
            q_to_r=maps,
            query_target=target,
            reference_target=target,
        )
        records.append({"artifact": str(artifact)})
    finder = R003T003HeadFinder(
        per_sample=1,
        excluded_layers=(0,),
        fixed_head_counts=(1,),
    )
    result = finder.find(records)
    assert result["selected_sets"]["query"]["1"] == ["L1H00"]
    assert result["selected_sets"]["reference"]["1"] == ["L1H00"]
    assert result["roles"]["r003_query_nogt"]["gt_used_in_ranking"] is False
    assert result["roles"]["t003_reference_gt_reward"]["gt_used_in_ranking"] is True
    assert result["row_contract"] == "teacher_forced_query_bbox_pminus1/v1"


def test_probe_alignment_helpers_are_fail_closed():
    assert consecutive_spans([9, 2, 2, 8, 2], 2) == [(1, 3), (4, 5)]
    assert unique_subsequence([0, 1, 2, 3, 4], [2, 3], 1, 5) == [2, 3]


def test_half_epoch_schedule_and_set_stability():
    hook = object.__new__(HeadScreeningHook)
    hook.start_epoch = 0.5
    hook.interval_epochs = 0.5
    assert hook._next_boundary(0, 100) == 50
    assert hook._next_boundary(50, 100) == 100
    assert hook._next_boundary(825, 100) == 850
    assert set_jaccard(["a", "b"], ["b", "c"]) == 1 / 3
