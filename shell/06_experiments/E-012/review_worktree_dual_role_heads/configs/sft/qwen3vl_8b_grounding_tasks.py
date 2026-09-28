"""Task selection, checkpoint and experiment settings for this localization recipe."""

branch = dict(
    parent_config="qwen3vl_8b_grounding.py",
    action="evaluate",
    nproc_per_node=4,
    periodic_head_screening=False,
)

named_run = dict(
    experiment_root="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments",
    experiment_id="E-011",
    run_name="qwen3-grounding-adapter-eval",
    run_kind="adapter-eval",
    mode="new",
    timestamp="auto",
    # Select the evaluation checkpoint here. The shell does not override it.
    parent_checkpoint="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-011/sft-runs/e011-grounding-sft-v1/checkpoints/samples_00029502_step_000461",
    require_parent_checkpoint=True,
    run_dir=None,
    resume_checkpoint=None,
    tags=["1shot", "qwen3-grounding", "nf4", "ddp4", "evaluation"],
    notes="Autoregressive adapter evaluation using the training-time JSON bbox protocol.",
)

# Model, prompt, datasets and evaluation settings come from parent_config.
