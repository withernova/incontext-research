"""Single-GPU, DDP-style Qwen3-VL LoRA SFT with one FOCUS support."""

_base_ = "../_base_/localization_sft.py"

# ``torchrun --nproc_per_node=1`` exercises the same wrapper/checkpoint path
# as multi-rank DDP while one complete model replica occupies one GPU.
model = dict(attn_implementation="sdpa")

work_dir = (
    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
    "E009-focus-qwen3vl8b-lora-1shot-single"
)

train_dataloader = dict(
    batch_size=1,
    dataset=dict(
        type="IPLocManifestDataset",
        ann_file=(
            "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
            "E009-real-focus-data/manifests/train_only_1shot_focus.json"
        ),
        target_role="positive-image",
        normalized_scale=1000,
        prompt_protocol="focus",
    ),
    collator=dict(type="Qwen3VLSFTCollator", vision_max_patch_tokens=1024),
)

runner = dict(
    # Cheap per-step teacher-forced localization diagnostics.  They are not
    # autoregressive validation scores; train-only manifests have no held-out
    # validation split by design.
    localization_iou_thresholds=(0.25, 0.5, 0.75),
    # Preserve effective global batch 64 while minimizing one microbatch's
    # visual context for a single-GPU capability check.
    max_epochs=12,
    checkpoint_interval_epochs=0.5,
    gradient_accumulation_steps=64,
    seed=20260827,
)
