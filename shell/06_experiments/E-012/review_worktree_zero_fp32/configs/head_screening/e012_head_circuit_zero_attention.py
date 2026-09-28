"""E-012：直接抹除 query-visual attention 的两阶段 head 路径测试。

【样本数量只改这一处】每个数据集从 R-001 已冻结索引中依次选取。
例如较小测试可设 dict(LaSOT=4, GOT10k=4, TAO=4)；
当前默认稍微扩展为 20/20/20，共 60 条。
"""
screening_counts = dict(LaSOT=20, GOT10k=20, TAO=20)

# 输出目录必须不存在；新一轮请手动修改目录名，禁止覆盖旧结果。
work_dir = "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-003-zero-query-attention-head-path-patching-v2"

model = dict(
    type="Qwen3VLNative",
    model_path="/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct",
    dtype="bfloat16", device_map="auto", attn_implementation="eager", local_files_only=True,
)
checkpoint_path = "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-011/20260907T174853785543Z--focus-early-gt-mask-pipeline/checkpoints/samples_00126264_step_001973"

input_manifest = "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-real-focus-data/manifests/test_combined_lasot600_gotval_taoval_1shot_focus.json"
screen_dataloader = dict(
    batch_size=1,
    dataset=dict(type="IPLocManifestDataset", ann_file=input_manifest,
                 prompt_protocol="focus", normalized_scale=1000),
    collator=dict(type="Qwen3VLSFTCollator", assistant_only=True,
                  vision_max_patch_tokens=1024),
)
head_screening = dict(
    probe=dict(type="BBoxGradientAttentionProbe", samples=sum(screening_counts.values()),
               seed=20260912, max_sequence_tokens=2048,
               parity_atol=0.002, parity_rtol=0.002,
               finite_difference_epsilon=0.02),
)

head_circuit = dict(
    # 不重归一化：只把候选 head 的 bbox p-1 rows × query visual keys 置零。
    corruption_mode="zero_query_attention",
    sample_source="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-001-bbox-gradient-halffull/frozen_input.json",
    samples_per_dataset=screening_counts,
    parity_atol=0.002,
    parity_rtol=0.002,
    paths=[
        dict(
            name="P1_L21_sensitive_to_L23_decodable",
            upstream=[[21, 31], [21, 11]],
            upstream_control=[[21, 6], [21, 7]],
            downstream=[[23, 19], [23, 2], [23, 30], [23, 31]],
            downstream_control=[[23, 8], [23, 21], [23, 20], [23, 27]],
        ),
        dict(
            name="P2_L23_decodable_to_L24_L26_sensitive",
            upstream=[[23, 19], [23, 2], [23, 30], [23, 31]],
            upstream_control=[[23, 8], [23, 21], [23, 20], [23, 27]],
            downstream=[[24, 13], [26, 25]],
            downstream_control=[[24, 18], [26, 2]],
        ),
    ],
)
