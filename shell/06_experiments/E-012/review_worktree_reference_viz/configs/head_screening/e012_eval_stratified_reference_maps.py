"""E-012 correct step494：按自回归 eval IoU 高低分层的 reference-head 可视化。"""

_eval_root = (
    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/"
    "ref10-query5-correct-step247-3ep-v1/training/branches/"
    "20260914T001057740901Z--eval-494/evaluation"
)

visualization_spec = dict(
    selection_summary=(
        "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/"
        "checkpoint-spatial-stability-e009-v1/step_1153_reference/summary.json"
    ),
    selection_summary_sha256="14fd17485ffdc30a7194fea1afd692835a1f62d61fd882f6965c318ef59bdc93",
    eval_metrics=f"{_eval_root}/metrics.json",
    eval_metrics_sha256="6d88fe98983a2d865b1da08a5cd13fa385d64f51be6451498425bd7795ae823e",
    eval_predictions=f"{_eval_root}/predictions.jsonl",
    eval_predictions_sha256="9d4e2ed3aff0f5aa556c872c40647a6851ec9089e682d798967b1d89bf6787b9",
    eval_manifest=(
        "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/"
        "E009-real-focus-data/manifests/"
        "test_combined_lasot600_gotval_taoval_1shot_focus.json"
    ),
    eval_manifest_sha256="48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b",
    checkpoint=(
        "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/"
        "ref10-query5-correct-step247-3ep-v1/training/checkpoints/"
        "samples_00031566_step_000494"
    ),
    screen_config="configs/head_screening/e012_bbox_gradient_initial.py",
    output_dir=(
        "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/"
        "reference-gt-correct-step494-eval-stratified-v2"
    ),
    datasets=("LaSOT", "GOT10k", "TAO"),
    samples_per_tail=2,
    # Match standard eval preprocessing (4096 unmerged patch tokens per image).
    vision_max_patch_tokens=4096,
    # The selected rows encode to 496--2177 tokens; no truncation is permitted.
    # This remains far below Qwen3-VL's 262144-position model limit.
    max_sequence_tokens=4096,
    replay_precision="BF16 eager teacher-forced; eval stratification came from NF4 autoregressive generation",
)
