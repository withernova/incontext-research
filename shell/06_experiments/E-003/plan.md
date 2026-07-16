# E-003 · IPLoc-ID identification–localization coupling audit

- status: running
- kind: evaluation_audit / mechanism_diagnostic
- source_ref: personal2026
- created: 2026-07-16

## 假设
H1：在原始 identification F1 较高时，把 positive TP 定义收紧为 `Yes 且 IoU>=τ` 会显著降低 Joint F1。

H2：如果 IPLoc-ID 的 identification component 真正在验证候选区域，那么同一 reference/query 下，将候选框从真实目标改为 distractor、低重叠偏移框或背景框，应系统性降低 Yes rate。

## 指标
- 原始 identification F1：只根据 query positive/negative 与最终 Yes/No。
- Joint F1@IoU=τ：positive 只有 `Yes && IoU>=τ` 才是 TP；否则 FN；negative 仍按 Yes/No 计 FP/TN。
- `mean IoU | identification TP` 与 Yes-positive IoU 分桶。
- Forced-candidate 各条件 Yes rate、同一样本 candidate-conditioned flip rate。

## 数据
本地 LaSOTTesting 确定性重建 POIL manifest；必须明确标注非官方 IPLoc-ID split。正式复现条件允许时再补官方 split。

## 运行安排
- E003-R-001：数据重建与 manifest 校验（由旧 E-002 路径迁移）。
- E003-R-002：失败的首次 Joint F1 环境兼容性运行，仅作失败审计。
- E003-R-003：兼容修复后的 n=1 smoke。
- E003-R-004：Joint F1 n=140，因 `max_new_tokens=80` 截断 Yes/No，于约9/140提前中止。
- E003-R-004b：改为 `max_new_tokens=128` 的 Joint F1 n=140 main diagnostic，已完成。
- E003-R-005：forced-candidate n=20 pilot；通过后决定是否扩展。

## 成功/证伪标准
- H1：比较原始 F1 与各 Joint F1，不预设必须下降多少；同时报告误差构成。
- H2：候选框条件改变时 Yes/No 有系统性响应；若几乎不响应，则支持 verifier-candidate 脱钩的假设。若对目标/背景框清晰区分，则该脱钩假设被削弱。

## 风险
- 本地 split 可能有 sequence/domain shortcut。
- 外部 candidate prefix 与模型自然自回归生成历史不同。
- F1 与 mIoU 量纲不同，禁止直接用数值差做机制推断。
