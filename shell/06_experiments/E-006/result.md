# E-006 · 实验结果

## 运行汇总（survey-tool 管理）
| Run | Variant | Seed | 状态 | 指标 |
|---|---|---:|---|---|
| E006-R-005-simple-top50-support-components-positive-extremes-n111-640 | fixed top50 support per-head GtoR QtoR QtoQ | 20260728 | completed_passed_integrity_inference_only | {"n_error":35,"n_correct":76,"forwards":111,"figures":111,"head_maps":1221,"support_mass":0.5,"connectivity":4,"grid_tokens_median":220,"grid_tokens_min":84,"grid_tokens_max":300,"gtr_all3_hit_error":0.9714285714,"gtr_all3_hit_correct":1.0,"qtr_mean_hit_heads_error":2.5142857143,"qtr_mean_hit_heads_correct":3.2236842105,"qtr_mean_hit_heads_diff":0.7093984962,"qtr_mean_hit_heads_ci95":[0.0857048872,1.3289473684],"qtr_all4_hit_error":0.4571428571,"qtr_all4_hit_correct":0.7105263158,"qtr_largest_mean_heads_error":1.7428571429,"qtr_largest_mean_heads_correct":2.5131578947,"qtr_majority_any_error":0.0285714286,"qtr_majority_any_correct":0.0657894737,"qtq_mean_hit_heads_error":1.0,"qtq_mean_hit_heads_correct":4.0} |
| E006-R-006-exact-last-token-bbox-row-alignment-gate-n10-640 | exact last-token vs first-generate-step vs bbox-pminus1 row gate | 20260728 | planned |  |
| E006-R-007-refcoco-coco-frozen-manifest-integrity-gate-n1220 | RefCOCO primary and optional filtered COCO-val proxy manifest gate | 20260724 | completed | {"gate":"GATE_STOP","read_only":true,"network_downloads":0,"files_extracted":0,"blockers":["MISSING_REFCOCO_METADATA","MISSING_COCO2014_IMAGES"]} |
| E006-R-008-upstream-llava-last-token-refcoco-positive-control-n1000-200 | immutable upstream LocalizationHeads LLaVA exact last-token positive control | 20260724 | cancelled |  |
| E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200 | Qwen RefCOCO exact-last-token first-step bbox-row parity | 20260728 | completed | {"exit_code":0,"gate":"GATE_PASS","n_pilot":20,"n_discovery":1000,"n_confirmation":200,"n_failures":0,"frozen_heads":["L25H08","L27H31","L29H01","L09H14","L26H29"],"fractional_mass":0.0455898327,"enrichment":0.2227863209,"s50":0.985,"pointing":0.07,"allhead_percentile":0.0701128472} |
| E006-R-010-outcome-stratified-allhead-discovery-sequence-split | correct-error separate all-head discovery for last-token and bbox rows | 20260728 | planned |  |
| E006-R-011-outcome-headsets-fresh-cross-evaluation | 2x2 correct-discovered error-discovered fresh sequence confirmation | 20260728 | planned |  |
| E006-R-012-reference-query-transform-geometric-separability-gate | identity HFlip VFlip R180 reference-only query-only both offline geometry | 20260728 | planned |  |
| E006-R-013-natural-behavior-transform-gate | natural Yes bbox under REF-only QUERY-only BOTH H V R180 | 20260728 | planned |  |
| E006-R-014-qtor-reference-vs-query-coordinate-equivariance | QtoR reference tracking versus query-coordinate copy transform audit | 20260728 | planned |  |
| E006-R-015-reference-image-vs-prompt-bbox-mismatch-diagnostic | reference visual transform versus explicit bbox-coordinate mismatch | 20260728 | planned |  |
| E006-R-010b-outcome-stratified-reference-query-allhead-discovery-viz | correct error balanced-mix by reference-query role all-head discovery and visualization | 20260728 | planned |  |
| E006-R-014b-r005-sample-aligned-three-row-equivariance-visualization | r005-sample-aligned-three-row-equivariance-visualization | 20260728 | completed | {"exit_code":0,"gate":"GATE_PASS","n_design":84,"n_ok":84,"n_failed":0,"main_figures":36,"appendix_figures":84,"parse_failed":0,"current_behavior":{"correct":36,"partial":13,"error":31,"rejected":4},"ref_only_sequence_mean_median":0.0146841432,"ref_only_ci95":[-0.0215546022,0.0607504917],"ref_only_positive":8,"query_only_fixed_R0_preference_median":0.0306631853,"query_only_ci95":[-0.0150321908,0.0783100553],"query_only_positive":7} |
| E006-R-016-icol-last-token-row-stage-falsification | icol-last-token-row-stage-falsification | 20260728 | planned |  |
| E006-R-007b-refcoco-train2014-recovery-integrity-gate-n1220 | refcoco-train2014-recovery-integrity-gate-n1220 | 20260724 | completed | {"gate":"GATE_PASS","coco_jpg_count":82783,"metadata_rows":42404,"selected":1220,"decode_valid":1220,"decode_failed":0,"split_counts":{"pilot":20,"discovery":1000,"confirmation":200},"split_image_overlap":0} |
| E006-R-014c-prediction-projection-expanded-equivariance-audit | prediction-projection-expanded-equivariance-audit | 20260728 | completed | {"exit_code":0,"n_design":777,"n_ok":776,"n_failed":1,"parse_failed":1,"main_figures":332,"overview_figures":110,"appendix_figures":776,"ref_only_sequence_median":0.022839472025801624,"ref_only_ci95":[0.017241721963701252,0.033404342560741214],"query_prediction_projection_sequence_median":-0.0006159337667415657,"query_prediction_projection_ci95":[-0.01807702570087052,0.0234938389689921]} |
| E006-R-009b-refcoco-natural-bbox-token-head-transfer-n1000-200 | refcoco-natural-bbox-token-head-transfer-n1000-200 | 20260728 | completed | {"gate":"GATE_STOP","stage":"pilot","n_pilot":20,"parse_valid":0,"parse_rate":0.0,"discovery_started":false,"heads_selected":false} |
| E006-R-009c-refcoco-qwen-normalized-natural-bbox-token-head-transfer-n1000-200 | refcoco-qwen-normalized-natural-bbox-token-head-transfer-n1000-200 | 20260728 | completed | {"exit_code":0,"gate":"GATE_PASS","pilot_parse":20,"pilot_exact_replay":20,"n_discovery":1000,"n_confirmation":200,"frozen_top5":["L04H29","L14H04","L09H14","L23H30","L22H04"],"gt_mass":0.3007064193,"enrichment":2.0052698536,"pointing":0.423,"allhead_percentile":0.6938932292,"natural_miou":0.8657095573,"r010_correct_top10_overlap":8,"r010_error_top10_overlap":7,"r010_mix_top10_overlap":8,"main4_top10_overlap":0,"n_visualizations":20} |
| E006-R-009d-refcoco-original-prompt-natural-output-row-audit-n20-1000-200 | refcoco-original-prompt-natural-output-row-audit-n20-1000-200 | 20260728 | completed | {"exit_code":0,"gate":"GATE_PASS","pilot_parse":20,"pilot_exact_replay":20,"n_discovery_valid":999,"n_discovery_failed":1,"n_confirmation_valid":200,"n_confirmation_failed":0,"frozen_top5":["L04H29","L14H04","L09H14","L22H04","L23H30"],"gt_mass":0.3002157836,"enrichment":1.9921328703,"pointing":0.417,"allhead_percentile":0.6873741319,"natural_miou":0.8621494281,"r010_correct_top10_overlap":8,"r010_error_top10_overlap":7,"r010_mix_top10_overlap":8,"main4_top10_overlap":0} |
| E006-R-009e-refcoco-specific-gt-aligned-head-discovery-viz-fresh200 | refcoco-specific-gt-aligned-head-discovery-viz-fresh200 | 20260728 | planned |  |
| E006-R-017-refcoco-synthetic-paired-view-icol-format-head-transfer | refcoco-synthetic-paired-view-icol-format-head-transfer | 20260728 | planned |  |
| E006-R-017b-refcoco-synthetic-icol-format-within-lora-head-transfer | refcoco-synthetic-icol-format-within-lora-head-transfer | 20260728 | completed | {"gate":"GATE_STOP_GEOMETRY_RETENTION_LT90","pilot_valid":13,"pilot_n":20,"discovery_valid":607,"discovery_n":1000,"confirmation_valid":121,"confirmation_n":200,"model_inference_started":false,"lora_loaded":false,"natural_generations":0} |

## 结果摘要（survey-tool 管理）
（待登记）

## 对 Claims 的影响（survey-tool 管理）
（待人工判断；不会自动提升 Claim）

## 局限性（survey-tool 管理）
（待补充）

## 详细审计正文（canonical）
### Top50 的关键定义

这里的50%是目标 `image span` 内重新归一化后的**条件attention质量**。它既不是选择数量排名前50%的tokens，也不是说该head对完整上下文有50%的attention落在目标图像。

令目标图像内归一化attention为 `p_i`，按 `p_(1)>=...>=p_(N)` 排序：

```text
k* = min{k: sum_{j=1..k} p_(j) >= .5}
S50 = 前k*个tokens
```

`sum(S50)` 通常略大于 `.5`，因为最后一个离散token会跨过阈值。

本run merged-token数 median=220、range=84–300，最常见grid为11×20（94/111）。Q→R的 `k*`：

| Head | Error median [Q1,Q3] | Correct median [Q1,Q3] |
|---|---:|---:|
| L18H15 | 9 `[4,11.5]` | 12.5 `[6.75,16]` |
| L19H03 | 6 `[2,20]` | 17 `[5.75,27]` |
| L22H00 | 35 `[17,42]` | 38 `[31,43]` |
| L20H08 | 6 `[2,15.5]` | 12 `[3,20]` |

因此correct中的Q→R support通常更大而非更小。可支持的是“更多heads的support/最大component触及GT”，不支持“correct attention更集中”。

### 组会与完整审计入口

完整公式、伪代码、220-token示例、H/M/C/CG/L区别、逐head统计、展示措辞和不可支持结论：

```text
shell/06_experiments/E-006/top50_support_group_meeting_guide.md
```

Canonical run记录：

```text
shell/06_experiments/E-006/runs/
E006-R-005-simple-top50-support-components-positive-extremes-n111-640.md
```

原始/派生统计：

```text
remote analysis/summary.json
remote analysis/poststats.json
remote analysis/support_selection_details.json
local shell/06_experiments/E-006/visualizations/R-005/
```
