"""Four-GPU 1-shot NF4 QLoRA branch with isolated named-run outputs."""

_base_ = "qwen3vl_8b_lora_focus_1shot_ddp4_4bit.py"

# Keep experimental identity separate from optimization settings.  Every
# invocation in mode="new" allocates a timestamped child below the root run's
# branches/ directory and restores from parent_checkpoint.
named_run = dict(
    experiment_root="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments",
    experiment_id="E-009",
    run_name="focus-qwen3vl8b-1shot-nf4-ddp4-branch",
    run_kind="branch-train",
    mode="new",
    timestamp="auto",
    parent_checkpoint=None,
    require_parent_checkpoint=True,
    run_dir=None,
    resume_checkpoint=None,
    tags=["1shot", "nf4", "ddp4"],
    notes="Named training branch from a resumable parent checkpoint.",
)
