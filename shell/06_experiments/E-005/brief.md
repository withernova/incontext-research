# E-005 · Experiment Brief

## 用户提出的目标
严格参照Localization Heads论文与官方实现，在冻结LVLM中发现少量稳定视觉定位heads，并迁移到Qwen3-VL/IPLoc-ID以比较localization与identification circuits。

## 用户约束
保留官方源码不改；论文与公开代码不一致处显式审计；Qwen适配仅做必要最小修改；raw attention不得表述为因果证据；先复现原生流程再迁移。

## 来源
- kind: attention_mechanism_analysis
- source_ref: localizationheads2025
- evidence_refs: [, "shell/03_evidence/papers/localizationheads2025.md", ]
- claim_refs: 
- workspace_id: 02
