import importlib.util
import json
from pathlib import Path

import pytest

TOOL = Path(__file__).parents[1] / "tools" / "build_e009_posthoc_splits.py"
SPEC = importlib.util.spec_from_file_location("build_e009_posthoc_splits", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _row(dataset, sequence, image):
    return {
        "dataset": dataset,
        "sequence": sequence,
        "element": "target",
        "image_path": [image + "-ref.jpg", image + "-query.jpg"],
        "bbox": [[0, 0, 1, 1], [0, 0, 1, 1]],
        "role": ["reference", "positive-image"],
    }


def test_builds_reproducible_disjoint_splits_and_hashes(tmp_path):
    train = tmp_path / "train.json"
    pool = tmp_path / "pool.json"
    train.write_text(json.dumps([_row("LaSOT", "train-1", "train")]))
    pool.write_text(json.dumps([_row("LaSOT", f"test-{i}", f"pool-{i}") for i in range(5)]))
    val, test, audit_path = (tmp_path / name for name in ("val.json", "test.json", "audit.json"))

    audit = MODULE.build_posthoc_splits(
        train, pool, val, test, audit_path, val_size=2, seed=7
    )
    val_rows, test_rows = json.loads(val.read_text()), json.loads(test.read_text())
    assert audit["selection"]["selected_source_indices"] == [1, 2]
    assert [row["sequence"] for row in val_rows] == ["test-1", "test-2"]
    assert [row["sequence"] for row in test_rows] == ["test-0", "test-3", "test-4"]
    assert all(row["metadata"]["split"] == "validation" for row in val_rows)
    assert all(row["metadata"]["split"] == "test" for row in test_rows)
    assert all(value == 0 for kind in audit["overlap"].values() for value in kind.values())
    assert audit["outputs"]["validation_manifest_sha256"] == MODULE._sha256(val)
    assert audit["outputs"]["test_manifest_sha256"] == MODULE._sha256(test)
    assert json.loads(audit_path.read_text())["status"] == "complete"


def test_refuses_leakage_and_overwrite(tmp_path):
    train = tmp_path / "train.json"
    pool = tmp_path / "pool.json"
    shared = _row("LaSOT", "shared-1", "shared")
    train.write_text(json.dumps([shared]))
    pool.write_text(json.dumps([shared, _row("LaSOT", "other-1", "other")]))
    outputs = [tmp_path / name for name in ("val.json", "test.json", "audit.json")]
    with pytest.raises(RuntimeError, match="leakage"):
        MODULE.build_posthoc_splits(train, pool, *outputs, val_size=1, seed=1)

    pool.write_text(json.dumps([_row("LaSOT", "a-1", "a"), _row("LaSOT", "b-1", "b")]))
    outputs[0].write_text("existing")
    with pytest.raises(FileExistsError, match="overwrite"):
        MODULE.build_posthoc_splits(train, pool, *outputs, val_size=1, seed=1)
