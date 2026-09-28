"""Two-RTX-3090 LoRA batch-scaling probe on the deterministic SFT data.

Run this configuration with explicit overrides, for example:

    python tools/train.py configs/sft/qwen3vl_8b_lora_batch_scaling.py \
        --cfg-options train_dataloader.batch_size=4 work_dir=./work_dirs/bs4

Each bounded run performs three optimizer steps and records examples/second and
peak allocated memory for both visible GPUs. Increase physical batch size in the
pre-registered order 1, 2, 4, 8 and stop after the first CUDA OOM. Gradient
accumulation is fixed at one because this experiment measures physical batch
capacity rather than effective batch size.
"""

_base_ = "../_base_/qwen3vl_lora.py"

work_dir = "./work_dirs/qwen3vl_8b_lora_batch_scaling"
train_dataloader = dict(
    batch_size=1,
    dataset=dict(
        type="SyntheticLocalizationDataset",
        root="./work_dirs/qwen3vl_8b_lora_batch_scaling/data",
        repeat=2,
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
