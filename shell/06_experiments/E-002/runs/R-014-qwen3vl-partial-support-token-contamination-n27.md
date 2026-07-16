# R-014-qwen3vl-partial-support-token-contamination-n27

- 状态：completed
- 性质：partial support-token contamination dose probe
- 远端目录：`/home/featurize/work/mechanism/explog/E-002/runs/R-014-qwen3vl-partial-support-token-contamination-n27/`
- 目的：控制 R-012 repeated stamping，主要用 unique/no-repeat donor tokens 做分剂量污染。
- 数据：large/rich n=27 balanced。
- 干预：support object token→negative query object slots；p25/p50/p75/p100；no-repeat capped by donor count，另设 p100 repeat；query-self shuffle control。
- 结果（F1/FPR）：baseline .931/.148；p25 .885/.259；p50 .885/.259；p75 .831/.407；p100 no-repeat .818/.444；p100 repeat .818/.444；query shuffle .981/0。
- 支持：无需重复 stamping，support-like token contamination 仍增加 same-class FP，并呈大致剂量趋势。
- 局限：该版 destination 选择不是 center-out；不同 run baseline/随机路径有波动；pooler-only。
- 审核：`config/run.md`、`logs/run.log`、`analysis/summary.json`、`visualizations/token_mix_effects_with_support/`。
