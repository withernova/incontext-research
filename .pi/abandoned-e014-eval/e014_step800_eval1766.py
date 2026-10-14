"""Frozen E-014 step800 evaluation on the original 1766 positive queries."""
ROOT = "/defaultShare/archive/songzhengyue/projects/IPLoc"
settings = dict(
    run_id="e014-step800-variable-candidates-eval1766-8gpu",
    model_path=ROOT + "/mechanism/models/Qwen3-VL-8B-Instruct",
    checkpoint=ROOT + "/experiments/E-014/e014-variable-symmetric-sft659-puregrpo-seed11451/resume-100/grpo/checkpoints/step_000800",
    manifest=ROOT + "/experiments/E-009/E009-real-focus-data/manifests/test_combined_lasot600_gotval_taoval_1shot_focus.json",
    manifest_sha256="48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b",
    dataset_size=1766, nproc_per_node=8,
    evaluation=dict(max_new_tokens=192, do_sample=False,
                    vision_max_patch_tokens=4096, seed=20260901),
    evaluator=dict(type="E014VariableCandidateLocalizationEvaluator",
                   iou_thresholds=(0.25, 0.5, 0.75)),
)
