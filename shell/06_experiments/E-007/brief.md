# E-007 · Experiment Brief

## 用户提出的目标
在原始IPLoc-ID/POIL任务中，对真正参与A@V计算的query-stage Q→R attention进行受控移植、破坏与恢复，检验prompt-stage reference-grounding空间分布能否改善或救回自然bbox localization与Joint F1，并区分reference总预算、reference内部空间shape和任意集中化效应。

## 用户约束
保持原IPLoc-ID LoRA、原始prompt、max_side=640和自然输出协议；primary shape transplant严格保持每个target row原Q→R总mass，只改变reference span内分布；必须有identity、R180/permutation、uniform-reference-bbox、mismatched-source和Q→R knockout controls；先工程gate/teacher replay，后自然生成；attention intervention必须发生在softmax后A@V前；sequence-level split/bootstrap；不把改善解释为identity理解或共享因果电路。

## 来源
- kind: causal_intervention
- source_ref: shell/06_experiments/E-005/head_role_registry.md; shell/06_experiments/E-005/dual_gpu_640_core_results.md; shell/06_experiments/E-006/result.md; shell/06_experiments/E-004/runs/E004-R-010-single-head-activation-patching-correctness-smoke.md
- evidence_refs: E006-R-006 row alignment GATE_PASS; E006-R-014c reference-target attention response; E003-R-004b Joint F1 audit; E005 historical G→R and Q→R head sets
- claim_refs: Q-004; attention-derived reference-target use remains observational until behavior-changing intervention
- workspace_id: W-01
