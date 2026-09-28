"""R-005：Reference target-grounded screening 与冻结确认。"""

launch = dict(action="analyze", nproc_per_node=1)

work_dir = (
    "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/"
    "R-005-reference-target-grounded-screening"
)

analysis = dict(
    run_id="R-005-reference-target-grounded-screening",
    entrypoint=(
        "iploc_szy.head_screening.reference_target_screening:run_r005_from_records"
    ),
    # 所有值必须来自审核后冻结的采集与 calibration；None 会 fail closed。
    required_parameters=dict(
        input_records=None,
        input_records_sha256=None,
        tau_c=None,
        tau_a=None,
        tau_d=None,
        qualification_frequency_min=None,
        top_k=None,
        legacy_iou_threshold=None,
    ),
)
