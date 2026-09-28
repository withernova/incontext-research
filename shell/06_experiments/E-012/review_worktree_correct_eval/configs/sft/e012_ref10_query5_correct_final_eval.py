"""Standard FOCUS autoregressive evaluation of the E-012 correct final adapter."""

branch = dict(
    parent_config="qwen3vl_8b_lora_focus_1shot_ddp4_4bit.py",
    action="evaluate",
    nproc_per_node=4,
    periodic_head_screening=False,
    source="e012_correct_final",
    source_profiles=dict(
        e012_correct_final=dict(
            kind="checkpoint",
            experiment_id="E-012",
            parent_checkpoint=(
                "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/"
                "ref10-query5-correct-step247-3ep-v1/training"
            ),
        ),
    ),
)

named_run = dict(
    experiment_root="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments",
    experiment_id="E-012",
    run_name="ref10-query5-correct-final-eval",
    run_kind="branch-evaluate",
    mode="new",
    timestamp="auto",
    parent_checkpoint=None,
    require_parent_checkpoint=False,
    run_dir=None,
    resume_checkpoint=None,
    tags=["focus", "qwen3vl", "e012", "correct", "final", "eval"],
    notes=(
        "复用标准FOCUS branch evaluator评测E-012 correct三轮训练的final adapter；"
        "这是只读评测，不恢复optimizer或trainer state。"
    ),
)

runtime = dict(
    evaluator=dict(
        type="LocalizationEvaluator",
        iou_thresholds=(0.25, 0.5, 0.75),
    ),
    test_dataloader=dict(
        batch_size=1,
        dataset=dict(
            type="IPLocManifestDataset",
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

evaluation = dict(
    dataloader="test_dataloader",
    limit=None,
    selection="head",
    seed=20260901,
    vision_max_patch_tokens=4096,
    max_new_tokens=32,
    do_sample=False,
    log_interval=10,
)
