import importlib.util
import sys
from pathlib import Path

import pytest

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "screen_head_stability_suite.py"
)
SPEC = importlib.util.spec_from_file_location("screen_head_stability_suite", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
sys.path.insert(0, str(MODULE_PATH.parent))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_suite_entries_preserve_order_and_require_unique_values(tmp_path):
    root = tmp_path / "suite"
    config = {
        "checkpoint_suite": {
            "work_dir": str(root),
            "checkpoints": [
                {"label": "step1", "path": str(tmp_path / "checkpoint1")},
                {"label": "step2", "path": str(tmp_path / "checkpoint2")},
            ],
        }
    }
    work_dir, entries = MODULE.suite_entries(config)
    assert work_dir == root
    assert [item["label"] for item in entries] == ["step1", "step2"]

    config["checkpoint_suite"]["checkpoints"][1]["label"] = "step1"
    with pytest.raises(ValueError, match="must be unique"):
        MODULE.suite_entries(config)


def test_checkpoint_log_payload_lists_every_selected_set(tmp_path):
    latest = tmp_path / "latest.json"
    result = {
        "records": 100,
        "selected_sets": {
            "query": {
                "3": ["L2H01", "L3H02", "L4H03"],
                "5": ["L2H01", "L3H02", "L4H03", "L5H04", "L6H05"],
            },
            "reference": {
                "3": ["L7H06", "L8H07", "L9H08"],
                "5": ["L7H06", "L8H07", "L9H08", "L10H09", "L11H10"],
            },
        },
    }
    payload = MODULE.checkpoint_log_payload("step1", "/checkpoint1", latest, result)
    assert payload["records"] == 100
    assert payload["query_top5"][-1] == "L6H05"
    assert payload["reference_top3"] == ["L7H06", "L8H07", "L9H08"]
    assert payload["result_json"] == str(latest)


def test_aggregate_log_payloads_include_query_and_reference_topk():
    cell = {
        "adjacent_jaccard_min": 0.5,
        "adjacent_jaccard_mean": 0.75,
        "all_checkpoint_intersection": ["L2H01"],
        "all_checkpoint_union": ["L2H01", "L3H02"],
    }
    summary = {
        "roles": {
            "query": {"3": cell, "5": cell},
            "reference": {"3": cell, "5": cell},
        }
    }
    payloads = list(MODULE.aggregate_log_payloads(summary))
    assert [(item["role"], item["top_k"]) for item in payloads] == [
        ("query", 3),
        ("query", 5),
        ("reference", 3),
        ("reference", 5),
    ]
