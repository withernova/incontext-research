import copy
import importlib.util
import json
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "analyze_head_stability.py"
SPEC = importlib.util.spec_from_file_location("analyze_head_stability", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
analyze = MODULE.analyze
load_screens = MODULE.load_screens


def payload(query, reference, sample_ids=("a", "b")):
    return {
        "schema": "iploc-szy.head-screening.r003-t003/v1",
        "status": "completed",
        "records": len(sample_ids),
        "row_contract": "teacher_forced_query_bbox_pminus1/v1",
        "head_shape": {"layers": 36, "heads_per_layer": 32},
        "parameters": {"fixed_head_counts": [3]},
        "probe_records": [
            {"dataset_index": index, "sample_id": sample_id}
            for index, sample_id in enumerate(sample_ids)
        ],
        "selected_sets": {
            "query": {"3": query},
            "reference": {"3": reference},
        },
    }


def write_screen(root: Path, label: str, value):
    path = root / f"{label}.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return f"{label}={path}"


def test_analyze_reports_adjacent_and_all_checkpoint_stability(tmp_path):
    values = [
        write_screen(
            tmp_path,
            "step1400",
            payload(["L2H01", "L3H02", "L4H03"], ["L5H04", "L6H05", "L7H06"]),
        ),
        write_screen(
            tmp_path,
            "step1482",
            payload(["L2H01", "L3H02", "L8H07"], ["L5H04", "L6H05", "L7H06"]),
        ),
        write_screen(
            tmp_path,
            "step1564",
            payload(["L2H01", "L3H02", "L9H08"], ["L5H04", "L6H05", "L10H09"]),
        ),
    ]
    summary = analyze(load_screens(values))
    query = summary["roles"]["query"]["3"]
    reference = summary["roles"]["reference"]["3"]
    assert query["adjacent_jaccard_min"] == 0.5
    assert query["all_checkpoint_intersection"] == ["L2H01", "L3H02"]
    assert reference["head_frequency"][0]["checkpoints"] == 3
    assert summary["comparability"]["sample_identity_equal"] is True


def test_load_screens_rejects_different_samples(tmp_path):
    first = payload(["L2H01", "L3H02", "L4H03"], ["L5H04", "L6H05", "L7H06"])
    second = copy.deepcopy(first)
    second["probe_records"][1]["sample_id"] = "different"
    with pytest.raises(ValueError, match="not comparable"):
        load_screens(
            [
                write_screen(tmp_path, "step1400", first),
                write_screen(tmp_path, "step1482", second),
            ]
        )


def test_load_screens_rejects_failed_or_duplicate_heads(tmp_path):
    failed = payload(["L2H01", "L3H02", "L4H03"], ["L5H04", "L6H05", "L7H06"])
    failed["status"] = "failed"
    with pytest.raises(ValueError, match="not completed"):
        load_screens(
            [
                write_screen(tmp_path, "step1400", failed),
                write_screen(
                    tmp_path,
                    "step1482",
                    payload(
                        ["L2H01", "L3H02", "L4H03"],
                        ["L5H04", "L6H05", "L7H06"],
                    ),
                ),
            ]
        )

    duplicate = payload(
        ["L2H01", "L2H01", "L4H03"], ["L5H04", "L6H05", "L7H06"]
    )
    with pytest.raises(ValueError, match="not a unique Top-3"):
        load_screens(
            [
                write_screen(tmp_path, "step1564", duplicate),
                write_screen(
                    tmp_path,
                    "step1646",
                    payload(
                        ["L2H01", "L3H02", "L4H03"],
                        ["L5H04", "L6H05", "L7H06"],
                    ),
                ),
            ]
        )
