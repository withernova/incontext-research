"""Four-GPU DDP 1-shot NF4 QLoRA SFT, equivalent to the single-GPU batch."""

_base_ = "qwen3vl_8b_lora_focus_1shot_single_4bit.py"

work_dir = (
    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
    "E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4"
)

runner = dict(
    # 4 ranks x per-rank batch 1 x accumulation 16 = 64, exactly matching
    # the single-rank batch 1 x accumulation 64 configuration. This keeps
    # optimizer-step semantics and checkpoint sample progress aligned.
    gradient_accumulation_steps=16,
    hooks=[
        dict(type="FiniteHook"),
        dict(type="LoggerHook"),
        dict(type="TrainingHistoryHook"),
        dict(type="GpuMemoryHook"),
        dict(type="MetricsWriterHook"),
    ],
)
