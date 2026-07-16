# R-010-qwen3vl-object-token-shuffle-n50-full-vs-center-vis

- 状态：completed
- 性质：scaled visual-token order probe + destructive control
- 远端目录：`/home/featurize/work/mechanism/explog/E-002/runs/R-010-qwen3vl-object-token-shuffle-n50-full-vs-center-vis/`
- 目的：把 n=10 的 object-token shuffle 扩到 n=50，并比较 bbox_full、center50、center25。
- 数据：LaSOT hard local manifest，50 positive + 50 same-class negative；max_side=640。
- 模型/层级：Qwen3-VL-8B-Instruct + IPLoc-ID LoRA；修改 post-merge `pooler_output`，在 `masked_scatter` 前。
- 映射：`image_grid_thw` 经 merger 得到 `h//2 × w//2` 网格；bbox 与 cell 任意 overlap 即选中；LaSOT bbox 是 mask proxy。
- 干预：选中 token values 内 permutation，位置集合不变；object seed=`2000+sample*10+image_idx`；global seed=`20260714`。
- 结果：baseline F1=0.925/FPR=0.14；full=0.906/0.16；center50=0.913/0.12；center25=0.932/0.10；global full-visual shuffle=0.667/1.00。
- Token-scale 审计：merged cell median≈32.0×32.7 px；bbox_full selected median=9，70/200 image instances ≤4；center25 median=2，56/200 ≤1。
- 支持：object-footprint order shuffle 没有稳定造成大幅退化，而全局视觉流破坏会使 negative rejection 崩溃。
- 不支持：小/中心 footprint 常只有 1–2 tokens，不能据此证明中心顺序不重要。
- 审核：`config/run.md`、`logs/run.log`、`analysis/summary.json`、`analysis/token_scale_diagnostic_live.json`。
