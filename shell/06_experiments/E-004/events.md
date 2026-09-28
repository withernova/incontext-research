# E-004 事件日志

> 本文件只保留单行摘要；完整 details 保存在工具内部的 experiment-events.jsonl 中。
> 需要展开某条事件时运行：`python3 /home/zhengyuesong/Tools/survey-tool/surveyctl.py --project <proj> experiment event-detail <E-ID> <EVENT-ID>`。

- 2026-07-20T17:15:06+08:00 · experiment_created · Agent 创建实验初稿 E-004 · Reference-conditioned causal token routing · run=- · detail=evt-e03a56465af9
- 2026-07-20T17:16:20+08:00 · run_created · Agent 创建 R-012 · E004-R-000-qwen3vl-head-hook-audit · run=R-012 · detail=evt-d81080812d56
- 2026-07-20T17:16:20+08:00 · run_update · 同步Qwen3-VL head-hook模块审计。 · run=R-012 · detail=evt-17de38ba9669
- 2026-07-20T17:16:20+08:00 · run_created · Agent 创建 R-013 · E004-R-001-synthetic-double-instance-behavior-n4 · run=R-013 · detail=evt-7c43e5365bc7
- 2026-07-20T17:16:20+08:00 · run_update · 同步synthetic 2x2 sanity，并明确behavioral gate failed。 · run=R-013 · detail=evt-d0ea61aa98f2
- 2026-07-20T17:17:34+08:00 · registry_sync · E-004 已创建并同步 module audit 与 synthetic behavioral gate。 · run=- · detail=evt-ad0c082471ed
- 2026-07-20T17:35:56+08:00 · run_rekey · Run registry 已从 R-012 迁移为 canonical ID E004-R-000-qwen3vl-head-hook-audit · run=E004-R-000-qwen3vl-head-hook-audit · detail=evt-d62aea93bc3a
- 2026-07-20T17:35:56+08:00 · run_rekey · Run registry 已从 R-013 迁移为 canonical ID E004-R-001-synthetic-double-instance-behavior-n4 · run=E004-R-001-synthetic-double-instance-behavior-n4 · detail=evt-a8337cd26fdf
- 2026-07-20T22:30:50+08:00 · run_created · Agent 创建 canonical Run E004-R-006-qwen3vl-head-hook-correctness-smoke · E004-R-006-qwen3vl-head-hook-correctness-smoke · run=E004-R-006-qwen3vl-head-hook-correctness-smoke · detail=evt-15a2e46016af
- 2026-07-20T22:30:50+08:00 · run_created · Agent 创建 canonical Run E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4 · E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4 · run=E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4 · detail=evt-b4a84ecf0638
- 2026-07-20T22:30:50+08:00 · run_created · Agent 创建 canonical Run E004-R-008-source-base-object-removal-proxy-gate-n4 · E004-R-008-source-base-object-removal-proxy-gate-n4 · run=E004-R-008-source-base-object-removal-proxy-gate-n4 · detail=evt-30ca8ca295f6
- 2026-07-20T22:30:51+08:00 · run_created · Agent 创建 canonical Run E004-R-009-layer-cma-recoverability-proxy-strict-n6 · E004-R-009-layer-cma-recoverability-proxy-strict-n6 · run=E004-R-009-layer-cma-recoverability-proxy-strict-n6 · detail=evt-de521b5d620e
- 2026-07-20T22:30:51+08:00 · run_created · Agent 创建 canonical Run E004-R-010-single-head-activation-patching-correctness-smoke · E004-R-010-single-head-activation-patching-correctness-smoke · run=E004-R-010-single-head-activation-patching-correctness-smoke · detail=evt-0253c6d9eb1e
- 2026-07-20T22:30:51+08:00 · run_created · Agent 创建 canonical Run E004-R-011-official-lama-code-acquisition · E004-R-011-official-lama-code-acquisition · run=E004-R-011-official-lama-code-acquisition · detail=evt-82841d324a7a
