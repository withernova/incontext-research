# R-014b-qwen3vl-partial-support-token-contamination-centerout-n27

- 状态：completed
- 性质：deterministic center-out contamination + box response analysis
- 远端目录：`/home/featurize/work/mechanism/explog/E-002/runs/R-014b-qwen3vl-partial-support-token-contamination-centerout-n27/`
- 目的：把 destination 明确定义为距 query bbox-footprint 中心由近到远的 deterministic prefix。
- 数据/模型：large/rich n=27 balanced；Qwen3-VL/IPLoc-ID post-merge pooler tokens。
- 结果（F1/FPR）：baseline .982/.037；p25 .931/.148；p50 .871/.296；p75 .871/.296；p100 no-repeat .857/.333；p100 repeat .818/.444；query shuffle .982/.037。
- Box size（all negatives，intervention/base mean area ratio）：p25 1.142；p50 1.319；p75 1.419；p100 no-repeat 1.516；repeat≈1.440；shuffle≈1.095。
- Box-follow proxy（new FP）：p25 ΔIoU +.227/Δdist −107.2；p50 +.039/−41.4；p75 +.131/−23.0；p100 no-repeat +.145/−25.7。
- 支持：center-out support contamination 提高 FP 并倾向扩大框。
- 局限：LaSOT bbox proxy；不是每个 FP 都扩大；污染区域 box-follow 是 token-grid proxy。
- 审核：`analysis/summary.json`、`analysis/r014b_box_size_change.*`、`analysis/r014b_box_follow_contamination.*`、两个 visualization sets。
