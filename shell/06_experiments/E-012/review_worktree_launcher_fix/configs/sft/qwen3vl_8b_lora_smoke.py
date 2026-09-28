"""Three-step synthetic capability smoke for the config-driven runner."""

_base_ = "../_base_/qwen3vl_lora.py"

work_dir = "./work_dirs/qwen3vl_8b_lora_smoke"
train_dataloader = dict(
    # The initial collator intentionally supports one sample per forward.
    batch_size=1,
    dataset=dict(
        type="SyntheticLocalizationDataset",
        root="./work_dirs/qwen3vl_8b_lora_smoke/data",
        repeat=2,
    ),
    collator=dict(type="Qwen3VLSFTCollator"),
)
runner = dict(
    type="SFTLoRARunner",
    max_steps=3,
    seed=20260825,
    optimizer=dict(lr=1e-3, weight_decay=0.0),
    hooks=[
        dict(type="FiniteHook"),
        dict(type="LoggerHook"),
        dict(type="GpuMemoryHook"),
        dict(type="MetricsWriterHook"),
    ],
)
