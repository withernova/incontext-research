"""R-001 gradient Top-10 的 teacher-forced bbox-row → query-image attention 可视化。"""
visualization_spec = dict(
    source_run_dir="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-001-bbox-gradient-halffull",
    output_dir="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/visualizations/r001-gradient-top10-attention-maps-v1",
    top_k=10,
    samples_per_dataset=dict(LaSOT=2, GOT10k=2, TAO=2),
)
