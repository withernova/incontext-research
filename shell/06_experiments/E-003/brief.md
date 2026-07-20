# E-003 · Experiment Brief

## 用户提出的目标
审计 identification-only F1 是否与定位正确性解耦；报告 Joint F1@IoU，并用 prefix-conditioned forced-candidate verifier probe 检验最终判断对 candidate region 的响应。

## 用户约束
使用本地 deterministic LaSOT POIL reconstruction，明确其非官方 split；forced assistant-prefix 存在 exposure shift；失败与中止 run 必须保留且不得作为科学结果。

## 来源
- kind: evaluation_audit
- source_ref: personal2026
- evidence_refs: shell/06_experiments/E-003/result.md
- claim_refs: 
- workspace_id: W-01
