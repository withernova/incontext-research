"""Native Qwen3-VL evaluation using the shared frozen E-011 scope."""

_base_ = "../_base_/e011_frozen_eval.py"

model = dict(
    type="Qwen3VLNative",
    model_path=(
        "/defaultShare/archive/liuwenchu/projects/IPLoc/"
        "mechanism/models/Qwen3-VL-8B-Instruct"
    ),
    dtype="bfloat16",
    device_map="balanced",
    max_memory=None,
    attn_implementation="sdpa",
    local_files_only=True,
)
launch = dict(action="infer", nproc_per_node=1)
work_dir = (
    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-011/"
    "native-qwen3vl-runs/e011-native-config"
)
