"""Reference 选头：同一梯度候选，最大注意力质量连通域 IoU >= 0.5。"""
selection_spec = dict(
    source_run_dir="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-001-bbox-gradient-halffull",
    output_dir="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/reference-gradient-spatial-iou050-r001-v1",
    gradient_top_m=50, spatial_top_m=10, visual_mass_quantile=0.5,
    fiou_weight=2.0, top_k=10, invalid_gt_policy="exclude",
    min_component_iou=0.5,
    gradient_records_path="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/reference-gradient-gated-spatial-frequency-r001-v1/records.json",
    gradient_records_sha256="5396b7692789ad69a25a7e327e977629509bae0c1fefaa5466b64040f1b70e65",
)
