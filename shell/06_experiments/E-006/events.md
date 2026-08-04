
## 2026-07-28T23:21:49+08:00 · experiment_created
- run: -
- message: Agent 创建实验初稿 E-006 · 简洁的attention-on-GT与联通子图审计

## 2026-07-28T23:37:58+08:00 · run_created
- run: E006-R-005-simple-top50-support-components-positive-extremes-n111-640
- message: Agent 创建 canonical Run E006-R-005-simple-top50-support-components-positive-extremes-n111-640 · fixed top50 support per-head GtoR QtoR QtoQ

## 2026-07-28T23:51:04+08:00 · run_update
- run: E006-R-005-simple-top50-support-components-positive-extremes-n111-640
- message: 补全top50 support算法定义、条件归一化边界、selected-token统计与组会解释。

## 2026-08-03T14:54:20+08:00 · run_created
- run: E006-R-006-exact-last-token-bbox-row-alignment-gate-n10-640
- message: Agent 创建 canonical Run E006-R-006-exact-last-token-bbox-row-alignment-gate-n10-640 · exact last-token vs first-generate-step vs bbox-pminus1 row gate

## 2026-08-03T14:54:20+08:00 · run_created
- run: E006-R-007-refcoco-coco-frozen-manifest-integrity-gate-n1220
- message: Agent 创建 canonical Run E006-R-007-refcoco-coco-frozen-manifest-integrity-gate-n1220 · RefCOCO primary and optional filtered COCO-val proxy manifest gate

## 2026-08-03T14:54:20+08:00 · run_created
- run: E006-R-008-upstream-llava-last-token-refcoco-positive-control-n1000-200
- message: Agent 创建 canonical Run E006-R-008-upstream-llava-last-token-refcoco-positive-control-n1000-200 · immutable upstream LocalizationHeads LLaVA exact last-token positive control

## 2026-08-03T14:54:20+08:00 · run_created
- run: E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200
- message: Agent 创建 canonical Run E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200 · Qwen RefCOCO exact-last-token first-step bbox-row parity

## 2026-08-03T14:54:20+08:00 · run_created
- run: E006-R-010-outcome-stratified-allhead-discovery-sequence-split
- message: Agent 创建 canonical Run E006-R-010-outcome-stratified-allhead-discovery-sequence-split · correct-error separate all-head discovery for last-token and bbox rows

## 2026-08-03T14:54:20+08:00 · run_created
- run: E006-R-011-outcome-headsets-fresh-cross-evaluation
- message: Agent 创建 canonical Run E006-R-011-outcome-headsets-fresh-cross-evaluation · 2x2 correct-discovered error-discovered fresh sequence confirmation

## 2026-08-03T14:54:20+08:00 · run_created
- run: E006-R-012-reference-query-transform-geometric-separability-gate
- message: Agent 创建 canonical Run E006-R-012-reference-query-transform-geometric-separability-gate · identity HFlip VFlip R180 reference-only query-only both offline geometry

## 2026-08-03T14:54:20+08:00 · run_created
- run: E006-R-013-natural-behavior-transform-gate
- message: Agent 创建 canonical Run E006-R-013-natural-behavior-transform-gate · natural Yes bbox under REF-only QUERY-only BOTH H V R180

## 2026-08-03T14:54:20+08:00 · run_created
- run: E006-R-014-qtor-reference-vs-query-coordinate-equivariance
- message: Agent 创建 canonical Run E006-R-014-qtor-reference-vs-query-coordinate-equivariance · QtoR reference tracking versus query-coordinate copy transform audit

## 2026-08-03T14:54:20+08:00 · run_created
- run: E006-R-015-reference-image-vs-prompt-bbox-mismatch-diagnostic
- message: Agent 创建 canonical Run E006-R-015-reference-image-vs-prompt-bbox-mismatch-diagnostic · reference visual transform versus explicit bbox-coordinate mismatch

## 2026-08-03T15:15:18+08:00 · run_update
- run: E006-R-007-refcoco-coco-frozen-manifest-integrity-gate-n1220
- message: 按用户审核修订R-007：使用现有COCO，澄清unique-image来源与采样单位。

## 2026-08-03T15:16:11+08:00 · run_update
- run: E006-R-008-upstream-llava-last-token-refcoco-positive-control-n1000-200
- message: 用户决定不做LLaVA upstream control。

## 2026-08-03T15:16:11+08:00 · run_update
- run: E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200
- message: 按用户疑问重新解释并缩小R-009。

## 2026-08-03T15:17:11+08:00 · run_review_submitted
- run: E006-R-007-refcoco-coco-frozen-manifest-integrity-gate-n1220
- message: 已按审核修订：使用现有COCO；n为expression samples；image_id group split是本地防泄漏而非原文要求。

## 2026-08-03T15:17:11+08:00 · run_review_submitted
- run: E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200
- message: 已简化为Qwen-only可选RefCOCO空间正对照，请决定保留或取消。

## 2026-08-03T15:17:11+08:00 · run_created
- run: E006-R-010b-outcome-stratified-reference-query-allhead-discovery-viz
- message: Agent 创建 canonical Run E006-R-010b-outcome-stratified-reference-query-allhead-discovery-viz · correct error balanced-mix by reference-query role all-head discovery and visualization

## 2026-08-03T15:17:11+08:00 · run_update
- run: E006-R-010b-outcome-stratified-reference-query-allhead-discovery-viz
- message: 基于已批准R010的新增可视化授权备注创建实质修订版，避免修改已批准记录。

## 2026-08-03T15:17:11+08:00 · run_review_submitted
- run: E006-R-010b-outcome-stratified-reference-query-allhead-discovery-viz
- message: 请审核修订版R010b；旧R010保留但不执行。

## 2026-08-03T15:17:11+08:00 · run_update
- run: E006-R-011-outcome-headsets-fresh-cross-evaluation
- message: 同步用户对R010的三组和可视化要求。

## 2026-08-03T17:55:31+08:00 · run_review_submitted
- run: E006-R-014-qtor-reference-vs-query-coordinate-equivariance
- message: 按用户要求重写为attention-first直接空间迁移审计：同一forward Q→R/Q→Q、projected Q→Q、REF-only/QUERY-only、固定main4与6+6全套turbo heatmaps。请审核；尚未执行。

## 2026-08-03T20:06:43+08:00 · run_created
- run: E006-R-014b-r005-sample-aligned-three-row-equivariance-visualization
- message: Agent 创建 canonical Run E006-R-014b-r005-sample-aligned-three-row-equivariance-visualization · r005-sample-aligned-three-row-equivariance-visualization

## 2026-08-03T20:07:03+08:00 · run_review_submitted
- run: E006-R-014b-r005-sample-aligned-three-row-equivariance-visualization
- message: 已按用户反馈提交初稿：与R-005原始n111样本对齐；固定6 correct+6 error、84个真实自然生成/replay；36张identity/REF-only/QUERY-only三行四列主图；修复原图到max_side=640显示坐标缩放；每行显示当前预测状态与IoU；R-014保持不可变。请用户审核和补充，批准后仍需单独执行授权。

## 2026-08-03T20:18:40+08:00 · run_update
- run: E006-R-014b-r005-sample-aligned-three-row-equivariance-visualization
- message: Activated and launched only R-014b after approval/authorization/spec-equality gate.

## 2026-08-03T20:36:17+08:00 · run_update
- run: E006-R-014b-r005-sample-aligned-three-row-equivariance-visualization
- message: exit=0; GATE_PASS; 84/84 natural generations and same-forward bbox-p-1 teacher replays; 36/36 main 3x4 figures; 84 appendices; no parse failures. REF-only sequence-level median mass preference toward R_t over R_0 = +0.01468, 95% sequence bootstrap CI [-0.02155,+0.06075], 8/12 positive; only VFlip transform CI excluded 0. QUERY-only preference for R_0 over projected Q_t = +0.03066 CI [-0.01503,+0.07831], 7/12. Supports at most a weak/mixed reference-region tracking signature; simple direct query-map copying remains weakened, not disproved; non-causal and small n.

## 2026-08-03T20:39:43+08:00 · run_update
- run: E006-R-014b-r005-sample-aligned-three-row-equivariance-visualization
- message: Completed canonical result and bounded interpretation; local statistical charts added.

## 2026-08-03T20:44:19+08:00 · run_created
- run: E006-R-016-icol-last-token-row-stage-falsification
- message: Agent 创建 canonical Run E006-R-016-icol-last-token-row-stage-falsification · icol-last-token-row-stage-falsification

## 2026-08-03T20:44:19+08:00 · run_review_submitted
- run: E006-R-016-icol-last-token-row-stage-falsification
- message: Run 初稿已完成，等待用户审核

## 2026-08-03T22:00:45+08:00 · run_update
- run: E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200
- message: User requested proceeding with experiment after COCO train2014 extraction. Pre-execution dependency/data gate now being validated; no model run launched yet.

## 2026-08-03T22:01:13+08:00 · run_update
- run: E006-R-007-refcoco-coco-frozen-manifest-integrity-gate-n1220
- message: Corrected immutable old R-007 status to completed gate-stop; current assets require R-007b.

## 2026-08-03T22:01:41+08:00 · run_created
- run: E006-R-007b-refcoco-train2014-recovery-integrity-gate-n1220
- message: Agent 创建 canonical Run E006-R-007b-refcoco-train2014-recovery-integrity-gate-n1220 · refcoco-train2014-recovery-integrity-gate-n1220

## 2026-08-03T22:01:41+08:00 · run_review_submitted
- run: E006-R-007b-refcoco-train2014-recovery-integrity-gate-n1220
- message: Run 初稿已完成，等待用户审核

## 2026-08-04T15:14:44+08:00 · run_update
- run: E006-R-007b-refcoco-train2014-recovery-integrity-gate-n1220
- message: Network interruption did not affect remote tmux; R-007b completed successfully.

## 2026-08-04T15:30:31+08:00 · run_created
- run: E006-R-014c-prediction-projection-expanded-equivariance-audit
- message: Agent 创建 canonical Run E006-R-014c-prediction-projection-expanded-equivariance-audit · prediction-projection-expanded-equivariance-audit

## 2026-08-04T15:30:31+08:00 · run_review_submitted
- run: E006-R-014c-prediction-projection-expanded-equivariance-audit
- message: Run 初稿已完成，等待用户审核

## 2026-08-04T15:39:47+08:00 · run_update
- run: E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200
- message: Completed after one archived missing-scipy attempt; canonical successful attempt used existing lama_site scipy.

## 2026-08-04T15:40:37+08:00 · run_created
- run: E006-R-009b-refcoco-natural-bbox-token-head-transfer-n1000-200
- message: Agent 创建 canonical Run E006-R-009b-refcoco-natural-bbox-token-head-transfer-n1000-200 · refcoco-natural-bbox-token-head-transfer-n1000-200

## 2026-08-04T15:40:37+08:00 · run_review_submitted
- run: E006-R-009b-refcoco-natural-bbox-token-head-transfer-n1000-200
- message: Run 初稿已完成，等待用户审核

## 2026-08-04T15:46:45+08:00 · run_update
- run: E006-R-009b-refcoco-natural-bbox-token-head-transfer-n1000-200
- message: Sequential first run completed at preregistered pilot gate. No scope bypass; normalized-coordinate recovery requires a new run.

## 2026-08-04T16:02:57+08:00 · run_created
- run: E006-R-009c-refcoco-qwen-normalized-natural-bbox-token-head-transfer-n1000-200
- message: Agent 创建 canonical Run E006-R-009c-refcoco-qwen-normalized-natural-bbox-token-head-transfer-n1000-200 · refcoco-qwen-normalized-natural-bbox-token-head-transfer-n1000-200

## 2026-08-04T16:02:57+08:00 · run_review_submitted
- run: E006-R-009c-refcoco-qwen-normalized-natural-bbox-token-head-transfer-n1000-200
- message: Run 初稿已完成，等待用户审核

## 2026-08-04T17:25:21+08:00 · run_update
- run: E006-R-014c-prediction-projection-expanded-equivariance-audit
- message: Completed with one immutable natural parse failure (idx86 monkey-3 REF-only VFlip); no borrowed bbox and no rerun.

## 2026-08-04T17:46:57+08:00 · run_update
- run: E006-R-009c-refcoco-qwen-normalized-natural-bbox-token-head-transfer-n1000-200
- message: Completed after archived attempt-001 variable-grid raw-map accumulation failure; successful recovery used per-sample repo-style head votes. Interpretation explicitly bounded by modified explicit-bbox prompt.

## 2026-08-04T17:47:36+08:00 · run_created
- run: E006-R-009d-refcoco-original-prompt-natural-output-row-audit-n20-1000-200
- message: Agent 创建 canonical Run E006-R-009d-refcoco-original-prompt-natural-output-row-audit-n20-1000-200 · refcoco-original-prompt-natural-output-row-audit-n20-1000-200

## 2026-08-04T17:47:36+08:00 · run_review_submitted
- run: E006-R-009d-refcoco-original-prompt-natural-output-row-audit-n20-1000-200
- message: Run 初稿已完成，等待用户审核

## 2026-08-04T18:44:45+08:00 · run_update
- run: E006-R-009d-refcoco-original-prompt-natural-output-row-audit-n20-1000-200
- message: Successful canonical attempt followed archived attempt-001 one-natural-nonbbox handling bug; successful runner preserved output and enforced >=95% coverage.

## 2026-08-04T18:45:27+08:00 · run_created
- run: E006-R-009e-refcoco-specific-gt-aligned-head-discovery-viz-fresh200
- message: Agent 创建 canonical Run E006-R-009e-refcoco-specific-gt-aligned-head-discovery-viz-fresh200 · refcoco-specific-gt-aligned-head-discovery-viz-fresh200

## 2026-08-04T18:45:27+08:00 · run_review_submitted
- run: E006-R-009e-refcoco-specific-gt-aligned-head-discovery-viz-fresh200
- message: Run 初稿已完成，等待用户审核

## 2026-08-04T19:22:19+08:00 · run_created
- run: E006-R-017-refcoco-synthetic-paired-view-icol-format-head-transfer
- message: Agent 创建 canonical Run E006-R-017-refcoco-synthetic-paired-view-icol-format-head-transfer · refcoco-synthetic-paired-view-icol-format-head-transfer

## 2026-08-04T19:22:20+08:00 · run_review_submitted
- run: E006-R-017-refcoco-synthetic-paired-view-icol-format-head-transfer
- message: Run 初稿已完成，等待用户审核

## 2026-08-04T19:30:32+08:00 · run_created
- run: E006-R-017b-refcoco-synthetic-icol-format-within-lora-head-transfer
- message: Agent 创建 canonical Run E006-R-017b-refcoco-synthetic-icol-format-within-lora-head-transfer · refcoco-synthetic-icol-format-within-lora-head-transfer

## 2026-08-04T19:30:32+08:00 · run_review_submitted
- run: E006-R-017b-refcoco-synthetic-icol-format-within-lora-head-transfer
- message: Run 初稿已完成，等待用户审核

## 2026-08-04T19:41:14+08:00 · run_update
- run: E006-R-017b-refcoco-synthetic-icol-format-within-lora-head-transfer
- message: Approved authorization consumed for Stage0 only. Immutable preregistered geometry retention gate failed; stopped before GPU/model inference. Artifacts preserved in canonical run directory.
