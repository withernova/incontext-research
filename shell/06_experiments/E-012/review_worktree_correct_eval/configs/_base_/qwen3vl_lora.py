"""Shared local Qwen3-VL-8B language-side LoRA configuration."""

model = dict(
    type="Qwen3VLLoRASFT",
    model_path=(
        "/defaultShare/archive/liuwenchu/projects/IPLoc/"
        "mechanism/models/Qwen3-VL-8B-Instruct"
    ),
    dtype="bfloat16",
    device_map="auto",
    # CUDA_VISIBLE_DEVICES remaps physical GPUs to these local indices.
    max_memory={0: "22GiB", 1: "22GiB"},
    gradient_checkpointing=True,
    lora=dict(
        r=8,
        alpha=16,
        dropout=0.0,
        # Match the existing IPLoc-ID adapter while excluding visual modules.
        target_modules=(
            r"^(?!.*visual).*"
            r"(?:down_proj|v_proj|gate_proj|up_proj|k_proj|o_proj|q_proj).*$"
        ),
    ),
)
