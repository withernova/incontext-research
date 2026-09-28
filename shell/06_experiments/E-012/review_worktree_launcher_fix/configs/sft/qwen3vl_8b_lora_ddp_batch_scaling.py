"""Per-device batch scaling with one full Qwen3-VL replica on each GPU."""

_base_ = "../_base_/qwen3vl_lora_ddp.py"

work_dir = "./work_dirs/qwen3vl_8b_lora_ddp_batch_scaling"
train_dataloader = dict(
    # In torchrun this is per-device batch size. With two ranks, global physical
    # batch is twice this value before gradient accumulation.
    batch_size=1,
    dataset=dict(
        type="SyntheticLocalizationDataset",
        root="./work_dirs/qwen3vl_8b_lora_ddp_batch_scaling/data",
        # At least two disjoint rank batches are available before cycling.
        repeat=4,
    ),
    collator=dict(type="Qwen3VLSFTCollator"),
)
runner = dict(
    type="SFTLoRARunner",
    max_steps=3,
    gradient_accumulation_steps=1,
    seed=20260825,
    optimizer=dict(lr=1e-3, weight_decay=0.0),
    hooks=[
        dict(type="FiniteHook"),
        dict(type="LoggerHook"),
        dict(type="GpuMemoryHook"),
        dict(type="MetricsWriterHook"),
    ],
)
