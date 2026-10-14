"""Shared Qwen3-VL localization SFT defaults across experiment families."""

_base_ = "qwen3vl_lora_ddp.py"

model = dict(attn_implementation="sdpa")
runner = dict(
    type="SFTLoRARunner",
    assistant_only_logits=True,
    resume_from=None,
    warmup_ratio=0.03,
    max_grad_norm=0.3,
    optimizer=dict(lr=2e-4, weight_decay=0.0),
    hooks=[
        dict(type="FiniteHook"),
        dict(type="LoggerHook"),
        dict(type="TrainingHistoryHook"),
        dict(type="GpuMemoryHook"),
        dict(type="MetricsWriterHook"),
    ],
)
