
## 2026-07-20T17:15:05+08:00 · experiment_created
- run: -
- message: Agent 创建实验初稿 E-003 · IPLoc-ID identification-only F1 与 localization correctness 联合评测审计

## 2026-07-20T17:16:20+08:00 · run_created
- run: R-010
- message: Agent 创建 R-010 · E003-R-004b-joint-f1-iou-local-lasot-n140-t128

## 2026-07-20T17:16:20+08:00 · run_update
- run: R-010
- message: 同步已完成的 Joint F1 主评测；保留非官方 split 与结论边界。

## 2026-07-20T17:16:20+08:00 · run_created
- run: R-011
- message: Agent 创建 R-011 · E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20

## 2026-07-20T17:16:20+08:00 · run_update
- run: R-011
- message: 同步 R-005e，并按日志 traceback 登记为 failed 而非 completed。

## 2026-07-20T17:17:11+08:00 · run_created
- run: R-014
- message: Agent 创建 R-014 · E003-R-001-data-rehydrate-local-lasot-n140

## 2026-07-20T17:17:11+08:00 · run_update
- run: R-014
- message: 同步 canonical run E003-R-001-data-rehydrate-local-lasot-n140。

## 2026-07-20T17:17:11+08:00 · run_created
- run: R-015
- message: Agent 创建 R-015 · E003-R-002-joint-f1-n140-failed-env

## 2026-07-20T17:17:12+08:00 · run_update
- run: R-015
- message: 同步 canonical run E003-R-002-joint-f1-n140-failed-env。

## 2026-07-20T17:17:12+08:00 · run_created
- run: R-016
- message: Agent 创建 R-016 · E003-R-003-torch-compat-smoke-local-lasot-n1

## 2026-07-20T17:17:12+08:00 · run_update
- run: R-016
- message: 同步 canonical run E003-R-003-torch-compat-smoke-local-lasot-n1。

## 2026-07-20T17:17:12+08:00 · run_created
- run: R-017
- message: Agent 创建 R-017 · E003-R-004-joint-f1-iou-local-lasot-n140

## 2026-07-20T17:17:12+08:00 · run_update
- run: R-017
- message: 同步 canonical run E003-R-004-joint-f1-iou-local-lasot-n140。

## 2026-07-20T17:17:12+08:00 · run_created
- run: R-018
- message: Agent 创建 R-018 · E003-R-005-forced-candidate-verifier-local-lasot-n20

## 2026-07-20T17:17:12+08:00 · run_update
- run: R-018
- message: 同步 canonical run E003-R-005-forced-candidate-verifier-local-lasot-n20。

## 2026-07-20T17:17:12+08:00 · run_created
- run: R-019
- message: Agent 创建 R-019 · E003-R-005b-forced-candidate-verifier-local-lasot-n20

## 2026-07-20T17:17:12+08:00 · run_update
- run: R-019
- message: 同步 canonical run E003-R-005b-forced-candidate-verifier-local-lasot-n20。

## 2026-07-20T17:17:12+08:00 · run_created
- run: R-020
- message: Agent 创建 R-020 · E003-R-005c-forced-candidate-verifier-local-lasot-n20

## 2026-07-20T17:17:12+08:00 · run_update
- run: R-020
- message: 同步 canonical run E003-R-005c-forced-candidate-verifier-local-lasot-n20。

## 2026-07-20T17:17:12+08:00 · run_created
- run: R-021
- message: Agent 创建 R-021 · E003-R-005d-forced-candidate-verifier-local-lasot-n20

## 2026-07-20T17:17:12+08:00 · run_update
- run: R-021
- message: 同步 canonical run E003-R-005d-forced-candidate-verifier-local-lasot-n20。

## 2026-07-20T17:17:34+08:00 · registry_sync
- run: -
- message: E-003 已创建并同步 canonical run chain R-001 至 R-005e。

工具自动ID映射：R-014→E003-R-001，R-015→E003-R-002，R-016→E003-R-003，R-017→E003-R-004，R-010→E003-R-004b，R-018→E003-R-005，R-019→E003-R-005b，R-020→E003-R-005c，R-021→E003-R-005d，R-011→E003-R-005e。canonical ID保存在variant/notes；failed/aborted/smoke/completed状态均保留。

## 2026-07-20T17:35:55+08:00 · run_rekey
- run: E003-R-001-data-rehydrate-local-lasot-n140
- message: Run registry 已从 R-014 迁移为 canonical ID E003-R-001-data-rehydrate-local-lasot-n140

legacy_registry_id=R-014

## 2026-07-20T17:35:55+08:00 · run_rekey
- run: E003-R-002-joint-f1-n140-failed-env
- message: Run registry 已从 R-015 迁移为 canonical ID E003-R-002-joint-f1-n140-failed-env

legacy_registry_id=R-015

## 2026-07-20T17:35:55+08:00 · run_rekey
- run: E003-R-003-torch-compat-smoke-local-lasot-n1
- message: Run registry 已从 R-016 迁移为 canonical ID E003-R-003-torch-compat-smoke-local-lasot-n1

legacy_registry_id=R-016

## 2026-07-20T17:35:56+08:00 · run_rekey
- run: E003-R-004-joint-f1-iou-local-lasot-n140
- message: Run registry 已从 R-017 迁移为 canonical ID E003-R-004-joint-f1-iou-local-lasot-n140

legacy_registry_id=R-017

## 2026-07-20T17:35:56+08:00 · run_rekey
- run: E003-R-004b-joint-f1-iou-local-lasot-n140-t128
- message: Run registry 已从 R-010 迁移为 canonical ID E003-R-004b-joint-f1-iou-local-lasot-n140-t128

legacy_registry_id=R-010

## 2026-07-20T17:35:56+08:00 · run_rekey
- run: E003-R-005-forced-candidate-verifier-local-lasot-n20
- message: Run registry 已从 R-018 迁移为 canonical ID E003-R-005-forced-candidate-verifier-local-lasot-n20

legacy_registry_id=R-018

## 2026-07-20T17:35:56+08:00 · run_rekey
- run: E003-R-005b-forced-candidate-verifier-local-lasot-n20
- message: Run registry 已从 R-019 迁移为 canonical ID E003-R-005b-forced-candidate-verifier-local-lasot-n20

legacy_registry_id=R-019

## 2026-07-20T17:35:56+08:00 · run_rekey
- run: E003-R-005c-forced-candidate-verifier-local-lasot-n20
- message: Run registry 已从 R-020 迁移为 canonical ID E003-R-005c-forced-candidate-verifier-local-lasot-n20

legacy_registry_id=R-020

## 2026-07-20T17:35:56+08:00 · run_rekey
- run: E003-R-005d-forced-candidate-verifier-local-lasot-n20
- message: Run registry 已从 R-021 迁移为 canonical ID E003-R-005d-forced-candidate-verifier-local-lasot-n20

legacy_registry_id=R-021

## 2026-07-20T17:35:56+08:00 · run_rekey
- run: E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20
- message: Run registry 已从 R-011 迁移为 canonical ID E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20

legacy_registry_id=R-011

## 2026-07-20T17:43:37+08:00 · run_update
- run: E003-R-004b-joint-f1-iou-local-lasot-n140-t128
- message: 补全E003主run的成立依据、数据身份、指标公式、完整性gate和论文级claim边界。

## 2026-07-20T17:43:37+08:00 · run_update
- run: E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20
- message: 补全R-005e的candidate定义、logit metric、role-specific gate和failed结论边界。

## 2026-07-20T17:44:19+08:00 · run_update
- run: E003-R-004b-joint-f1-iou-local-lasot-n140-t128
- message: 验证工具更新不会覆盖result.md详细审计正文。

## 2026-07-20T17:45:33+08:00 · run_update
- run: E003-R-004b-joint-f1-iou-local-lasot-n140-t128
- message: 再次验证result详细审计正文保留。

## 2026-07-20T17:46:03+08:00 · run_update
- run: E003-R-001-data-rehydrate-local-lasot-n140
- message: 补全数据构造与非官方split边界。

## 2026-07-20T17:46:03+08:00 · run_update
- run: E003-R-002-joint-f1-n140-failed-env
- message: 补全failed-env no-silent-zero边界。

## 2026-07-20T17:46:03+08:00 · run_update
- run: E003-R-003-torch-compat-smoke-local-lasot-n1
- message: 补全compat smoke的必要性与结论边界。

## 2026-07-20T17:46:03+08:00 · run_update
- run: E003-R-004-joint-f1-iou-local-lasot-n140
- message: 补全截断run的gate与superseded边界。

## 2026-07-20T17:46:51+08:00 · run_update
- run: E003-R-005-forced-candidate-verifier-local-lasot-n20
- message: 补全forced-candidate失败链的详细审计字段。

## 2026-07-20T17:46:51+08:00 · run_update
- run: E003-R-005b-forced-candidate-verifier-local-lasot-n20
- message: 补全forced-candidate失败链的详细审计字段。

## 2026-07-20T17:46:51+08:00 · run_update
- run: E003-R-005c-forced-candidate-verifier-local-lasot-n20
- message: 补全forced-candidate失败链的详细审计字段。

## 2026-07-20T17:46:51+08:00 · run_update
- run: E003-R-005d-forced-candidate-verifier-local-lasot-n20
- message: 补全forced-candidate失败链的详细审计字段。

## 2026-07-21T01:01:17+08:00 · run_created
- run: E003-R-006-rejection-linked-bbox-audit-n140
- message: Agent 创建 canonical Run E003-R-006-rejection-linked-bbox-audit-n140 · E003-R-006-rejection-linked-bbox-audit-n140

## 2026-07-21T01:02:39+08:00 · run_update
- run: E003-R-006-rejection-linked-bbox-audit-n140
- message: 保留attempt-001失败并以raw floating bbox修复IoU复算。

## 2026-07-21T01:04:11+08:00 · run_update
- run: E003-R-006-rejection-linked-bbox-audit-n140
- message: attempt-003采用阈值归属一致性gate，保留前两次失败。

## 2026-07-21T01:07:44+08:00 · run_update
- run: E003-R-006-rejection-linked-bbox-audit-n140
- message: R-006完成：rejection-linked bbox geometry主假设未获支持；登记反证、negative candidate辅助结果和结论边界。

## 2026-07-21T01:10:38+08:00 · result_audit
- run: E003-R-006-rejection-linked-bbox-audit-n140
- message: R-006 completed；paired rejected bbox geometry hypothesis not supported

IoU<0.1 TP n=35：negPred paired-control RMSE delta=+0.0353,p_lower=0.918；negGT delta=+0.0152,p_lower=0.664。83/140 negative candidate IoU>=0.5，82个最终No。attempt-001/002失败保留；结论仅限跨图像normalized geometry。

## 2026-07-21T12:02:42+08:00 · run_created
- run: E003-R-010-natural-same-image-instance-binding-logit-pilot-n7
- message: Agent 创建 canonical Run E003-R-010-natural-same-image-instance-binding-logit-pilot-n7 · E003-R-010-natural-same-image-instance-binding-logit-pilot-n7

## 2026-07-21T12:05:32+08:00 · run_update
- run: E003-R-010-natural-same-image-instance-binding-logit-pilot-n7
- message: 启动R-010 natural same-image binding logit pilot。

## 2026-07-21T12:15:30+08:00 · run_update
- run: E003-R-010-natural-same-image-instance-binding-logit-pilot-n7
- message: R-010设计与n7 selection已完成，但完整Qwen3-VL snapshot缺失，0 records，标记blocked。

## 2026-07-21T13:02:31+08:00 · run_update
- run: E003-R-010-natural-same-image-instance-binding-logit-pilot-n7
- message: R-010完成但natural-prefix replay gate失败；不下candidate-binding结论，并发现R-005e token boundary问题。

## 2026-07-21T13:14:44+08:00 · run_created
- run: E003-R-011-self-replayed-same-image-binding-logit-pilot-n7
- message: Agent 创建 canonical Run E003-R-011-self-replayed-same-image-binding-logit-pilot-n7 · E003-R-011-self-replayed-same-image-binding-logit-pilot-n7

## 2026-07-21T13:16:36+08:00 · run_update
- run: E003-R-011-self-replayed-same-image-binding-logit-pilot-n7
- message: R-011已在tmux e003_r011启动。

## 2026-07-21T13:40:20+08:00 · run_update
- run: E003-R-011-self-replayed-same-image-binding-logit-pilot-n7
- message: R-011 attempt-001实现失败且设计废弃；0 scientific records，不重试。

## 2026-07-21T14:53:58+08:00 · run_update
- run: E003-R-004b-joint-f1-iou-local-lasot-n140-t128
- message: 补录Identification错误率、positive mIoU、条件mIoU、Joint F1/失败率及低IoU分层；明确7/35只为视觉初筛。

## 2026-07-21T14:55:54+08:00 · run_update
- run: E003-R-006-rejection-linked-bbox-audit-n140
- message: 补录低IoU比例、negative candidate mIoU/rejection、7/35视觉初筛边界和support+query可视化入口。

## 2026-07-21T14:56:27+08:00 · run_update
- run: E003-R-006-rejection-linked-bbox-audit-n140
- message: 修正并写入R-006结构化详细metrics；前一update的空metrics已恢复。

## 2026-07-21T16:24:31+08:00 · run_created
- run: E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140
- message: Agent 创建 canonical Run E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140 · E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140

## 2026-07-21T16:28:39+08:00 · run_update
- run: E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140
- message: 完成IoU threshold curve与10k sample-clustered bootstrap并归档；不扩充数据集。

## 2026-07-21T16:28:58+08:00 · run_update
- run: E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140
- message: 修正写入R-007结构化metrics；前一update仅summary成功、metrics空值现已恢复。
