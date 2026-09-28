"""R-004：先验证 Query/Reference visual contribution 计算，再允许选头。"""

# 所有实验值都在 config 中冻结；Shell 不接收 checkpoint、数据或阈值位置参数。
launch = dict(action="analyze", nproc_per_node=1)

work_dir = (
    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/"
    "R-004-contribution-calculation-check"
)

analysis = dict(
    run_id="R-004-contribution-calculation-check",
    entrypoint="iploc_szy.head_screening.dual_role_metrics:run_r004_scaffold",
    metric_contract=dict(
        schema="e012.dual-role-head-metrics/v1",
        sha256="bab83a1f801b158f7fbe7a027760e1e937185c439b778107e83f6ece1e3c5f06",
    ),
    # None 表示尚未经过 Run 审核冻结。正式 worker 必须先调用
    # validate_analysis_contract；缺任何值都拒绝运行，禁止隐式默认。
    required_parameters=dict(
        input_manifest=None,
        input_manifest_sha256=None,
        checkpoint_path=None,
        sample_indices=None,
        layer_head_regions=None,
        finite_difference_epsilons=None,
        algebra_atol=None,
        algebra_rtol=None,
        finite_difference_relative_error_max=None,
        finite_difference_sign_agreement_min=None,
        empty_hook_atol=None,
        empty_hook_rtol=None,
        denominator_epsilon=None,
    ),
)
