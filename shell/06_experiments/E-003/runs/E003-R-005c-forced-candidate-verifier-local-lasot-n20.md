# E003-R-005c-forced-candidate-verifier-local-lasot-n20

- 状态：aborted_prefix_format
- 性质：forced-candidate prompt-format audit；不是科学结果。
- 远端目录：`/home/featurize/work/mechanism/explog/E-003/runs/E003-R-005c-forced-candidate-verifier-local-lasot-n20/`
- 改动：只接受 continuation 中显式且不歧义的 Yes/No，保存 prefix drift diagnostic。
- 中止原因：把 candidate 作为额外 user turn 只会让模型重新生成 bbox+question；大多数 continuation 不含最终 Yes/No。这个实现没有真正强制 assistant bbox prefix。
- 有效科学输出：无；不得把 unparsed 计 No 或用 bbox fallback 补 Yes。
- 后继：R-005d 把 candidate+question 直接作为 assistant autoregressive prefix。
- 审核入口：`config/run.md`、`logs/run.log`。
