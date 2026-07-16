# R-014c-qwen3vl-sampled-centerout-support-contamination-n27

- 状态：completed_with_geometry_caveat
- 性质：sampled-intensity center-out contamination
- 远端目录：`/home/featurize/work/mechanism/explog/E-002/runs/R-014c-qwen3vl-sampled-centerout-support-contamination-n27/`
- 目的：让 p25/p50/p75/p100 表示在相应比例 bin 内采样替换数量，而非完整 deterministic prefix。
- 数据：large/rich n=27 balanced；seed 和 sampled metadata 见 summary。
- 结果（F1/FPR）：baseline .964/.074；p25 .900/.222；p50 .885/.259；p75 .885/.259；p100 no-repeat .818/.444；p100 repeat .871/.296；query shuffle .964/.074。
- Box area ratio（all negatives）：p25 1.108；p50 1.303；p75 1.480；p100 no-repeat 1.634；repeat 1.405；shuffle 1.149。
- Approx box-follow（all negatives）：p25 ΔIoU +.017/Δdist −9.7；p50 +.053/−19.1；p75 +.102/−21.4；p100 +.128/−26.7。
- 可支持：decision/FPR 与 box-area dose response。
- 禁止正式引用：exact box-follow 与 posthoc `actual_fraction`；run 未保存完整 `src_indices/dst_indices/pairs_list`，几何是 center-out reconstruction，且旧 actual_fraction 可>1。
- 审核：`analysis/summary.json`、`analysis/r014c_box_metrics.*`、`visualizations/token_mix_sampled_centerout_*`。
