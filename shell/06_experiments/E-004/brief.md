# E-004 · Experiment Brief

## 用户提出的目标
识别对 Yes/No margin 有因果作用的 Qwen3-VL attention heads，并检验其是否随 reference identity 读取正确的 query-instance tokens，以及 localization 与 identification circuits 是否解耦。

## 用户约束
先通过 Reference A/B × Candidate A/B behavioral gate；按因果效应而非 attention map 选 heads；synthetic pilot 不外推自然同图双实例；覆盖 pooler/deepstack 路径限制。

## 来源
- kind: mechanism_causal_analysis
- source_ref: Q-001
- evidence_refs: shell/01_questions/Q-001.md
- claim_refs: 
- workspace_id: W-01
