"""Two-rank DDP: one complete frozen Qwen3-VL-8B model per GPU."""

model = dict(
    type="Qwen3VLLoRADDP",
    model_path=(
        "/defaultShare/archive/liuwenchu/projects/IPLoc/"
        "mechanism/models/Qwen3-VL-8B-Instruct"
    ),
    dtype="bfloat16",
    gradient_checkpointing=True,
    find_unused_parameters=False,
    lora=dict(
        r=8,
        alpha=16,
        dropout=0.0,
        target_modules=(
            r"^(?!.*visual).*"
            r"(?:down_proj|v_proj|gate_proj|up_proj|k_proj|o_proj|q_proj).*$"
        ),
    ),
)
