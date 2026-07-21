# E-004 · 实验结果

## 运行汇总（survey-tool 管理）
| Run | Variant | Seed | 状态 | 指标 |
|---|---|---:|---|---|
| E004-R-000-qwen3vl-head-hook-audit | E004-R-000-qwen3vl-head-hook-audit |  | completed | {"text_layers":36,"query_heads":32,"kv_heads":8,"head_dim":128,"hidden_size":4096,"hook":"self_attn.o_proj forward_pre_hook"} |
| E004-R-001-synthetic-double-instance-behavior-n4 | E004-R-001-synthetic-double-instance-behavior-n4 | 0 | completed_gate_failed | {"conditions":16,"accuracy":0.5625,"quartets":4,"quartets_all_four_correct":0,"matched_minus_mismatched":[0.5625,0.125,0.71875,0.125],"behavioral_gate_passed":false} |
| E004-R-006-qwen3vl-head-hook-correctness-smoke | E004-R-006-qwen3vl-head-hook-correctness-smoke |  | completed_passed |  |
| E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4 | E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4 |  | completed_diagnostic |  |
| E004-R-008-source-base-object-removal-proxy-gate-n4 | E004-R-008-source-base-object-removal-proxy-gate-n4 |  | completed_gate_passed |  |
| E004-R-009-layer-cma-recoverability-proxy-strict-n6 | E004-R-009-layer-cma-recoverability-proxy-strict-n6 |  | completed_gate_passed |  |
| E004-R-010-single-head-activation-patching-correctness-smoke | E004-R-010-single-head-activation-patching-correctness-smoke |  | completed_passed |  |
| E004-R-011-official-lama-code-acquisition | E004-R-011-official-lama-code-acquisition |  | completed_passed |  |

## 结果摘要（survey-tool 管理）
（待登记）

## 对 Claims 的影响（survey-tool 管理）
（待人工判断；不会自动提升 Claim）

## 局限性（survey-tool 管理）
（待补充）

## 详细审计正文（canonical）
这里保存指标定义、证据链、逐层结论边界与审核入口；后续 Run 更新不会覆盖本节。
