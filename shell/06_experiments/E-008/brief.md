# E-008 · Experiment Brief

## 用户提出的目标
在不进行模型干预的前提下，审计reference-grounding heads在自然query bbox生成p-1 rows上对query与reference视觉token的attention，区分跨角色query localization与reference-only角色分工。

## 用户约束
只复用E003-R-004b positive n140与归档natural responses；Qwen3-VL-8B-Instruct+原IPLoc-ID 1shot LoRA；max_side=640 exact teacher replay；冻结G-heads=L15H13,L16H23,L18H15与L-heads=L18H15,L19H03,L22H00,L20H08；无activation/attention干预；attention-derived、non-causal；不得创建或提升Claim。

## 来源
- kind: observational_mechanism_audit
- source_ref: shell/06_experiments/E-005/head_role_registry.md; shell/06_experiments/E-005/dual_gpu_640_core_results.md; shell/06_experiments/E-005/runs/positive-binding-audit/E005-R-029c-original140-positive-targets-binding-640.md; shell/01_questions/Q-004.md; shell/01_questions/Q-005.md
- evidence_refs: E005-R-016 original-order stage audit; E005-R-029c n140 max_side640 exact replay; E006-R-005 Q→Q main4 support audit
- claim_refs: Q-004; Q-005; observational head-role audit only
- workspace_id: 02
