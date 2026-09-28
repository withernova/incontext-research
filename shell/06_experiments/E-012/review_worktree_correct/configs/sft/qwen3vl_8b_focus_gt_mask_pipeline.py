"""FOCUS 1-shot SFT: warm-up -> adaptive GT-mask -> fixed-head GT-mask.

start_step counts completed optimizer updates, not microbatches or a parent
checkpoint's number. These are exploratory intervention settings, not validated
optimal phase boundaries. All head selection uses this run's training manifest.
"""

_base_ = "qwen3vl_8b_lora_focus_1shot_ddp4_4bit.py"

named_run = dict(
    experiment_root="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments",
    experiment_id="E-011",
    run_name="focus-early-gt-mask-pipeline",
    run_kind="staged-gt-mask-sft",
    mode="new",
    timestamp="auto",
    parent_checkpoint=None,
    require_parent_checkpoint=False,
    run_dir=None,
    resume_checkpoint=None,
    tags=["focus", "1shot", "gt-mask", "pipeline", "ddp4"],
    notes="从原始模型开始；只在训练集重筛 heads；沿用 FOCUS prompt。",
)

model = dict(gradient_checkpointing_kwargs=dict(use_reentrant=False))
train_dataloader = dict(
    dataset=dict(
        ann_file=(
            "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
            "E009-real-focus-data/manifests/train_only_1shot_focus_valid10522.json"
        ),
        prompt_protocol="focus",
    ),
)

_gt_mask = dict(
    type="ReferenceQueryAttentionDistillation",
    treatment="gt_mask",
    teacher_manifest=None,
    teacher_heads=(),
    student_heads=(),  # Filled from the current model's train-only screening.
)

runner = dict(
    max_epochs=12,
    initialize_from=None,
    auxiliary_loss=None,
    pipeline=dict(
        screening=dict(
            probe=dict(
                type="TeacherForcedDualSpanAttentionProbe",
                samples_per_screening=96,
                seed=20260901,
                require_reference_count=1,
                artifact_dtype="float16",
            ),
            finder=dict(
                type="R003QueryHeadFinder",
                per_sample=10,
                mean_multiplier=1.0,
                excluded_layers=(0, 1),
            ),
        ),
        stages=dict(
            warmup=dict(start_step=0, auxiliary_loss=None),
            early=dict(
                start_step=83,
                auxiliary_loss=dict(**_gt_mask, coefficient=0.02),
                ramp_steps=83,
                ramp_from_coefficient=0.0,
                head_selection=dict(role="query", top_k=3, refresh_steps=83),
            ),
            adaptive=dict(
                start_step=494,
                auxiliary_loss=dict(**_gt_mask, coefficient=0.05),
                ramp_steps=83,
                ramp_from_coefficient=0.02,
                head_selection=dict(role="query", top_k=5, refresh_steps=83),
            ),
            fixed=dict(
                start_step=1482,
                auxiliary_loss=dict(**_gt_mask, coefficient=0.1),
                ramp_steps=83,
                ramp_from_coefficient=0.05,
                head_selection=dict(role="query", top_k=5, refresh_steps=None),
            ),
        ),
    ),
)
