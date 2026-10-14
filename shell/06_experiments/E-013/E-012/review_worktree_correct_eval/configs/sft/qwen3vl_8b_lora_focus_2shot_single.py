"""Single-GPU, DDP-style Qwen3-VL LoRA SFT with two FOCUS supports."""

_base_ = "../_base_/qwen3vl_lora_ddp.py"

# ``torchrun --nproc_per_node=1`` preserves the DDP wrapper and checkpoint
# code path while placing one complete model replica on one selected GPU.
model = dict(attn_implementation="sdpa")

work_dir = (
    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
    "E009-focus-qwen3vl8b-lora-2shot-single"
)

train_dataloader = dict(
    batch_size=1,
    dataset=dict(
        type="IPLocManifestDataset",
        ann_file=(
            "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
            "E009-real-focus-data/manifests/train_only_2shot_focus.json"
        ),
        target_role="positive-image",
        normalized_scale=1000,
        prompt_protocol="focus",
    ),
    collator=dict(type="Qwen3VLSFTCollator", vision_max_patch_tokens=2048),
)

runner = dict(
    type="SFTLoRARunner",
    assistant_only_logits=True,
    # Preserve the sharded experiment's effective global batch (64) with one
    # physical example per step. The runner derives updates per epoch from the
    # frozen two-shot train-only manifest.
    max_epochs=12,
    checkpoint_interval_epochs=0.5,
    resume_from=None,
    gradient_accumulation_steps=64,
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
