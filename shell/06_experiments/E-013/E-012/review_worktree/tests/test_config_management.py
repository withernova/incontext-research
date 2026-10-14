"""Configuration provenance and launcher regression tests without model loading."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from iploc_szy.config import Config
from iploc_szy.branching import load_experiment_config
from iploc_szy.run_snapshot import save_snapshot, save_prompt_example
from iploc_szy.prompting.messages import qwen3_grounding_messages, QWEN3_GROUNDING_PROMPT


def module(name):
    spec = importlib.util.spec_from_file_location(name, Path("tools") / f"{name}.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_branch_snapshot_preserves_sources_and_resume(tmp_path):
    (tmp_path / "base.py").write_text("runner=dict(max_steps=1)\n")
    (tmp_path / "parent.py").write_text("_base_='base.py'\n")
    path = tmp_path / "branch.py"
    path.write_text("branch=dict(parent_config='parent.py', action='train')\n"
                    "runtime=dict(runner=dict(max_steps=2))\n")
    cfg = load_experiment_config(path, ["runtime.runner.max_steps=3"])
    cfg["work_dir"] = str(tmp_path / "run")
    first = save_snapshot(cfg, path, "train")
    (tmp_path / "base.py").write_text("runner=dict(max_steps=999)\n")
    second = save_snapshot(cfg, path, "train")
    assert first != second
    assert json.loads((first / "resolved.json").read_text())["runner"]["max_steps"] == 3
    assert len(json.loads((first / "provenance.json").read_text())["source_configs"]) == 3
    assert any("max_steps=1" in p.read_text() for p in second.glob("*base.py"))
    save_prompt_example(first, {"id": "sample", "messages": [{"role": "user", "content": "custom"}]})
    assert json.loads((first / "prompt_example.json").read_text())["messages"][0]["content"] == "custom"


def test_prompt_default_and_override():
    default = qwen3_grounding_messages([], "image.jpg", "cat")
    explicit = qwen3_grounding_messages([], "image.jpg", "cat", prompt=QWEN3_GROUNDING_PROMPT)
    custom = qwen3_grounding_messages([], "image.jpg", "cat", prompt="Custom instruction")
    assert default == explicit
    assert custom[0]["content"][0]["text"] == "Custom instruction"


def test_launcher_reads_config_and_rejects_duplicate_inference():
    launch = module("launch")
    command = launch.launch_command({"launch": {"action": "train", "nproc_per_node": 2}}, "train.py")
    assert "--nproc_per_node=2" in command
    with pytest.raises(ValueError, match="one process"):
        launch.launch_command({"launch": {"action": "infer", "nproc_per_node": 4}}, "infer.py")


def test_infer_uses_config_and_snapshots_cli_override(tmp_path, monkeypatch):
    infer = module("infer")
    path = tmp_path / "config.py"
    path.write_text(f"work_dir={str(tmp_path / 'output')!r}\n"
                    "model=dict(type='fake')\n"
                    "test_dataloader=dict(dataset=dict(type='fake'))\n"
                    "evaluation=dict(limit=None,max_new_tokens=77)\n")
    dataset = [{"id": str(i), "messages": [], "answer": "box"} for i in range(3)]
    seen = []
    monkeypatch.setattr(infer, "MODELS", SimpleNamespace(build=lambda cfg: object()))
    monkeypatch.setattr(infer, "DATASETS", SimpleNamespace(build=lambda cfg: dataset))
    evaluator = SimpleNamespace(process=lambda *args: None, evaluate=lambda: {})
    monkeypatch.setattr(infer, "EVALUATORS", SimpleNamespace(build=lambda cfg: evaluator))
    monkeypatch.setattr(infer, "generate", lambda model, sample, tokens: seen.append(tokens) or "box")
    assert infer.main([str(path)]) == 0
    assert seen == [77, 77, 77]
    seen.clear()
    assert infer.main([str(path), "--limit", "1", "--max-new-tokens", "12"]) == 0
    assert seen == [12]
    resolved = [json.loads(p.read_text()) for p in (tmp_path / "output").glob("logs/config_snapshots/*/resolved.json")]
    assert sorted(row["evaluation"]["max_new_tokens"] for row in resolved) == [12, 77]


def test_manifest_list_is_combined_and_keeps_dataset_labels(tmp_path):
    from iploc_szy.datasets.iploc import IPLocManifestDataset
    from PIL import Image

    image = tmp_path / "image.png"
    Image.new("RGB", (10, 10), "white").save(image)
    paths = []
    for index, name in enumerate(("lasot", "tao", "got10k")):
        row = {"element": "cat", "image_path": [str(image), str(image)],
               "bbox": [[0, 0, 5, 5], [0, 0, 5, 5]],
               "role": ["reference", "positive-image"], "dataset": name}
        path = tmp_path / f"{index}.json"
        path.write_text(json.dumps([row]))
        paths.append(str(path))
    dataset = IPLocManifestDataset(paths)
    assert len(dataset) == 3
    assert [sample["raw"]["dataset"] for sample in dataset] == ["lasot", "tao", "got10k"]


def test_manifest_dataset_filter_and_missing_name(tmp_path):
    from iploc_szy.datasets.iploc import IPLocManifestDataset
    from PIL import Image
    image = tmp_path / "filter-image.png"
    Image.new("RGB", (10, 10), "white").save(image)
    rows = []
    for name in ("LaSOT", "TAO", "GOT10k"):
        rows.append({"element": "cat", "image_path": [str(image), str(image)],
                     "bbox": [[0, 0, 5, 5], [0, 0, 5, 5]],
                     "role": ["reference", "positive-image"], "dataset": name})
    manifest = tmp_path / "combined.json"
    manifest.write_text(json.dumps(rows))
    selected = IPLocManifestDataset(str(manifest), dataset_names=("TAO",))
    assert len(selected) == 1
    assert selected[0]["raw"]["dataset"] == "TAO"
    with pytest.raises(ValueError, match="not present"):
        IPLocManifestDataset(str(manifest), dataset_names=("unknown",))


def test_native_and_adapter_share_frozen_evaluation_scope():
    native = load_experiment_config("configs/eval/e011_qwen3vl8b_native_iploc.py")
    adapter = load_experiment_config("configs/sft/e011_qwen3vl8b_grounding_eval_branch.py")
    for key in ("ann_file", "dataset_names", "prompt_protocol", "prompt_version", "prompt_text"):
        assert native["test_dataloader"]["dataset"][key] == adapter["test_dataloader"]["dataset"][key]
    assert native["evaluation"]["datasets"] == ("LaSOT", "GOT10k", "TAO")
    assert native["FROZEN_EVAL_SHA256"] == "48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b"


def test_manifest_hash_is_enforced(tmp_path):
    import hashlib
    from iploc_szy.datasets.iploc import IPLocManifestDataset
    from PIL import Image
    image = tmp_path / "hash-image.png"
    Image.new("RGB", (10, 10), "white").save(image)
    manifest = tmp_path / "hash.json"
    manifest.write_text(json.dumps([{
        "element": "cat", "image_path": [str(image), str(image)],
        "bbox": [[0, 0, 5, 5], [0, 0, 5, 5]],
        "role": ["reference", "positive-image"], "dataset": "LaSOT"
    }]))
    digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
    assert len(IPLocManifestDataset(str(manifest), ann_file_sha256=digest)) == 1
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        IPLocManifestDataset(str(manifest), ann_file_sha256="0" * 64)
