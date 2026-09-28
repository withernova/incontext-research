import json
from pathlib import Path

import pytest

from iploc_szy.engine.runner import SFTLoRARunner
from iploc_szy.run_management import (
    latest_index_rows,
    prepare_named_run,
    validate_prepared_run,
)


def _source_config(tmp_path: Path) -> Path:
    path = tmp_path / "config.py"
    path.write_text("value = 1\n", encoding="utf-8")
    return path


def _checkpoint(run_dir: Path, name: str = "checkpoint-1") -> Path:
    checkpoint = run_dir / "checkpoints" / name
    adapter = checkpoint / "adapter"
    adapter.mkdir(parents=True)
    (adapter / "adapter_model.safetensors").write_bytes(b"test")
    (checkpoint / "trainer_state.pt").write_bytes(b"test")
    return checkpoint


def _config(root: Path, **named_overrides):
    named = {
        "experiment_root": str(root),
        "experiment_id": "E-009",
        "run_name": "unit-branch",
        "run_kind": "branch-train-test",
        "mode": "new",
        "timestamp": "20260901T010203000000Z",
    }
    named.update(named_overrides)
    return {
        "named_run": named,
        "runner": {"initialize_from": None, "resume_from": None},
    }


def test_new_runs_are_isolated_and_indexed_with_named_lineage(tmp_path):
    source = _source_config(tmp_path)
    root = tmp_path / "experiments"
    parent_result = prepare_named_run(_config(root), source)
    parent_dir = Path(parent_result["work_dir"])
    parent_checkpoint = _checkpoint(parent_dir)

    child_config = _config(
        root,
        run_name="child",
        timestamp="20260901T020304000000Z",
        parent_checkpoint=str(parent_checkpoint),
    )
    child_config["runner"]["initialize_from"] = str(parent_checkpoint)
    child_result = prepare_named_run(child_config, source, ["loss.variant=test"])
    child_manifest = child_result["manifest"]

    assert child_result["work_dir"] != parent_result["work_dir"]
    assert Path(child_result["work_dir"]).parent == parent_dir / "branches"
    assert child_manifest["lineage"]["parent_run_id"] == parent_result["run_id"]
    assert child_manifest["lineage"]["root_run_id"] == parent_result["run_id"]
    assert child_manifest["lineage"]["generation"] == 1
    assert child_manifest["lineage"]["ancestors"] == [parent_result["run_id"]]
    assert child_manifest["source"]["cfg_options"] == ["loss.variant=test"]

    child_checkpoint = _checkpoint(Path(child_result["work_dir"]))
    grandchild_config = _config(
        root,
        run_name="grandchild",
        timestamp="20260901T030405000000Z",
        parent_checkpoint=str(child_checkpoint),
    )
    grandchild_config["runner"]["initialize_from"] = str(child_checkpoint)
    grandchild_result = prepare_named_run(grandchild_config, source)
    grandchild = grandchild_result["manifest"]
    assert Path(grandchild_result["work_dir"]).parent == parent_dir / "branches"
    assert grandchild["lineage"]["parent_run_id"] == child_result["run_id"]
    assert grandchild["lineage"]["root_run_id"] == parent_result["run_id"]
    assert grandchild["lineage"]["generation"] == 2

    rows = latest_index_rows(root / "E-009")
    assert set(rows) == {
        parent_result["run_id"],
        child_result["run_id"],
        grandchild_result["run_id"],
    }
    assert rows[child_result["run_id"]]["parent_run_id"] == parent_result["run_id"]


def test_legacy_parent_is_recorded_without_mutating_it(tmp_path):
    source = _source_config(tmp_path)
    root = tmp_path / "experiments"
    legacy_dir = root / "E-009" / "legacy-base"
    checkpoint = _checkpoint(legacy_dir)
    adapter_before = (checkpoint / "adapter" / "adapter_model.safetensors").read_bytes()
    state_before = (checkpoint / "trainer_state.pt").read_bytes()

    config = _config(root, parent_checkpoint=str(checkpoint))
    config["runner"]["initialize_from"] = str(checkpoint)
    result = prepare_named_run(config, source)

    assert result["manifest"]["lineage"]["parent_run_id"] == "legacy-base"
    assert result["manifest"]["lineage"]["parent_is_legacy"] is True
    assert result["manifest"]["lineage"]["generation"] == 1
    assert Path(result["work_dir"]).parent == legacy_dir / "branches"
    assert (checkpoint / "adapter" / "adapter_model.safetensors").read_bytes() == adapter_before
    assert (checkpoint / "trainer_state.pt").read_bytes() == state_before
    rows = latest_index_rows(root / "E-009")
    assert rows["legacy-base"]["run_kind"] == "legacy-root"
    assert rows[result["run_id"]]["parent_run_id"] == "legacy-base"


def test_resume_stays_in_same_named_run_and_validates_resolved_checkpoint(tmp_path):
    source = _source_config(tmp_path)
    root = tmp_path / "experiments"
    result = prepare_named_run(_config(root), source)
    run_dir = Path(result["work_dir"])
    checkpoint = _checkpoint(run_dir)

    resume_config = _config(
        root,
        mode="resume",
        run_dir=str(run_dir),
        resume_checkpoint=str(checkpoint),
    )
    resumed = prepare_named_run(resume_config, source)
    assert resumed["run_id"] == result["run_id"]
    assert resumed["work_dir"] == result["work_dir"]

    launched = {
        "work_dir": str(run_dir),
        "runner": {"resume_from": str(checkpoint)},
        "named_run": {
            "mode": "resume",
            "resolved_run_id": result["run_id"],
            "resolved_resume_checkpoint": str(checkpoint),
        },
    }
    assert validate_prepared_run(launched)["run_id"] == result["run_id"]
    launched["runner"]["resume_from"] = None
    with pytest.raises(RuntimeError, match="resume_from"):
        validate_prepared_run(launched)


def test_resume_from_another_run_requires_a_new_branch(tmp_path):
    source = _source_config(tmp_path)
    root = tmp_path / "experiments"
    first = prepare_named_run(_config(root), source)
    first_checkpoint = _checkpoint(Path(first["work_dir"]))
    second = prepare_named_run(
        _config(root, run_name="second", timestamp="20260901T030405000000Z"),
        source,
    )
    resume_config = _config(
        root,
        mode="resume",
        run_dir=second["work_dir"],
        resume_checkpoint=str(first_checkpoint),
    )
    with pytest.raises(ValueError, match="new branch"):
        prepare_named_run(resume_config, source)


def test_collision_and_required_parent_fail_closed(tmp_path):
    source = _source_config(tmp_path)
    root = tmp_path / "experiments"
    config = _config(root)
    prepare_named_run(config, source)
    with pytest.raises(FileExistsError):
        prepare_named_run(config, source)

    required = _config(
        root,
        timestamp="20260901T040506000000Z",
        require_parent_checkpoint=True,
    )
    with pytest.raises(ValueError, match="requires"):
        prepare_named_run(required, source)
    expected = root / "E-009" / "20260901T040506000000Z--unit-branch"
    assert not expected.exists()


def test_manifest_and_events_are_valid_json(tmp_path):
    source = _source_config(tmp_path)
    root = tmp_path / "experiments"
    result = prepare_named_run(_config(root), source)
    run_dir = Path(result["work_dir"])
    assert json.loads((run_dir / "run_manifest.json").read_text())["run_id"] == result[
        "run_id"
    ]
    events = (run_dir / "events.jsonl").read_text().splitlines()
    assert len(events) == 1
    assert json.loads(events[0])["event"] == "run_prepared"


def test_checkpoint_save_refuses_to_overwrite_existing_directory(tmp_path):
    runner = object.__new__(SFTLoRARunner)
    runner.work_dir = tmp_path
    runner.step = 7
    existing = tmp_path / "checkpoints" / "samples_00000064_step_000007"
    existing.mkdir(parents=True)
    sentinel = existing / "keep.txt"
    sentinel.write_text("original", encoding="utf-8")

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        runner._save_checkpoint(64)
    assert sentinel.read_text(encoding="utf-8") == "original"
