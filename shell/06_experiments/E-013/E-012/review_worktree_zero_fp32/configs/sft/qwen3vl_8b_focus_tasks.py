"""Task selection, checkpoint and experiment settings for this localization recipe."""

# Select any compatible parent config. Relative paths resolve from this file.
branch = dict(
    parent_config="qwen3vl_8b_lora_focus_1shot_ddp4_4bit.py",

    # Choices: "train", "evaluate", "head_screen".
    action="evaluate",
    nproc_per_node=4,
    # For action="train", optionally screen twice per epoch while training.
    periodic_head_screening=False,
)

# Every action is a new child of this checkpoint unless mode="resume" is used
# for continuing the exact same named training run.
named_run = dict(
    experiment_root="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments",
    experiment_id="E-009",
    run_name="highlr-gt-mask-494-eval",
    run_kind="branch-eval-ft",
    mode="new",
    timestamp="auto",
    parent_checkpoint=(
       "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/checkpoints/samples_00005267_step_000083"
   ),
    require_parent_checkpoint=True,
    run_dir=None,
    resume_checkpoint=None,
    tags=["1shot", "nf4", "ddp4", "head-screening", "checkpoint-stability"],
    notes=(
        "One fixed-manifest standalone head screen. Cross-checkpoint stability is "
        "computed offline; the per-run stable_candidate field is not used."
    ),
)

# Deep-merge runtime changes onto branch.parent_config. Examples:
# runtime = dict(runner=dict(optimizer=dict(lr=1e-5), max_epochs=2))
# runtime = dict(train_dataloader=dict(batch_size=1))
runtime = dict(
    checkpoint_suite=dict(
        work_dir=(
            "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
            "E009-R-007-head-stability-many-with-base-model"
        ),
        checkpoints=(
            # This is the original Qwen3-VL model_path from the parent config.
            # The suite restores its initial, untrained LoRA tensors and loads
            # no adapter checkpoint for this entry.
            dict(label="zero-shot", kind="base_model"),
            dict(
                label="step0083",
                path=(
                    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
                    "E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/checkpoints/"
                    "samples_00005267_step_000083"
                ),
            ),
            dict(
                label="step0247",
                path=(
                    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
                    "E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/checkpoints/"
                    "samples_00015801_step_000247"
                ),
            ),
            dict(
                label="step0494",
                path=(
                    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
                    "E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/checkpoints/"
                    "samples_00031602_step_000494"
                ),
            ),
            
            dict(
                label="step1482",
                path=(
                    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
                    "E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/checkpoints/"
                    "samples_00094806_step_001482"
                ),
            ),
            dict(
                label="step1564",
                path=(
                    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
                    "E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/checkpoints/"
                    "samples_00100073_step_001564"
                ),
            ),
            dict(
                label="step1646",
                path=(
                    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
                    "E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/checkpoints/"
                    "samples_00105340_step_001646"
                ),
            ),
            dict(
                label="step1729",
                path=(
                    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
                    "E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/checkpoints/"
                    "samples_00110607_step_001729"
                ),
            ),
        ),
    ),
    # Standalone head screening is built through build_training(), so it reads
    # train_dataloader rather than evaluation.dataloader.  Keep every checkpoint
    # on the same frozen 100-row post-hoc validation subset.  The combined test
    # manifest below remains evaluation-only and must not participate in head
    # discovery or checkpoint selection.
    train_dataloader=dict(
        batch_size=1,
        dataset=dict(
            ann_file=(
                "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
                "E009-real-focus-data/manifests/"
                "val_lasot_posthoc_valid96_1shot_focus.json"
            ),
        ),
    ),
    evaluator=dict(
        type="LocalizationEvaluator",
        iou_thresholds=(0.25, 0.5, 0.75),
    ),
    test_dataloader=dict(
        batch_size=1,
        dataset=dict(
            type="IPLocManifestDataset",
            # Frozen 100-row validation subset already used by E-009.
            # Select the reserved 600-row test manifest only by explicit override.
            ann_file=(
                "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
                "E009-real-focus-data/manifests/"
                "test_combined_lasot600_gotval_taoval_1shot_focus.json"
            ),
            target_role="positive-image",
            normalized_scale=1000,
            prompt_protocol="focus",
        ),
    ),
)

# The manifest is already the frozen seeded-random 100-row validation subset,
# so consume it in full without selecting again.  After checkpoint selection,
# explicitly override runtime.test_dataloader.dataset.ann_file with
# val_lasot_posthoc_test600_1shot_focus.json to touch the reserved test split.
evaluation = dict(
    dataloader="test_dataloader",
    limit=None,
    selection="head",
    seed=20260901,
    # Match the 1-shot training collator. Without this cap, 4K GOT images
    # create a quadratic SDPA prefill allocation far beyond a 24 GiB GPU.
    vision_max_patch_tokens=4096,
    # Bbox answers are short; this already bounds decode/KV-cache growth.
    max_new_tokens=32,
    do_sample=False,
    log_interval=10,
)

# Used by standalone action="head_screen" and, when enabled, periodic training.
head_screening = dict(
    interval_epochs=0.5,
    start_epoch=0.5,
    stability_head_count=5,
    stability_jaccard=1.0,
    stability_patience=3,
    probe=dict(
        type="TeacherForcedDualSpanAttentionProbe",
        # This equals the audited valid-manifest size, so all checkpoints use
        # the same 96 positive-area samples without random subsampling.
        samples_per_screening=96,
        seed=20260901,
        require_reference_count=1,
        artifact_dtype="float16",
    ),
    finder=dict(
        type="R003T003HeadFinder",
        per_sample=10,
        mean_multiplier=1.0,
        excluded_layers=(0, 1),
        fixed_head_counts=(3, 5),
        entropy_weight=1.0,
        iou_reward_weight=2.0,
        iou_threshold=0.1,
    ),
)
