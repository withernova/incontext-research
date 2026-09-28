"""Frozen real-checkpoint R-004 correctness gate."""

work_dir = (
    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/"
    "R-004-contribution-calculation-check/real-checkpoint-attempt-001"
)

model = dict(
    type="Qwen3VLNative",
    model_path="/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct",
    dtype="bfloat16",
    device_map="auto",
    attn_implementation="eager",
    local_files_only=True,
)

checkpoint_path = (
    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/"
    "ref10-query5-correct-step247-3ep-v1/training/checkpoints/"
    "samples_00031566_step_000494"
)

input_manifest = (
    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
    "E009-real-focus-data/manifests/"
    "test_combined_lasot600_gotval_taoval_1shot_focus.json"
)

screen_dataloader = dict(
    batch_size=1,
    dataset=dict(type="IPLocManifestDataset", ann_file=input_manifest,
                 prompt_protocol="focus", normalized_scale=1000),
    collator=dict(type="Qwen3VLSFTCollator", assistant_only=True,
                  vision_max_patch_tokens=1024),
)

r004 = dict(
    input_manifest_sha256="48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b",
    sample_indices=list(range(8)),
    layer_heads=[(20, 18), (24, 25)],
    epsilons=[1e-3, 1e-2],
    algebra_atol=2e-6,
    algebra_rtol=2e-3,
    fd_relative_error_max=0.15,
    parity_atol=0.002,
    max_sequence_tokens=2048,
)
