"""E-012：梯度候选门控 + attention 空间质量 + 跨样本频率的选头 run。"""
selection_spec = dict(
    source_run_dir="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-001-bbox-gradient-halffull",
    output_dir="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/gradient-gated-spatial-frequency-r001-v2",
    gradient_top_m=50,
    spatial_top_m=10,
    visual_mass_quantile=0.5,
    fiou_weight=2.0,
    top_k=10,
    invalid_gt_policy="exclude",
)
