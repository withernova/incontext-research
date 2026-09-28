"""Single-GPU 1-shot NF4 QLoRA capability configuration."""

_base_ = "qwen3vl_8b_lora_focus_1shot_single.py"

model = dict(
    attn_implementation="sdpa",
    quantization=dict(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype="bfloat16",
    ),
)

work_dir = (
    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
    "E009-focus-qwen3vl8b-lora-1shot-nf4-single"
)
