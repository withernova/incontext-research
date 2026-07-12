# 声明注册表（Claims registry，kernel 真相层）

状态生命周期：
- draft -> supported -> validated   （晋升为 validated 需满足：R2 裁决 PASS + 人工 approved + ≥1 个有 content_hash 的来源）
- draft -> contradicted / contradicted_by_prior / partial / inference_only
- inference_only 在综合报告中**只能作为标注过的推测**出现，绝不能当作事实。

每个声明的字段：
- text、status、confidence (high|med|low)、sources ([[citekey]] §位置)、contradicting_evidence、
  r2_verdict (pending|PASS|REJECT|NEEDS_MORE_EVIDENCE)、human_verdict (pending|approved|rejected)、
  created、rationale

## C01
- text: 测试claim
- status: draft
- confidence: 
- sources: [[focusfor2026]] §3.2
- contradicting_evidence: 
- r2_verdict: pending
- human_verdict: pending
- citekey: focusfor2026
- created: 2026-07-09T15:45:08
- rationale:

## C02
- text: 测试引用claim
- status: draft
- confidence: 
- sources: [[detpoinc2026]] §3
- contradicting_evidence: 
- r2_verdict: pending
- human_verdict: pending
- citekey: 
- source_type: seven_question
- source_ref: detpoinc2026:q3
- created: 2026-07-12T09:00:48
- rationale: 
