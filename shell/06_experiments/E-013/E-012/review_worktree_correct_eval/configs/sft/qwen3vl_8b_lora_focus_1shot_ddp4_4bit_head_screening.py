"""Four-GPU 1-shot NF4 QLoRA with isolated half-epoch head screening."""

_base_ = "qwen3vl_8b_lora_focus_1shot_ddp4_4bit_named.py"

# Every branch gets a timestamped, isolated work directory and an indexed
# parent relation.  Supply parent_checkpoint on the command line or edit it
# here; mode="resume" is reserved for continuing the exact same named run.
named_run = dict(
    run_name="focus-qwen3vl8b-1shot-nf4-ddp4-headscreen-n100",
    run_kind="branch-train-headscreen",
    tags=["1shot", "nf4", "ddp4", "head-screening", "n100"],
    notes="Teacher-forced head screening twice per epoch; no added attention loss.",
)

# All experiment-level screening controls live here.  Edit this block instead
# of changing the probe/finder implementation.  The ordinary training config
# remains untouched.
head_screening = dict(
    # Schedule: two screenings per epoch, starting at epoch 0.5.
    interval_epochs=0.5,
    start_epoch=0.5,
    # Convergence: exact Top-5 equality for three consecutive comparisons.
    stability_head_count=5,
    stability_jaccard=1.0,
    stability_patience=3,
    probe=dict(
        type="TeacherForcedDualSpanAttentionProbe",
        # Global count. With four ranks, each rank probes 25 samples.
        samples_per_screening=100,
        seed=20260901,
        require_reference_count=1,
        artifact_dtype="float16",
    ),
    finder=dict(
        type="R003T003HeadFinder",
        # R003 no-GT selector.
        per_sample=10,
        mean_multiplier=1.0,
        excluded_layers=(0, 1),
        # Shared persisted sets; stability_head_count must be included here.
        fixed_head_counts=(3, 5),
        # R006-T003 reference selector.
        entropy_weight=1.0,
        iou_reward_weight=2.0,
        iou_threshold=0.1,
    ),
)

runner = dict(
    hooks=[
        dict(type="FiniteHook"),
        dict(type="LoggerHook"),
        dict(type="TrainingHistoryHook"),
        dict(
            type="HeadScreeningHook",
            **head_screening,
        ),
        dict(type="GpuMemoryHook"),
        dict(type="MetricsWriterHook"),
    ],
)
