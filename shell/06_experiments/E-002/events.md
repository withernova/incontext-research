
## 2026-07-14T10:10:31+08:00 · run_created
- run: R-010
- message: Agent 创建 R-010 · hard_patch_level_proxy_pilot

## 2026-07-14T10:10:31+08:00 · result
- run: R-010
- message: completed: hard_patch_level_proxy_pilot

output=/home/featurize/work/mechanism/explog/E-002/runs/R-002a-hard-patch-pilot-autoloop; metrics={"baseline":{"mIoU":0.5607,"TP":30,"TN":29,"FP":1,"FN":0,"F1":0.9836,"neg_FPR":0.0333},"ref_shuffle":{"mIoU":0.4805,"TP":28,"TN":29,"FP":1,"FN":2,"F1":0.9492},"pos_shuffle":{"mIoU":0.2723,"TP":30,"TN":29,"FP":1,"FN":0,"F1":0.9836},"ref_pos_shuffle":{"mIoU":0.3501,"TP":29,"TN":29,"FP":1,"FN":1,"F1":0.9667},"all_obj_shuffle":{"mIoU":0.3801,"TP":29,"TN":29,"FP":1,"FN":1,"F1":0.9667}}

## 2026-07-14T10:10:31+08:00 · run_created
- run: R-011
- message: Agent 创建 R-011 · qwen3vl_token_hook_inspection

## 2026-07-14T10:10:31+08:00 · result
- run: R-011
- message: completed: qwen3vl_token_hook_inspection

output=/home/featurize/work/mechanism/explog/E-002/runs/R-003-token-hook-inspection; metrics={"verified_hook_point":"Qwen3VLModel.forward: image_embeds = image_outputs.pooler_output; inputs_embeds.masked_scatter(image_mask, image_embeds)","artifact":"analysis/qwen3vl_module_inspection.json"}

## 2026-07-14T10:10:31+08:00 · run_created
- run: R-012
- message: Agent 创建 R-012 · qwen3vl_token_hook_smoke

## 2026-07-14T10:10:31+08:00 · result
- run: R-012
- message: completed: qwen3vl_token_hook_smoke

output=/home/featurize/work/mechanism/explog/E-002/runs/R-004-qwen3vl-token-hook-smoke; metrics={"status":"hook works","artifact":"analysis/hook_smoke_outputs.json"}

## 2026-07-14T10:10:31+08:00 · run_created
- run: R-013
- message: Agent 创建 R-013 · qwen3vl_full_visual_token_intervention_n10

## 2026-07-14T10:10:31+08:00 · result
- run: R-013
- message: completed: qwen3vl_full_visual_token_intervention_n10

output=/home/featurize/work/mechanism/explog/E-002/runs/R-005-qwen3vl-full-visual-token-intervention-n10; metrics={"baseline":{"TP":10,"TN":8,"FP":2,"FN":0,"F1":0.9091,"neg_FPR":0.2},"visual_shuffle":{"TP":10,"TN":0,"FP":10,"FN":0,"F1":0.6667,"neg_FPR":1.0},"visual_zero":{"TP":10,"TN":0,"FP":10,"FN":0,"F1":0.6667,"neg_FPR":1.0}}

## 2026-07-14T10:10:31+08:00 · run_created
- run: R-014
- message: Agent 创建 R-014 · qwen3vl_object_footprint_token_shuffle_n10

## 2026-07-14T10:10:31+08:00 · result
- run: R-014
- message: completed: qwen3vl_object_footprint_token_shuffle_n10

output=/home/featurize/work/mechanism/explog/E-002/runs/R-006-qwen3vl-object-token-shuffle-n10; metrics={"baseline":{"TP":10,"TN":10,"FP":0,"FN":0,"F1":1.0,"neg_FPR":0.0},"ref_obj_shuffle":{"TP":10,"TN":10,"FP":0,"FN":0,"F1":1.0,"neg_FPR":0.0},"query_obj_shuffle":{"TP":10,"TN":10,"FP":0,"FN":0,"F1":1.0,"neg_FPR":0.0},"ref_query_obj_shuffle":{"TP":10,"TN":9,"FP":1,"FN":0,"F1":0.9524,"neg_FPR":0.1},"full_visual_shuffle":{"TP":10,"TN":1,"FP":9,"FN":0,"F1":0.6897,"neg_FPR":0.9}}

## 2026-07-14T10:10:31+08:00 · run_created
- run: R-015
- message: Agent 创建 R-015 · qwen3vl_object_footprint_token_ablation_n10

## 2026-07-14T10:10:31+08:00 · result
- run: R-015
- message: completed: qwen3vl_object_footprint_token_ablation_n10

output=/home/featurize/work/mechanism/explog/E-002/runs/R-007-qwen3vl-object-token-ablation-n10; metrics={"baseline":{"TP":10,"TN":10,"FP":0,"FN":0,"F1":1.0,"neg_FPR":0.0},"ref_obj_zero":{"TP":10,"TN":9,"FP":1,"FN":0,"F1":0.9524,"neg_FPR":0.1},"query_obj_zero":{"TP":10,"TN":10,"FP":0,"FN":0,"F1":1.0,"neg_FPR":0.0},"ref_query_obj_zero":{"TP":10,"TN":10,"FP":0,"FN":0,"F1":1.0,"neg_FPR":0.0},"full_visual_zero":{"TP":10,"TN":0,"FP":10,"FN":0,"F1":0.6667,"neg_FPR":1.0},"full_visual_shuffle":{"TP":10,"TN":0,"FP":10,"FN":0,"F1":0.6667,"neg_FPR":1.0}}

## 2026-07-14T10:10:31+08:00 · run_created
- run: R-016
- message: Agent 创建 R-016 · persistent_orchestrator_crossrun_summary

## 2026-07-14T10:10:31+08:00 · result
- run: R-016
- message: completed: persistent_orchestrator_crossrun_summary

output=/home/featurize/work/mechanism/explog/E-002/runs/R-008-persistent-orchestrator-and-summary; metrics={"artifact":"analysis/e002_token_intervention_crossrun_summary.json"}

## 2026-07-14T10:11:26+08:00 · run_created
- run: R-017
- message: Agent 创建 R-017 · data_rehydrate_after_server_reset

## 2026-07-14T10:11:35+08:00 · result
- run: R-017
- message: completed: data rehydrate after server reset

LaSOT links=280; LASOTTesting_1shot_T2_local samples=140 missing=0; LASOT_hard_1shot_T2_n50 samples=50 missing=0; perturb variants regenerated under /home/featurize/data/e002_perturbed.

## 2026-07-20T17:04:13+08:00 · sync_blocker
- run: -
- message: E-003/E-004 最新 runs 已在本地 Markdown 归档，但当前 surveyctl 无 experiment-create 接口，暂不能按 canonical experiment/run IDs 写入工具 registry。

待同步：E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20（run 末尾 integrity assertion traceback，须记 failed/incomplete）；E004-R-000-qwen3vl-head-hook-audit（implementation audit）；E004-R-001-synthetic-double-instance-behavior-n4（completed / behavioral gate failed）。surveyctl run create E-003 返回 not found: E-003；experiment 子命令仅 context/events/handoff。未直接编辑 .survey-tool。
