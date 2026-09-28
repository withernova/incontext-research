"""CPU-only checks for the shared Shell+Config analysis flow."""

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest


ROOT = Path(__file__).parents[1]


def load_tool(name, monkeypatch):
    package = ModuleType("iploc_szy")
    package.__path__ = []
    branching = ModuleType("iploc_szy.branching")
    branching.load_experiment_config = lambda *args, **kwargs: {}
    snapshot = ModuleType("iploc_szy.run_snapshot")
    snapshot.save_snapshot = lambda *args, **kwargs: None
    monkeypatch.setitem(sys.modules, "iploc_szy", package)
    monkeypatch.setitem(sys.modules, "iploc_szy.branching", branching)
    monkeypatch.setitem(sys.modules, "iploc_szy.run_snapshot", snapshot)
    spec = importlib.util.spec_from_file_location(f"e012_{name}", ROOT / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_common_launcher_supports_single_process_analysis(monkeypatch):
    launch = load_tool("launch", monkeypatch)
    command = launch.launch_command(
        {"launch": {"action": "analyze", "nproc_per_node": 1}}, "run.py"
    )
    assert command[-2:] == ["tools/analyze.py", "run.py"]
    with pytest.raises(ValueError, match="one process"):
        launch.launch_command(
            {"launch": {"action": "analyze", "nproc_per_node": 2}}, "run.py"
        )


def test_analysis_worker_writes_completed_status(monkeypatch, tmp_path):
    analyze = load_tool("analyze", monkeypatch)
    work_dir = tmp_path / "run"
    work_dir.mkdir()
    snapshot = work_dir / "logs" / "config_snapshots" / "analyze-unit"
    snapshot.mkdir(parents=True)
    config = {
        "work_dir": str(work_dir),
        "analysis": {"run_id": "R-unit", "entrypoint": "fake_worker:run"},
    }
    worker = ModuleType("fake_worker")
    worker.run = lambda *, config, snapshot_dir: {
        "received_work_dir": config["work_dir"], "snapshot": str(snapshot_dir)
    }
    monkeypatch.setitem(sys.modules, "fake_worker", worker)
    monkeypatch.setattr(analyze, "load_experiment_config", lambda *args: config)
    monkeypatch.setattr(analyze, "save_snapshot", lambda *args: snapshot)
    assert analyze.main(["config.py"]) == 0
    status = json.loads((work_dir / "status.json").read_text())
    assert status["schema"] == "iploc-szy.analysis-status/v1"
    assert status["status"] == "completed"
    assert status["run_id"] == "R-unit"
    assert status["result"]["received_work_dir"] == str(work_dir)


def test_analysis_worker_writes_failure_before_reraising(monkeypatch, tmp_path):
    analyze = load_tool("analyze", monkeypatch)
    work_dir = tmp_path / "run"
    work_dir.mkdir()
    snapshot = work_dir / "logs" / "config_snapshots" / "analyze-unit"
    snapshot.mkdir(parents=True)
    config = {
        "work_dir": str(work_dir),
        "analysis": {"run_id": "R-unit", "entrypoint": "fake_failure:run"},
    }
    worker = ModuleType("fake_failure")

    def fail(**kwargs):
        raise RuntimeError("expected unit failure")

    worker.run = fail
    monkeypatch.setitem(sys.modules, "fake_failure", worker)
    monkeypatch.setattr(analyze, "load_experiment_config", lambda *args: config)
    monkeypatch.setattr(analyze, "save_snapshot", lambda *args: snapshot)
    with pytest.raises(RuntimeError, match="expected unit failure"):
        analyze.main(["config.py"])
    status = json.loads((work_dir / "status.json").read_text())
    assert status["status"] == "failed"
    assert status["exception"] == "RuntimeError"
    assert "expected unit failure" in status["reason"]


def test_r004_config_is_explicitly_non_runnable_until_frozen():
    namespace = {}
    exec(
        (ROOT / "configs/head_screening/e012_contribution_calculation_check.py").read_text(),
        namespace,
    )
    assert namespace["launch"] == {"action": "analyze", "nproc_per_node": 1}
    assert namespace["analysis"]["run_id"] == "R-004-contribution-calculation-check"
    required = namespace["analysis"]["required_parameters"]
    assert required and all(value is None for value in required.values())


def test_r005_config_is_explicitly_non_runnable_until_frozen():
    namespace = {}
    exec(
        (ROOT / "configs/head_screening/e012_reference_target_grounded_screening.py").read_text(),
        namespace,
    )
    assert namespace["launch"] == {"action": "analyze", "nproc_per_node": 1}
    assert namespace["analysis"]["run_id"] == "R-005-reference-target-grounded-screening"
    required = namespace["analysis"]["required_parameters"]
    assert required and all(value is None for value in required.values())
