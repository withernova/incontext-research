"""Template for reference-conditioned IPLoc LoRA supervised training."""

_base_ = "../_base_/qwen3vl_lora.py"

work_dir = "./work_dirs/qwen3vl_8b_iploc"
# Copy this config for a concrete run and replace the placeholder with a frozen
# manifest path. Do not silently point a registered run at a different dataset.
ann_file = "/path/to/iploc_manifest.json"

train_dataloader = dict(
    batch_size=32,
    dataset=dict(
        type="IPLocManifestDataset",
        ann_file=ann_file,
        # FOCUS is the primary category-free training protocol. Set to
        # "iploc" only for the category/pseudo-name ablation.
        prompt_protocol="focus",
    ),
    collator=dict(type="Qwen3VLSFTCollator"),
)
test_dataloader = dict(
    batch_size=1,
    dataset=dict(
        type="IPLocManifestDataset",
        ann_file=ann_file,
        # FOCUS is the primary category-free training protocol. Set to
        # "iploc" only for the category/pseudo-name ablation.
        prompt_protocol="focus",
    ),
)
evaluator = dict(
    type="LocalizationEvaluator",
    iou_thresholds=(0.3, 0.5, 0.7),
)
runner = dict(
    type="SFTLoRARunner",
    max_steps=1000,
    seed=20260825,
    optimizer=dict(lr=2e-4, weight_decay=0.0),
    hooks=[
        dict(type="FiniteHook"),
        dict(type="LoggerHook"),
        dict(type="GpuMemoryHook"),
        dict(type="MetricsWriterHook"),
    ],
)
