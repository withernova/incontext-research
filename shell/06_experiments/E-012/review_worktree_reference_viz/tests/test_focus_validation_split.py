import importlib.util
import json
from pathlib import Path

import pytest

TOOL = Path(__file__).parents[1] / "tools" / "build_focus_val_manifest.py"
SPEC = importlib.util.spec_from_file_location("build_focus_val_manifest", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _sequence(root: Path, category: str, number: int) -> None:
    sequence = root / category / f"{category}-{number}"
    image_dir = sequence / "img"
    image_dir.mkdir(parents=True)
    (sequence / "groundtruth.txt").write_text("0,0,10,10\n1,1,10,10\n")
    (image_dir / "00000001.jpg").write_bytes(b"frame")
    (image_dir / "00000002.jpg").write_bytes(b"frame")


def test_builds_category_and_sequence_heldout_manifest(tmp_path):
    root = tmp_path / "LaSOT"
    for category in ("a", "b", "c", "d"):
        _sequence(root, category, 1)
    categories = tmp_path / "train_categories.txt"
    categories.write_text("a\nb\n")
    train = tmp_path / "train.json"
    train.write_text(
        json.dumps(
            [
                {"dataset": "LaSOT", "sequence": "a-1"},
                {"dataset": "LaSOT", "sequence": "b-1"},
            ]
        )
    )
    output = tmp_path / "val.json"
    audit_output = tmp_path / "val.audit.json"
    audit = MODULE.build_validation_manifest(
        root,
        train,
        categories,
        output,
        audit_output,
        expected_categories=4,
        expected_train_categories=2,
        expected_sequences_per_category=1,
    )

    rows = json.loads(output.read_text())
    assert [row["sequence"] for row in rows] == ["c-1", "d-1"]
    assert all(row["metadata"]["split"] == "validation" for row in rows)
    assert all(row["frame_indices"] == [0, 1] for row in rows)
    assert audit["counts"]["sequence_overlap"] == 0
    assert audit["validation_manifest_sha256"]


def test_refuses_category_mismatch_and_overwrite(tmp_path):
    root = tmp_path / "LaSOT"
    for category in ("a", "b"):
        _sequence(root, category, 1)
    categories = tmp_path / "train_categories.txt"
    categories.write_text("a\n")
    train = tmp_path / "train.json"
    train.write_text(json.dumps([{"dataset": "LaSOT", "sequence": "b-1"}]))
    output = tmp_path / "val.json"
    audit = tmp_path / "audit.json"
    with pytest.raises(ValueError, match="do not match"):
        MODULE.build_validation_manifest(
            root,
            train,
            categories,
            output,
            audit,
            expected_categories=2,
            expected_train_categories=1,
            expected_sequences_per_category=1,
        )

    train.write_text(json.dumps([{"dataset": "LaSOT", "sequence": "a-1"}]))
    output.write_text("existing")
    with pytest.raises(FileExistsError, match="overwrite"):
        MODULE.build_validation_manifest(
            root,
            train,
            categories,
            output,
            audit,
            expected_categories=2,
            expected_train_categories=1,
            expected_sequences_per_category=1,
        )
