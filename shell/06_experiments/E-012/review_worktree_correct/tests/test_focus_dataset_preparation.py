import importlib.util
import json
from pathlib import Path

TOOL = Path(__file__).parents[1] / "tools" / "prepare_focus_datasets.py"
SPEC = importlib.util.spec_from_file_location("prepare_focus_datasets", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_focus_indices_span_sequence_and_reserve_final_query() -> None:
    supports, query = MODULE._focus_indices(11, 4)
    assert supports == [0, 3, 6, 9]
    assert query == 10


def test_box_conversion() -> None:
    assert MODULE._xywh_to_xyxy([10, 20, 30, 40]) == [10, 20, 40, 60]


def test_tao_uses_most_frequent_track(tmp_path: Path) -> None:
    root = tmp_path / "prepared"
    annotation_dir = root / "TAO/annotations"
    annotation_dir.mkdir(parents=True)
    images, annotations = [], []
    for index in range(6):
        image_id = index + 1
        file_name = f"validation/source/video/frame{index:04d}.jpg"
        path = root / "TAO/frames" / file_name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"image")
        images.append({"id": image_id, "video_id": 7, "file_name": file_name, "frame_index": index})
        annotations.append({"image_id": image_id, "track_id": 11, "bbox": [index, 2, 3, 4]})
        if index < 2:
            annotations.append({"image_id": image_id, "track_id": 12, "bbox": [0, 0, 1, 1]})
    (annotation_dir / "validation.json").write_text(json.dumps({"videos": [{"id": 7, "name": "validation/source/video"}], "images": images, "annotations": annotations}))
    rows = list(MODULE._tao_records(root / "TAO", "validation", shots=4))
    assert len(rows) == 1
    assert rows[0]["metadata"]["track_id"] == 11
    assert rows[0]["frame_indices"] == [0, 1, 3, 4, 5]
    assert rows[0]["bbox"][-1] == [5.0, 2.0, 8.0, 6.0]
