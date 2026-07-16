# R-015-qwen3vl-support-vs-query-object-shuffle-n27

- 状态：completed
- 性质：support/query scope decomposition
- 远端目录：`/home/featurize/work/mechanism/explog/E-002/runs/R-015-qwen3vl-support-vs-query-object-shuffle-n27/`
- 目的：分离 support-only、query-only 与 support+query bbox object-token order shuffle。
- 数据：large/rich n=27 balanced。
- 结果（F1/FPR）：baseline .964/.074；support-only .982/.037；query-only .982/.037；both .982/.037；global full-visual shuffle .667/1.000。
- 支持：当前设置下 object-token order shuffle 未造成稳定退化；global visual structure 被破坏时 negative rejection 崩溃。
- 注意：现有 `full_visual_shuffle` 是 concatenated support+query 全视觉流跨图 permutation，不是 query-only full-image shuffle。
- 局限：单 seed/运行、baseline 有波动、pooler-only、bbox proxy；相同 aggregate 不代表 per-sample 完全相同。
- 审核：`config/run.md`、`logs/run.log`、`analysis/summary.json`、`visualizations/`。
