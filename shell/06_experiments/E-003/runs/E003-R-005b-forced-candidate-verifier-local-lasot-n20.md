# E003-R-005b-forced-candidate-verifier-local-lasot-n20

- 状态：aborted_parser_audit
- 性质：prefix-conditioned pilot 的实现审计，不是科学结果。
- 远端目录：`/home/featurize/work/mechanism/explog/E-003/runs/E003-R-005b-forced-candidate-verifier-local-lasot-n20/`
- 修复：相对 R-005 增加 PYTHONPATH、本地 offline snapshot、Torch compatibility 与 E003-R-004b baseline path。
- 中止原因：仓库 `PN_interpreter` 在没有显式 Yes/No 时，会用任意非零生成 bbox fallback 标为 positive；因此大量输出被错误记为 positive，不能用于 forced verifier。
- 有效科学输出：无；不得引用中止前的 Yes rate。
- 后继：R-005c 改为显式 Yes/No-only parser。
- 审核入口：`config/run.md`、`logs/run.log`。
