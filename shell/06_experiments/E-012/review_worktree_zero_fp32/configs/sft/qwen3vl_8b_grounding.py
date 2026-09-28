"""Grounding JSON SFT and evaluation recipe; experiment paths are editable settings."""

_base_ = [
    "../_base_/localization_sft.py",
    "../_base_/e011_frozen_eval.py",
]

model = dict(
    attn_implementation="sdpa",
    local_files_only=True,
    gradient_checkpointing_kwargs=dict(use_reentrant=False),
    quantization=dict(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype="bfloat16",
    ),
)

# Set a fresh output directory here; the launcher refuses an existing directory.
work_dir = (
    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-011/"
    "sft-runs/e011-qwen3-grounding-sft"
)

train_dataloader = dict(
    batch_size=1,
    dataset=dict(
        type="IPLocManifestDataset",
        ann_file=(
            "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-011/"
            "manifests/train_only_tao_got10k_1shot_focus_iploc.json"
        ),
        target_role="positive-image",
        normalized_scale=1000,
        prompt_protocol="qwen3_grounding",
        # 改提示词时同步更新版本；日志保存实际文本和示例。
        prompt_version="qwen3-grounding-v1",
        prompt_text='Use the annotated reference image or images to identify the same target object in the final image. Coordinates are integers normalized to the range 0 to 1000. Report bbox coordinates as a JSON list with exactly one item in this format: [{"bbox_2d": [x1, y1, x2, y2], "label": "target label"}]. Output JSON only, without Markdown fences or additional explanation.',
    ),
    collator=dict(type="Qwen3VLSFTCollator", vision_max_patch_tokens=1024),
)

runner = dict(
    max_epochs=10,
    checkpoint_interval_epochs=1.0,
    initialize_from=None,
    # Effective global batch: 4 ranks x 1 sample x 16 accumulation = 64.
    gradient_accumulation_steps=16,
    seed=20260904,
)

launch = dict(action="train", nproc_per_node=4)
