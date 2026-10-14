import importlib.util
import json
from pathlib import Path

import pytest
from PIL import Image

TOOL = Path(__file__).parents[1] / "tools" / "filter_e009_valid_bbox_manifest.py"
SPEC = importlib.util.spec_from_file_location("filter_e009_valid_bbox_manifest", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def row(root, sequence, reference_box, target_box):
    return {
        "dataset": "LaSOT",
        "sequence": sequence,
        "image_path": [
            str(root / f"{sequence}-ref.jpg"),
            str(root / f"{sequence}-query.jpg"),
        ],
        "bbox": [reference_box, target_box],
        "role": ["reference", "positive-image"],
    }


def images(root, *sequences):
    for sequence in sequences:
        Image.new("RGB", (10, 10)).save(root / f"{sequence}-ref.jpg")
        Image.new("RGB", (10, 10)).save(root / f"{sequence}-query.jpg")


def test_filters_invalid_boxes_and_preserves_order(tmp_path):
    sequences = ("valid-1", "bad-target", "bad-reference", "off-image", "valid-2")
    images(tmp_path, *sequences)
    source = tmp_path / "source.json"
    output = tmp_path / "valid.json"
    audit_path = tmp_path / "valid.audit.json"
    source.write_text(
        json.dumps(
            [
                row(tmp_path, "valid-1", [1, 2, 3, 4], [5, 6, 7, 8]),
                row(tmp_path, "bad-target", [1, 2, 3, 4], [0, 0, 0, 0]),
                row(tmp_path, "bad-reference", [1, 1, 1, 1], [5, 6, 7, 8]),
                row(tmp_path, "off-image", [1, 2, 3, 4], [11, 2, 12, 4]),
                row(tmp_path, "valid-2", [2, 3, 4, 5], [6, 7, 8, 9]),
            ]
        ),
        encoding="utf-8",
    )
    audit = MODULE.filter_manifest(
        source, output, audit_path, expected_output_count=2
    )
    kept = json.loads(output.read_text(encoding="utf-8"))
    assert [item["sequence"] for item in kept] == ["valid-1", "valid-2"]
    assert [item["source_index"] for item in audit["dropped"]] == [1, 2, 3]
    assert (
        audit["dropped"][2]["invalid_boxes"][0]["reason"]
        == "zero_intersection_with_normalized_image_plane"
    )
    assert audit["output"]["sha256"] == MODULE.sha256_file(output)
    assert json.loads(audit_path.read_text())["dropped_count"] == 3


def test_count_and_overwrite_gates_are_fail_closed(tmp_path):
    images(tmp_path, "valid")
    source = tmp_path / "source.json"
    source.write_text(
        json.dumps([row(tmp_path, "valid", [1, 2, 3, 4], [5, 6, 7, 8])]),
        encoding="utf-8",
    )
    output = tmp_path / "valid.json"
    audit = tmp_path / "audit.json"
    with pytest.raises(ValueError, match="count mismatch"):
        MODULE.filter_manifest(source, output, audit, expected_output_count=2)
    output.write_text("existing", encoding="utf-8")
    with pytest.raises(FileExistsError, match="overwrite"):
        MODULE.filter_manifest(source, output, audit)
