"""E-012：两阶段 head 协作的跨层 path-patching smoke。

此 config 与梯度排名、GT-attention eval 分离，后续可直接替换 paths 中的 head 集合，
用于更细粒度的 U→D 候选筛查。运行时只读取 R-001 已冻结的样本索引。
"""

work_dir = "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-002-two-stage-head-path-patching-smoke"

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

# 仅复用 BBoxGradientAttentionProbe.encode_sample 的 bbox p-1 rows 和双图网格校验；
# 本实验不做反向传播，也不使用该 probe 的 gradient ranking。
head_screening = dict(
    probe=dict(type="BBoxGradientAttentionProbe", samples=12, seed=20260912,
               max_sequence_tokens=2048, parity_atol=0.002, parity_rtol=0.002,
               finite_difference_epsilon=0.02),
)

head_circuit = dict(
    sample_source="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-001-bbox-gradient-halffull/frozen_input.json",
    samples_per_dataset=dict(LaSOT=4, GOT10k=4, TAO=4),
    parity_atol=0.002,
    parity_rtol=0.002,
    paths=[
        dict(
            name="P1_L21_sensitive_to_L23_decodable",
            upstream=[[21, 31], [21, 11]],
            # 同层低 A/B 对照；数量与 candidate upstream 相同。
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
