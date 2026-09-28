from pathlib import Path

import pytest

from iploc_szy.branching import load_experiment_config
from iploc_szy.checkpointing import validate_adapter_checkpoint, validate_checkpoint
from iploc_szy.run_management import prepare_named_run


def _final_work_dir(tmp_path: Path) -> Path:
    work_dir = tmp_path / "experiments" / "E-012" / "correct" / "training"
    adapter = work_dir / "adapter"
    adapter.mkdir(parents=True)
    (adapter / "adapter_model.safetensors").write_bytes(b"adapter")
    (work_dir / "metrics.json").write_text('{"status":"passed"}\n')
    return work_dir


def _config(tmp_path: Path, parent: Path, action: str):
    return {
        "branch": {"action": action},
        "named_run": {
            "experiment_root": str(tmp_path / "experiments"),
            "experiment_id": "E-012",
            "run_name": f"final-{action}",
            "run_kind": f"branch-{action}",
            "mode": "new",
            "timestamp": f"20260914T01020{3 if action == 'evaluate' else 4}000000Z",
            "parent_checkpoint": str(parent),
            "require_parent_checkpoint": True,
        },
        "runner": {"initialize_from": None, "resume_from": None},
    }


def test_adapter_only_validation_is_read_only_and_training_stays_strict(tmp_path: Path):
    final = _final_work_dir(tmp_path)
    assert validate_adapter_checkpoint(final) == final.resolve()
    with pytest.raises(FileNotFoundError, match="trainer_state"):
        validate_checkpoint(final)


def test_named_evaluation_accepts_completed_final_adapter_work_dir(tmp_path: Path):
    final = _final_work_dir(tmp_path)
    source = tmp_path / "eval.py"
    source.write_text("value = 1\n", encoding="utf-8")
    result = prepare_named_run(_config(tmp_path, final, "evaluate"), source)
    assert Path(result["work_dir"]).parent == final / "branches"
    assert result["resume_checkpoint"] == str(final.resolve())
    assert result["manifest"]["action"] == "evaluate"


def test_named_training_rejects_adapter_only_parent(tmp_path: Path):
    final = _final_work_dir(tmp_path)
    with pytest.raises(FileNotFoundError, match="trainer_state"):
        prepare_named_run(_config(tmp_path, final, "train"), tmp_path / "train.py")


def test_e012_final_eval_config_resolves_expected_contract():
    root = Path(__file__).resolve().parents[1]
    config = load_experiment_config(
        root / "configs/sft/e012_ref10_query5_correct_final_eval.py"
    )
    assert config["branch"]["action"] == "evaluate"
    assert config["branch"]["resolved_source"] == "e012_correct_final"
    assert config["named_run"]["experiment_id"] == "E-012"
    assert config["named_run"]["parent_checkpoint"].endswith(
        "ref10-query5-correct-step247-3ep-v1/training"
    )
    assert config["evaluation"]["dataloader"] == "test_dataloader"
    assert config["evaluation"]["limit"] is None
