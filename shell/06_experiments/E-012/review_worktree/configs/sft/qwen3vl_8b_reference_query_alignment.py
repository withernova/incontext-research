"""E009 Reference Top-3 to Query Top-5 fixed-teacher distillation suite."""

branch = dict(
    parent_config="qwen3vl_8b_lora_focus_1shot_ddp4_4bit.py",
    action="train",
    nproc_per_node=4,
    periodic_head_screening=False,
)

parent_checkpoint = (
    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
    "E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/checkpoints/"
    "samples_00110607_step_001729"
)
teacher_root = (
    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
    "E009-R-008-reference-top3-query-top5-ensemble-distill/teacher_step1729"
)
train_manifest = (
    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
    "E009-real-focus-data/manifests/train_only_1shot_focus_valid10522.json"
)

named_run = dict(
    experiment_root="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments",
    experiment_id="E-009",
    run_name="E009-R-008-reference-top3-query-top5-ensemble-distill-baseline",
    run_kind="reference-query-attention-distillation",
    mode="new",
    timestamp="auto",
    parent_checkpoint=parent_checkpoint,
    require_parent_checkpoint=True,
    run_dir=None,
    resume_checkpoint=None,
    tags=["1shot", "nf4", "ddp4", "attention-distillation", "fixed-teacher"],
    notes=(
        "Four-arm R008 suite; launch overrides only treatment and run_name. "
        "Held-out test manifests are intentionally absent from this training config."
    ),
)

runtime = dict(
    model=dict(
        # Selected-attention distillation reuses trainable LoRA Q/K projections
        # outside the checkpointed decoder forward. Reentrant checkpointing makes
        # DDP fire the same parameter-ready hook twice; non-reentrant preserves
        # activation checkpointing without that unsupported backward topology.
        gradient_checkpointing_kwargs=dict(use_reentrant=False),
    ),
    train_dataloader=dict(
        batch_size=1,
        dataset=dict(ann_file=train_manifest),
    ),
    runner=dict(
        seed=20260901,
        max_epochs=3,
        optimizer=dict(lr=1e-4),
        auxiliary_loss=dict(
            type="ReferenceQueryAttentionDistillation",
            treatment="baseline",
            teacher_manifest=f"{teacher_root}/manifest.json",
            teacher_heads=("L20H15", "L20H20", "L14H23"),
            student_heads=("L21H10", "L17H04", "L17H07", "L24H16", "L18H15"),
            coefficient=0.1,
            cyclic_roll_seed=20260901,
        ),
    ),
)

teacher_precompute = dict(
    output_dir=teacher_root,
    checkpoint=parent_checkpoint,
    source_manifest=train_manifest,
    teacher_heads=("L20H15", "L20H20", "L14H23"),
)
