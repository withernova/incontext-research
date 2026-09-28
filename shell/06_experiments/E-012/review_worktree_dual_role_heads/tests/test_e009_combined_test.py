import importlib.util
import json
from pathlib import Path

import pytest

TOOL = Path(__file__).parents[1] / "tools" / "build_e009_combined_test.py"
SPEC = importlib.util.spec_from_file_location("build_e009_combined_test", TOOL)
MODULE = importlib.util.module_from_spec(SPEC); assert SPEC.loader is not None; SPEC.loader.exec_module(MODULE)


def _got(root):
    seq = root / "val" / "GOT-10k_Val_000001"; seq.mkdir(parents=True)
    (seq / "groundtruth.txt").write_text("0,0,10,10\n1,1,10,10\n2,2,10,10\n")
    (seq / "absence.label").write_text("0\n1\n0\n"); (seq / "cover.label").write_text("7\n0\n7\n")
    (seq / "meta_info.ini").write_text("[METAINFO]\nobject_class: object\n")
    for i in range(1, 4): (seq / f"{i:08d}.jpg").write_bytes(b"image")


def _tao(root):
    frames = root / "frames" / "val" / "video"; frames.mkdir(parents=True)
    for name in ("frame0001.jpg", "frame0003.jpg"): (frames / name).write_bytes(b"image")
    payload = {"videos": [{"id": 1, "name": "val/video"}], "images": [{"id": 1, "video_id": 1, "frame_index": 0, "file_name": "val/video/frame0001.jpg"}, {"id": 2, "video_id": 1, "frame_index": 2, "file_name": "val/video/frame0003.jpg"}], "annotations": [{"image_id": 1, "track_id": 5, "bbox": [0, 0, 10, 10]}, {"image_id": 2, "track_id": 5, "bbox": [1, 1, 10, 10]}]}
    (root / "annotations").mkdir(); (root / "annotations" / "validation.json").write_text(json.dumps(payload))


def _row(dataset, sequence, prefix):
    return {"dataset": dataset, "sequence": sequence, "element": "target-object", "image_path": [prefix + "a.jpg", prefix + "b.jpg"], "bbox": [[0,0,1,1],[0,0,1,1]], "role": ["reference", "positive-image"]}


def test_builds_components_combined_and_audit(tmp_path):
    got, tao = tmp_path / "got", tmp_path / "tao"; _got(got); _tao(tao)
    train, lasot = tmp_path / "train.json", tmp_path / "lasot.json"
    train.write_text(json.dumps([_row("LaSOT", "train-1", "train")]))
    lasot.write_text(json.dumps([_row("LaSOT", "test-1", "test")]))
    outputs = [tmp_path / name for name in ("got.json", "tao.json", "combined.json", "audit.json")]
    audit = MODULE.build_combined_test(train, lasot, got, tao, *outputs)
    assert audit["counts"] == {"LaSOT": 1, "GOT10k": 1, "TAO": 1, "combined": 3}
    assert len(json.loads(outputs[2].read_text())) == 3
    assert json.loads(outputs[0].read_text())[0]["frame_indices"] == [0, 2]
    assert all(value == 0 for group in audit["overlap"].values() for pair in group.values() for value in pair.values())


def test_refuses_overwrite(tmp_path):
    output = tmp_path / "got.json"; output.write_text("existing")
    with pytest.raises(FileExistsError, match="overwrite"):
        MODULE.build_combined_test(tmp_path/"train", tmp_path/"lasot", tmp_path/"got", tmp_path/"tao", output, tmp_path/"tao.json", tmp_path/"all.json", tmp_path/"audit.json")
