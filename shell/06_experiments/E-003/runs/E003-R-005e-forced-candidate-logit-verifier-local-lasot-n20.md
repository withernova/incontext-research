# E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20

- 状态：`failed_post_output_integrity_assertion` / analysis incomplete
- 性质：prefix-conditioned forced-candidate next-token logit verifier pilot。
- 远端目录：`/home/featurize/work/mechanism/explog/E-003/runs/E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20/`
- 目的：避免自由文本和 `PN_interpreter` bbox fallback；在 assistant autoregressive candidate prefix 后，直接比较单-token `Yes` 与 `No` 的 next-token logits。
- 数据：本地 deterministic LaSOT POIL reconstruction 前20 samples；20 positive targets + 20 same-class negative targets；每个 target 6 modes。
- 观测产物：`results/forced_candidate_outputs.json` 实际包含240条；所有 `yes_logit`、`no_logit`、`yes_minus_no_logit`、`yes_pair_probability` 均 finite；每个实际 role/mode 组合恰有20条。
- 失败原因：输出写盘后，脚本完整性 assertion 错误地要求 positive role 也存在 `annotated_distractor` mode；实际 positive 对应 mode 是 `annotated_target`。日志末尾为：`AssertionError: ('positive-image', 'annotated_distractor', 0, 20)`。
- 当前边界：由于存在 traceback 且没有生成正式 analysis summary，本 run 不登记为 completed main result，也不引用初步 margin 作为科学结论。原始240条可以在修复 role-specific integrity gate 后离线重分析，但必须保留本 run 的失败状态；修复版应使用新 run id。
- Probe 限制：这是 `prefix-conditioned verifier probe`，存在 forced assistant-prefix exposure shift；`yes_pair_probability` 仅在两个选定 token 间归一化，不是全词表校准概率。
- 审核入口：
  - config：`config/run.md`
  - log：`logs/run.log`
  - per-record outputs：`results/forced_candidate_outputs.json`
  - analysis：缺失（run 在 post-output assertion 处终止）
  - visualizations：无
