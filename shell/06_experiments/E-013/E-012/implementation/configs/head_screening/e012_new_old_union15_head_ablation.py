"""E-012：R-001 gradient Top-10 与 E-009 固定 Query Top-5 的整头联合置零。"""
run_spec = dict(
    source_run_id="E-012/R-001",
    ranking_metric="bbox_grad_abs_contrib_mean",
    source_run_dir="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-001-bbox-gradient-halffull",
    legacy_head_source=dict(
        config_path="/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy/configs/sft/qwen3vl_8b_reference_query_alignment.py",
        config_sha256="0be113ae476b4c94a10f58af7456be04b5979c39e9b6e42b3afc83b66768f487",
        field="student_heads",
    ),
    combine_r001_top10_with_legacy=True,
    output_dir="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/new-old-union15-whole-head-ablation-v1",
    samples_per_dataset=dict(LaSOT=20, GOT10k=20, TAO=20),
    num_layers=36,
    num_heads=32,
    coordinate_scale=1000,
    random_seeds=[20260912, 20260913, 20260914],
    max_new_tokens=128,
    max_sequence_tokens=2048,
    parity_atol=0.0,
    parity_rtol=0.0,
)
