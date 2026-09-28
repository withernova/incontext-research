"""E-012：复用已有 eval manifest，对指定 checkpoint 做 bbox 梯度初筛。"""

# 【样本数量只改这一处】下面保留已跑过的20条初筛设置；总数在后面自动求和。
# 使用完整test清单1766条：改成 dict(LaSOT=600, GOT10k=180, TAO=986)。
# 使用20条小规模初筛：改成 dict(LaSOT=7, GOT10k=7, TAO=6)。
# 不需要另建config或更换启动脚本，input_manifest也不需要变。
screening_counts = dict(LaSOT=300, GOT10k=90, TAO=300)

# 输出目录不能已存在，避免覆盖已完成/失败尝试；开始另一轮时请换目录。
# 例如全量时改为同一E-012目录下的 bbox-gradient-full-eval-step1973。
work_dir = "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-001-bbox-gradient-halffull"

# model_path 始终指向完整的原始模型，不要填只包含 LoRA adapter 的训练目录。
# 本探针使用 BF16 底座 + adapter，不复现训练时的 4bit 量化数值路径。
model = dict(
    type="Qwen3VLNative",
    model_path="/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct",
    dtype="bfloat16", device_map="auto", attn_implementation="eager", local_files_only=True,
)

# None：筛查原始模型。下面的路径：加载指定step 1973保存的adapter。
# 也支持具体 checkpoints/samples_..._step_... 目录，或直接指向 adapter/。
# 不自动选择 latest；不会恢复 optimizer、训练进度、GT-mask hook 或其他训练干预。
# 读取 adapter_config 自动恢复 LoRA 结构，并逐张量检查权重确实加载。
checkpoint_path = "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-011/20260907T174853785543Z--focus-early-gt-mask-pipeline/checkpoints/samples_00126264_step_001973"

# 直接复用现有清单，不重新生成帧对。可换成其他兼容的 IPLoc manifest 路径。
# ann_file 也支持路径列表；清单可以远大于 samples，只筛查选中的子集。
# 此路径已经包含完整1766条：LaSOT 600 + GOT10k 180 + TAO 986。
# 实际处理多少条由顶部screening_counts决定，不是换一个“全量manifest”。
input_manifest = "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-real-focus-data/manifests/test_combined_lasot600_gotval_taoval_1shot_focus.json"
manifest_preparation = None  # 复用模式禁止 --prepare-only，避免误覆盖已有清单。

screen_dataloader = dict(
    batch_size=1,
    dataset=dict(type="IPLocManifestDataset", ann_file=input_manifest,
                 prompt_protocol="focus", normalized_scale=1000),
    # 1024 是合并前 patch 上限；spatial_merge_size=2 时每图至多约256个视觉tokens。
    collator=dict(type="Qwen3VLSFTCollator", assistant_only=True, vision_max_patch_tokens=1024),
)

# 只从训练清单中未出现的视频选样本；reference 和 query 都参加序列重叠检查。
# 按顶部配额分层选择，每视频最多一条；设为600/180/986时纳入当前清单全部记录。
# 修改数据来源时也应重新核对训练清单与其哈希，不能仅依赖文件名中的eval/test。
eval_selection = dict(
    training_manifest="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-real-focus-data/manifests/train_only_1shot_focus_valid10522.json",
    training_manifest_sha256="bd7037325096cc99097333090ec5d02f64dd9ce2922f04e0e4409d1d635bd6e7",
    samples_per_dataset=screening_counts,
)

head_screening = dict(
    probe=dict(
        type="BBoxGradientAttentionProbe",
        samples=sum(screening_counts.values()), seed=20260910,  # 自动求和，不必再手改总量。
        max_sequence_tokens=2048,  # 超预算直接报错，不静默截断图像或bbox。
        parity_atol=0.002, parity_rtol=0.002,
        finite_difference_epsilon=0.02,  # 首样本做±2%指定概率边缩放，核验signed方向。
    ),
    finder=dict(type="BBoxGradientHeadFinder"),
)
# loss仅监督bbox（包含括号/逗号等格式tokens），prediction row=p−1。
# 排名同时输出所选样本的平均分，以及各数据集单独排名；这批eval样本用于选head，
# 后续验证定位收益应使用未参与本次筛查的样本，不能用同批样本宣称泛化提升。
