"""Shared grounding protocol over the common frozen evaluation manifest."""

# Edit only this tuple to evaluate all datasets or one dataset such as ("TAO",).
SELECTED_DATASETS = ("LaSOT", "GOT10k", "TAO")
FROZEN_EVAL_MANIFEST = "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/_shared/manifests/iploc_1shot_frozen_eval_v1.json"
FROZEN_EVAL_SHA256 = "48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b"

test_dataloader = dict(
    batch_size=1,
    dataset=dict(
        type="IPLocManifestDataset",
        ann_file=FROZEN_EVAL_MANIFEST,
        ann_file_sha256=FROZEN_EVAL_SHA256,
        dataset_names=SELECTED_DATASETS,
        target_role="positive-image",
        normalized_scale=1000,
        prompt_protocol="qwen3_grounding",
        prompt_version="qwen3-grounding-v1",
        prompt_text='Use the annotated reference image or images to identify the same target object in the final image. Coordinates are integers normalized to the range 0 to 1000. Report bbox coordinates as a JSON list with exactly one item in this format: [{"bbox_2d": [x1, y1, x2, y2], "label": "target label"}]. Output JSON only, without Markdown fences or additional explanation.',
    ),
)
evaluator = dict(type="LocalizationEvaluator", iou_thresholds=(0.3, 0.5, 0.7))
evaluation = dict(
    dataloader="test_dataloader",
    datasets=SELECTED_DATASETS,
    limit=None,
    selection="head",
    seed=20260905,
    vision_max_patch_tokens=2048,
    max_new_tokens=64,
    do_sample=False,
    log_interval=10,
)
