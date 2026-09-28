# E-002 事件日志

> 本文件只保留单行摘要；完整 details 保存在工具内部的 experiment-events.jsonl 中。
> 需要展开某条事件时运行：`python3 /home/zhengyuesong/Tools/survey-tool/surveyctl.py --project <proj> experiment event-detail <E-ID> <EVENT-ID>`。

- 2026-07-14T10:10:31+08:00 · run_created · Agent 创建 R-010 · hard_patch_level_proxy_pilot · run=R-010 · detail=evt-e5febdd847c5
- 2026-07-14T10:10:31+08:00 · result · completed: hard_patch_level_proxy_pilot · run=R-010 · detail=evt-b778090ec1de
- 2026-07-14T10:10:31+08:00 · run_created · Agent 创建 R-011 · qwen3vl_token_hook_inspection · run=R-011 · detail=evt-f087ec7ab942
- 2026-07-14T10:10:31+08:00 · result · completed: qwen3vl_token_hook_inspection · run=R-011 · detail=evt-9b7912c998ab
- 2026-07-14T10:10:31+08:00 · run_created · Agent 创建 R-012 · qwen3vl_token_hook_smoke · run=R-012 · detail=evt-f7a815effdab
- 2026-07-14T10:10:31+08:00 · result · completed: qwen3vl_token_hook_smoke · run=R-012 · detail=evt-71cb2f70d51c
- 2026-07-14T10:10:31+08:00 · run_created · Agent 创建 R-013 · qwen3vl_full_visual_token_intervention_n10 · run=R-013 · detail=evt-43951388e21e
- 2026-07-14T10:10:31+08:00 · result · completed: qwen3vl_full_visual_token_intervention_n10 · run=R-013 · detail=evt-cd803541e8c9
- 2026-07-14T10:10:31+08:00 · run_created · Agent 创建 R-014 · qwen3vl_object_footprint_token_shuffle_n10 · run=R-014 · detail=evt-be600705aad3
- 2026-07-14T10:10:31+08:00 · result · completed: qwen3vl_object_footprint_token_shuffle_n10 · run=R-014 · detail=evt-574bc4e13688
- 2026-07-14T10:10:31+08:00 · run_created · Agent 创建 R-015 · qwen3vl_object_footprint_token_ablation_n10 · run=R-015 · detail=evt-2e5e82dff268
- 2026-07-14T10:10:31+08:00 · result · completed: qwen3vl_object_footprint_token_ablation_n10 · run=R-015 · detail=evt-1864d80b06a2
- 2026-07-14T10:10:31+08:00 · run_created · Agent 创建 R-016 · persistent_orchestrator_crossrun_summary · run=R-016 · detail=evt-c1a0fe7091c6
- 2026-07-14T10:10:31+08:00 · result · completed: persistent_orchestrator_crossrun_summary · run=R-016 · detail=evt-0307c158dbdc
- 2026-07-14T10:11:26+08:00 · run_created · Agent 创建 R-017 · data_rehydrate_after_server_reset · run=R-017 · detail=evt-918eea37bac8
- 2026-07-14T10:11:35+08:00 · result · completed: data rehydrate after server reset · run=R-017 · detail=evt-b27907029cd6
- 2026-07-20T17:04:13+08:00 · sync_blocker · E-003/E-004 最新 runs 已在本地 Markdown 归档，但当前 surveyctl 无 experiment-create 接口，暂不能按 canonical experiment/run IDs 写入工具 registry。 · run=- · detail=evt-134a57011b6d
