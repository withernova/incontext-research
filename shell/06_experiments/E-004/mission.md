# Experiment Mission · E-004

## 标题
Reference-conditioned causal token routing in personalized instance verification

## 研究问题
对 Yes/No margin 真正有因果作用的 Qwen3-VL attention heads，是否读取与 reference identity 对应的正确 query-instance tokens；当 reference A↔B 或 candidate A↔B 时，其因果贡献是否同步改变？

## 与 E-002/E-003 的边界
- E-002：视觉 embedding/container/identity-detail interventions。
- E-003：Joint F1 与 prefix-conditioned candidate verifier evaluation audit。
- E-004：LLM 内部 causal heads、token-group routing 与 localization/identification circuit overlap。

## 核心设计
同一双实例 query，构造 `Reference A/B × Candidate A/B` 四条件；teacher-force candidate 与 verifier question，读取 `Yes-No` next-token logit margin。

## 结论边界
synthetic double-panel 只能用于 hook、prompt 和因果设计 sanity；正式 identity-routing 结论要求真实同图双实例、matched token counts、bbox/mask token mapping，并覆盖 Qwen3-VL pooler/deepstack 视觉路径。
