# R-011-qwen3vl-large-rich-object-shuffle-stratified-n27

- 状态：completed
- 性质：large/token-rich stratified order probe
- 远端目录：`/home/featurize/work/mechanism/explog/E-002/runs/R-011-qwen3vl-large-rich-object-shuffle-stratified-n27/`
- 目的：降低小目标 token 数过少的混杂，在 large/rich n=27 子集复核 object-order sensitivity。
- 数据：`LASOT_large_refpos16_rich_vs_simple_1shot_T2_n27.json`，27 positive + 27 negative。
- 模型/干预/映射：同 R-010；bbox approximation、post-merge pooler path、any-overlap grid selection。
- 结果：baseline F1=1.000/FPR=0；full bbox shuffle=0.947/0.111；center50=0.964/0.074；center25=0.929/0.111；global full-visual shuffle=0.667/1.000。
- 支持：token-rich subset 上 object-order shuffle 有有限影响，但远弱于 global destructive shuffle。
- 局限：n=27、自动 rich/simple proxy、pooler-only、非 segmentation mask。
- 审核：`config/run.md`、`logs/run.log`、`analysis/summary.json`、`analysis/r011_rich_group_summary.json`。
