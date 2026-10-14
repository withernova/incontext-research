"""E-012：自动解析已指定 R-001 的 absolute Top-10，做整头置零先导消融。"""
run_spec = dict(
    source_run_id="E-012/R-001",
    ranking_metric="bbox_grad_abs_contrib_mean",
    # 仅从这个用户指定的目录读取 frozen_input.json 与 summary.json；不搜索其他 Run。
    source_run_dir="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-001-bbox-gradient-halffull",
    # 新目录必须不存在。此名称仅描述产物目录，不注册/修改治理 Run ID。
    output_dir="/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/top10-whole-head-ablation-r001-top10-v2",
    # 先导固定 60 条：从 R-001 的 690 个 frozen selected_indices 中按原索引顺序选取。
    # 通过预检后不得依结果调整；想扩大规模时请改为明确配额并使用新 output_dir。
    samples_per_dataset=dict(LaSOT=20, GOT10k=20, TAO=20),
    num_layers=36,
    num_heads=32,
    coordinate_scale=1000,
    random_seeds=[20260912, 20260913, 20260914],
    max_new_tokens=128,
    max_sequence_tokens=2048,
    # 相同 eager 路径下的空 hook 检查应逐元素精确相等。
    parity_atol=0.0,
    parity_rtol=0.0,
)
