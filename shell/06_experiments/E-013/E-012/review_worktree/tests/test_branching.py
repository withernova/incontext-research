from pathlib import Path

import pytest

from iploc_szy.branching import branch_summary, load_experiment_config
from iploc_szy.run_management import prepare_named_run, validate_prepared_run


def _files(tmp_path: Path):
    parent = tmp_path / "parent.py"
    parent.write_text(
        """
model = dict(type="FakeModel", width=8)
work_dir = "legacy"
train_dataloader = dict(batch_size=1, dataset=dict(type="FakeDataset"))
runner = dict(
    max_epochs=12,
    resume_from=None,
    optimizer=dict(lr=2e-4),
    hooks=[dict(type="LoggerHook")],
)
""",
        encoding="utf-8",
    )
    branch = tmp_path / "branch.py"
    branch.write_text(
        """
branch = dict(
    parent_config="parent.py",
    action="train",
    nproc_per_node=4,
    periodic_head_screening=False,
)
named_run = dict(
    mode="new",
    run_name="unit-{action}",
    run_kind="branch-{action}",
    parent_checkpoint="/checkpoint",
)
runtime = dict(runner=dict(max_epochs=2))
evaluation = dict(dataloader="train_dataloader", limit=10)
head_screening = dict(
    probe=dict(type="Probe"),
    finder=dict(type="Finder"),
)
""",
        encoding="utf-8",
    )
    return parent, branch


def test_branch_composes_parent_runtime_and_cli_overrides(tmp_path):
    parent, branch = _files(tmp_path)
    config = load_experiment_config(
        branch,
        [
            "branch.action=evaluate",
            "branch.nproc_per_node=2",
            "runtime.runner.optimizer.lr=1e-5",
            "evaluation.limit=7",
        ],
    )
    assert config["model"]["width"] == 8
    assert config["runner"]["max_epochs"] == 2
    assert config["runner"]["optimizer"]["lr"] == 1e-5
    assert config["runner"]["resume_from"] is None
    assert config["evaluation"]["limit"] == 7
    assert config["named_run"]["run_name"] == "unit-evaluate"
    assert config["named_run"]["run_kind"] == "branch-evaluate"
    assert config["branch"]["resolved_parent_config"] == str(parent.resolve())
    assert branch_summary(config)["nproc_per_node"] == 2


def test_training_initializes_from_parent_and_can_inject_periodic_screening(tmp_path):
    _, branch = _files(tmp_path)
    config = load_experiment_config(
        branch,
        ["branch.periodic_head_screening=True"],
    )
    assert config["runner"]["initialize_from"] == "/checkpoint"
    assert config["runner"]["resume_from"] is None
    types = [hook["type"] for hook in config["runner"]["hooks"]]
    assert types == ["LoggerHook", "HeadScreeningHook"]
    assert config["runner"]["hooks"][-1]["probe"] == {"type": "Probe"}


def test_named_source_profiles_switch_between_base_model_and_checkpoints(tmp_path):
    _, branch = _files(tmp_path)
    with branch.open("a", encoding="utf-8") as handle:
        handle.write(
            """
branch.update(
    source="native",
    source_profiles=dict(
        native=dict(kind="base_model", experiment_id="E-011"),
        e009=dict(
            kind="checkpoint",
            experiment_id="E-009",
            parent_checkpoint="/e009/checkpoint",
        ),
    ),
)
"""
        )

    native = load_experiment_config(branch)
    assert native["named_run"]["experiment_id"] == "E-011"
    assert native["named_run"]["parent_checkpoint"] is None
    assert native["named_run"]["require_parent_checkpoint"] is False
    assert native["runner"]["initialize_from"] is None
    assert branch_summary(native)["source_kind"] == "base_model"

    e009 = load_experiment_config(branch, ["branch.source=e009"])
    assert e009["named_run"]["experiment_id"] == "E-009"
    assert e009["named_run"]["parent_checkpoint"] == "/e009/checkpoint"
    assert e009["named_run"]["require_parent_checkpoint"] is True
    assert e009["runner"]["initialize_from"] == "/e009/checkpoint"
    assert branch_summary(e009)["source"] == "e009"


def test_source_profile_validation_fails_closed(tmp_path):
    _, branch = _files(tmp_path)
    with branch.open("a", encoding="utf-8") as handle:
        handle.write(
            "\nbranch.update(source='missing', source_profiles=dict(native=dict(kind='base_model')))\n"
        )
    with pytest.raises(ValueError, match="unknown branch.source"):
        load_experiment_config(branch)


def test_resume_uses_same_run_checkpoint_for_training(tmp_path):
    _, branch = _files(tmp_path)
    config = load_experiment_config(
        branch,
        [
            "named_run.mode=resume",
            "named_run.parent_checkpoint=None",
            "named_run.resume_checkpoint=/same-run/checkpoint",
        ],
    )
    assert config["runner"]["initialize_from"] is None
    assert config["runner"]["resume_from"] == "/same-run/checkpoint"


def test_nontraining_resume_and_unknown_action_fail_closed(tmp_path):
    _, branch = _files(tmp_path)
    with pytest.raises(ValueError, match="must use named_run.mode='new'"):
        load_experiment_config(
            branch,
            ["branch.action=head_screen", "named_run.mode=resume"],
        )
    with pytest.raises(ValueError, match="branch.action"):
        load_experiment_config(branch, ["branch.action=unknown"])


def test_normal_config_remains_backward_compatible(tmp_path):
    parent, _ = _files(tmp_path)
    config = load_experiment_config(parent, ["runner.max_epochs=3"])
    assert config["runner"]["max_epochs"] == 3
    assert "branch" not in config


def test_evaluation_branch_prepare_and_worker_validation_agree(tmp_path):
    _, branch = _files(tmp_path)
    checkpoint = tmp_path / "experiments" / "E-009" / "legacy" / "checkpoints" / "c1"
    (checkpoint / "adapter").mkdir(parents=True)
    (checkpoint / "adapter" / "adapter_model.safetensors").write_bytes(b"test")
    (checkpoint / "trainer_state.pt").write_bytes(b"test")
    options = [
        "branch.action=evaluate",
        f"named_run.experiment_root={tmp_path / 'experiments'}",
        "named_run.experiment_id=E-009",
        "named_run.timestamp=20260901T010203000000Z",
        f"named_run.parent_checkpoint={checkpoint}",
        "named_run.require_parent_checkpoint=True",
    ]
    config = load_experiment_config(branch, options)
    prepared = prepare_named_run(config, branch, options)
    launched = load_experiment_config(
        branch,
        [
            *options,
            f"runtime.work_dir={prepared['work_dir']}",
            f"named_run.resolved_run_id={prepared['run_id']}",
            f"named_run.resolved_resume_checkpoint={checkpoint}",
        ],
    )
    manifest = validate_prepared_run(launched)
    assert manifest["action"] == "evaluate"
    assert manifest["source"]["parent_config_path"].endswith("parent.py")
    assert manifest["artifacts"]["log"].endswith("evaluate.log")
