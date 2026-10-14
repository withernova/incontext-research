"""Four-GPU model-sharded Qwen3-VL LoRA SFT with the category-free FOCUS prompt.

The complete Qwen3-VL model is placed through the existing single-process
loader across four GPUs exposed by ``CUDA_VISIBLE_DEVICES``. This is not DDP:
there is exactly one model replica. Pass dotted ``--cfg-options`` through the
launcher to alter batch size, steps, learning rate, manifest, or work directory.
"""

_base_ = "../_base_/qwen3vl_lora.py"

# CUDA_VISIBLE_DEVICES remaps these local indices. Keep one model replica and
# distribute it across all four visible GPUs.
model = dict(
    attn_implementation="flash_attention_2",
    # Keep GPU3 free of Transformer blocks for lm_head logits and loss.
    device_map={
        "model.visual": 0,
        "model.language_model.embed_tokens": 0,
        "model.language_model.layers.0": 0,
        "model.language_model.layers.1": 0,
        "model.language_model.layers.2": 0,
        "model.language_model.layers.3": 0,
        "model.language_model.layers.4": 0,
        "model.language_model.layers.5": 0,
        "model.language_model.layers.6": 0,
        "model.language_model.layers.7": 0,
        "model.language_model.layers.8": 0,
        "model.language_model.layers.9": 1,
        "model.language_model.layers.10": 1,
        "model.language_model.layers.11": 1,
        "model.language_model.layers.12": 1,
        "model.language_model.layers.13": 1,
        "model.language_model.layers.14": 1,
        "model.language_model.layers.15": 1,
        "model.language_model.layers.16": 1,
        "model.language_model.layers.17": 1,
        "model.language_model.layers.18": 1,
        "model.language_model.layers.19": 1,
        "model.language_model.layers.20": 1,
        "model.language_model.layers.21": 1,
        "model.language_model.layers.22": 2,
        "model.language_model.layers.23": 2,
        "model.language_model.layers.24": 2,
        "model.language_model.layers.25": 2,
        "model.language_model.layers.26": 2,
        "model.language_model.layers.27": 2,
        "model.language_model.layers.28": 2,
        "model.language_model.layers.29": 2,
        "model.language_model.layers.30": 2,
        "model.language_model.layers.31": 2,
        "model.language_model.layers.32": 2,
        "model.language_model.layers.33": 2,
        "model.language_model.layers.34": 2,
        "model.language_model.layers.35": 2,
        "model.language_model.norm": 2,
        "model.language_model.rotary_emb": 2,
        "lm_head": 3,
    },
    max_memory={
        0: "24GiB",
        1: "24GiB",
        2: "24GiB",
        3: "24GiB",
    },
)

work_dir = (
    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
    "E009-focus-qwen3vl8b-lora-bs16"
)

train_dataloader = dict(
    batch_size=4,
    dataset=dict(
        type="IPLocManifestDataset",
        ann_file=(
            "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
            "E009-real-focus-data/manifests/train_only_4shot_focus.json"
        ),
        target_role="positive-image",
        normalized_scale=1000,
        prompt_protocol="focus",
    ),
    # max_pixels = vision_max_patch_tokens * 16 * 16; merge_size=2 reduces
    # each 2x2 raw-patch group to one language-model image token.
    collator=dict(type="Qwen3VLSFTCollator", vision_max_patch_tokens=2048),
)

runner = dict(
    type="SFTLoRARunner",
    assistant_only_logits=True,
    # The runner derives updates per epoch from this frozen train-only manifest
    # and the effective global batch. It saves after each nominal half epoch.
    max_epochs=12,
    checkpoint_interval_epochs=0.5,
    # Set to a directory under work_dir/checkpoints to continue exactly from
    # its adapter, optimizer, scheduler, step, and data-progress state.
    resume_from=None,
    gradient_accumulation_steps=16,
    warmup_ratio=0.03,
    max_grad_norm=0.3,
    seed=20260827,
    optimizer=dict(lr=2e-4, weight_decay=0.0),
    hooks=[
        dict(type="FiniteHook"),
        dict(type="LoggerHook"),
        dict(type="GpuMemoryHook"),
        dict(type="MetricsWriterHook"),
    ],
)
