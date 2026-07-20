# E003-R-005d-forced-candidate-verifier-local-lasot-n20

- 状态：aborted_text_generation_instability
- 性质：assistant-prefix forced-candidate pilot 的 parser/formulation audit；不是主科学结果。
- 远端目录：`/home/featurize/work/mechanism/explog/E-003/runs/E003-R-005d-forced-candidate-verifier-local-lasot-n20/`
- 实现：normalized candidate 和 `Do all these boxes have the same object? ` 被直接追加为 assistant autoregressive prefix。
- 观察：格式开始生成 `Yes/No`，证明 prefix 位置比 R-005c 更接近目标；但出现 `1. Yes. 2. No.`、纯数字等歧义输出，显式 parser 仍有 nonzero unparsed。
- 中止原因：预注册 gate 要求 unparsed=0；继续跑满会浪费 GPU，且不可将歧义文本任意映射为 Yes/No。
- 有效科学输出：无；中止前行为只能用于设计下一版 constrained/logit probe。
- 后继：采用 next-token Yes-vs-No logit margin，避免自由文本 parser；文本 continuation 仅作为辅助。
- 审核入口：`config/run.md`、`logs/run.log`。
