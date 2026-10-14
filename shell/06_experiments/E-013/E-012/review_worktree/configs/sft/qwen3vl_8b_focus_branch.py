"""Qwen3-VL FOCUS 通用分支配置：native、E011 与旧 E009 共用一个入口。"""

branch = dict(
    parent_config="qwen3vl_8b_lora_focus_1shot_ddp4_4bit.py",
    action="attention_intervene",  # 可选：train / evaluate / head_screen / attention_intervene
    nproc_per_node=4,
    periodic_head_screening=False,

    # 通常只改这一项即可切换父模型；也可用 CLI：branch.source=e011_gt_mask。
    source="e011_gt_mask",
    source_profiles=dict(
        # native：直接从 Qwen3-VL 原模型开始，不加载任何 LoRA checkpoint。
        native=dict(kind="base_model", experiment_id="E-011"),

        # E011 early-GT-mask 当前已生成的 checkpoint。若要换训练阶段，只改路径。
        e011_gt_mask=dict(
            kind="checkpoint",
            experiment_id="E-011",
            parent_checkpoint=(
                "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-011/20260907T174853785543Z--focus-early-gt-mask-pipeline/checkpoints/samples_00005261_step_000083"
            ),
        ), 

        # 旧 E009 FOCUS checkpoint 示例；可复制此项添加更多 E009 checkpoint。
        e009_step0083=dict(
            kind="checkpoint",
            experiment_id="E-009",
            parent_checkpoint=(
                "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
                "E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/checkpoints/"
                "samples_00005267_step_000083"
            ),
        ),
    ),
)

named_run = dict(
    experiment_root="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments",
    # experiment_id、parent_checkpoint 和 require_parent_checkpoint 会由
    # branch.source 对应的 profile 自动填写，避免三处手工修改不一致。
    experiment_id="E-011",
    run_name="pipeline-083-attention-interv",  # 每次正式运行前请改成能说明干预内容的名字。
    run_kind="branch-train",
    mode="new",
    timestamp="auto",
    parent_checkpoint=None,
    require_parent_checkpoint=False,
    run_dir=None,
    resume_checkpoint=None,
    tags=["focus", "qwen3vl", "branch"],
    notes="通用 FOCUS branch；父模型来源由 branch.source 选择。",
)

# 这里只写相对父配置的差异；训练仍沿用原 FOCUS prompt 和 recipe。
# test_dataloader 供 evaluate / attention_intervene 使用；干预的自动 head 筛选也使用该 eval 集。
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

# evaluate / attention_intervene 共用；limit=None 表示完整 eval。
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

# action=head_screen 或 periodic_head_screening=True 时使用。
head_screening = dict(
    interval_epochs=0.5,
    start_epoch=0.5,
    stability_head_count=5,
    stability_jaccard=1.0,
    stability_patience=3,
    probe=dict(
        type="TeacherForcedDualSpanAttentionProbe",
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

# attention_intervene：加载 branch.source 指定的 ckpt，只筛选一次并固定 heads。
# 自动筛选使用上面的 eval 数据；samples=None 用完整 eval，与普通 head_screen 分开。
attention_intervention = dict(
    heads=(),  # 留空自动筛选；显式填写 ["L20H15", ...] 则跳过筛选。
    auto_head_screening=dict(enabled=True, top_k=5, samples=None),
    generation_steps="all",  # 整个生成序列；也可用零起始位置列表 [0,1,...]。
    normalization="overlap_area_preserve_query_mass",
    logits_atol=0.0,
    logits_rtol=0.0,
)
