"""Two-GPU DDP FOCUS SFT: each rank keeps one complete, unsharded model."""

_base_ = "../_base_/qwen3vl_lora_ddp.py"

# Safe default. The launcher may override this with --flash-attn when a
# compatible flash-attn runtime is available on the target host.
model = dict(attn_implementation="sdpa")

work_dir = (
    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
    "E009-focus-qwen3vl8b-lora-ddp"
)

model = dict(
    attn_implementation="sdpa",
)


train_dataloader = dict(
    # Per-rank batch size. With two ranks and accumulation 16, the effective
    # global batch is 32; override only after a successful batch-1 probe.
    batch_size=1,
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
    collator=dict(type="Qwen3VLSFTCollator", vision_max_patch_tokens=2048),
)

runner = dict(
    type="SFTLoRARunner",
    assistant_only_logits=True,
    # With two ranks, batch 1, and accumulation 16, the runner derives 329
    # updates per epoch from the frozen train-only manifest.
    max_epochs=12,
    checkpoint_interval_epochs=0.5,
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
