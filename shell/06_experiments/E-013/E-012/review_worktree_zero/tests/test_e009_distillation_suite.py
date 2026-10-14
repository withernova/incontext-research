from pathlib import Path

from iploc_szy.branching import load_experiment_config


PROJECT = Path(__file__).resolve().parents[1]
CONFIG = PROJECT / "configs/sft/e009_qwen3vl8b_reference_query_ensemble_distill.py"
LAUNCHER = PROJECT / "tools/run/run_e009_reference_query_ensemble_distill.sh"
DYNAMIC_LAUNCHER = PROJECT / "tools/run/run_e009_dynamic_reference_query_distill.sh"


def test_e009_config_freezes_heads_coefficient_seed_and_training_manifest():
    config = load_experiment_config(CONFIG)
    auxiliary = config["runner"]["auxiliary_loss"]
    assert auxiliary["teacher_heads"] == ("L20H15", "L20H20", "L14H23")
    assert auxiliary["student_heads"] == (
        "L21H10", "L17H04", "L17H07", "L24H16", "L18H15"
    )
    assert auxiliary["coefficient"] == 0.1
    assert config["runner"]["seed"] == 20260901
    assert config["runner"]["optimizer"]["lr"] == 1e-5
    ann_file = config["train_dataloader"]["dataset"]["ann_file"]
    assert ann_file.endswith("train_only_1shot_focus_valid10522.json")
    assert "test600" not in repr(config)
    assert config["model"]["attn_implementation"] == "sdpa"
    assert config["model"]["gradient_checkpointing"] is True
    assert config["model"]["gradient_checkpointing_kwargs"] == {
        "use_reentrant": False
    }
    teacher = config["teacher_precompute"]
    assert teacher["teacher_heads"] == ("L20H15", "L20H20", "L14H23")
    assert teacher["source_manifest"] == ann_file
    assert teacher["output_dir"].endswith("teacher_step1729")


def test_four_arm_launcher_is_thin_and_explicit():
    text = LAUNCHER.read_text(encoding="utf-8")
    assert "for treatment in baseline correct cyclic_roll gt_mask" in text
    assert "precompute_e009_reference_teacher.py" in text
    assert "tools/run_branch.py" in text
    assert 'tee -a "$PRECOMPUTE_LOG"' in text
    assert "incomplete teacher directory exists" not in text
    assert "test600" not in text



def test_dynamic_launcher_runs_only_online_stop_gradient_teacher():
    text = DYNAMIC_LAUNCHER.read_text(encoding="utf-8")
    assert "treatment=dynamic_teacher" in text
    assert "teacher_manifest=None" in text
    assert "runtime.runner.optimizer.lr=4e-5" in text
    assert "precompute_e009_reference_teacher.py" not in text
    assert "for treatment in" not in text
    assert "test600" not in text
