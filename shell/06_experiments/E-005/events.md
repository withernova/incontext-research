
## 2026-07-24T13:42:03+08:00 · experiment_created
- run: -
- message: Agent 创建实验初稿 E-005 · Attention-derived localization-head discovery and grounding audit

## 2026-07-24T13:44:31+08:00 · discovery
- run: -
- message: 官方仓库已按固定commit下载为只读上游快照。

路径=shell/06_experiments/_legacy/codespace/LocalizationHeads；commit=9ffe219d20ec376eb4dd14d42c54bb3299ffdb4a；Git clone因HTTP2/empty reply失败，改用GitHub codeload commit tarball；archive sha256=b020c51a97f6911829da6b83202104cdfc5519ca7706f4c7e5a960ede7e0b9e9；源码清单hash=shell/06_experiments/_legacy/codespace/LocalizationHeads_upstream_sha256.txt。

## 2026-07-24T13:44:31+08:00 · discovery
- run: -
- message: 公开实现与论文主协议存在需隔离处理的差异，不能直接视作逐公式复现。

conf/logic/selection_v1.yaml默认top_k=5而论文§6.3主设置k=3；analyze.py使用ReLU(S-2*mean)并按component attention mass算entropy，而论文Appendix B.1 Eq.4/Eq.7为ReLU(S-mean)与component area；bbox.py直接取所有正mask的min/max，未执行论文Appendix B.2所述largest convex hull；README称10 trials而论文Appendix A称5 trials。

## 2026-07-24T13:44:32+08:00 · discovery
- run: -
- message: 官方实现的核心attention读取位置与论文方向一致。

collector.py调用output_attentions=True并截取最后输入token到视觉span，输出[L,H,1,V]；默认eager attention；前两层在analyze.py通过layer>1排除。

## 2026-07-24T13:44:32+08:00 · blocker
- run: -
- message: 直接SSH勘察被本机host-key校验阻断；实验状态工具仍可访问远端。

命令ssh featurize返回Host key verification failed；experiment_status确认GPU=RTX3090 24GB、disk 66/100G、旧e004_lama_env为正常保留的dead pane。该旧日志错误不是E-005错误。

## 2026-07-24T13:44:32+08:00 · handoff
- run: -
- message: Agent 已提交勘察结果与待确认表单

## 2026-07-24T13:45:58+08:00 · decision
- run: -
- message: 用户确认E-005以当前公开代码参数和实现为主，不按论文公式另建paper-faithful主分支。

主协议采用repo-original：selection_v1.yaml top_k=5、analyze.py ReLU(A-2mean)+component attention-mass entropy、bottom-row filter、bbox.py当前mask min/max实现；论文差异仅记录为复现边界。上游shell/06_experiments/_legacy/codespace/LocalizationHeads保持零修改。

## 2026-07-24T13:52:44+08:00 · discovery
- run: -
- message: 远端勘察恢复：SSH host-key已按现有known_hosts中的端口记录接受，未绕过校验。

ssh featurize现可用；远端RTX3090 24GB空闲；e004_site含torch2.2.2+cu121/transformers4.57.3/peft0.18.0；scipy仅在lama_site；Qwen snapshot与LaSOT manifest在本次服务器状态下缺失，需恢复后才能做真实模型smoke。

## 2026-07-24T13:52:45+08:00 · implementation
- run: -
- message: 已完成最小Qwen3-VL适配层，未修改官方LocalizationHeads源码。

新增shell/06_experiments/_legacy/codespace/e005_adapter/{analyze_rect.py,qwen_spans.py,qwen_collector.py,test_repo_compat.py,README.md}；远端同步至/home/featurize/work/mechanism/scripts/e005/adapter；上游同步至/home/featurize/work/mechanism/third_party/LocalizationHeads。

## 2026-07-24T13:52:45+08:00 · test
- run: -
- message: repo-original兼容性与Qwen span单元测试全部通过。

远端PYTHONPATH=lama_site:e004_site:LocalizationHeads:e005_adapter；5/5 passed：square parity、rectangular analysis、two-image span/extraction、collector contract、mismatch hard failure；本地上游hash清单全量验证通过。真实Qwen forward尚未运行，因为model snapshot缺失。

## 2026-07-24T13:53:11+08:00 · run_created
- run: E005-R-000-repo-original-qwen-adapter-unit-gate
- message: Agent 创建 canonical Run E005-R-000-repo-original-qwen-adapter-unit-gate · repo-original Qwen适配单元门禁

## 2026-07-24T13:54:01+08:00 · run_created
- run: E005-R-001-qwen3vl-model-recovery-localdisk
- message: Agent 创建 canonical Run E005-R-001-qwen3vl-model-recovery-localdisk · Qwen3-VL本地盘模型恢复

## 2026-07-24T13:54:01+08:00 · start
- run: E005-R-001-qwen3vl-model-recovery-localdisk
- message: 已在独立tmux启动Qwen3-VL模型恢复。

tmux=e005_model_recovery；log=/home/featurize/work/mechanism/explog/E-005/runs/E005-R-001-qwen3vl-model-recovery-localdisk/logs/download.log；server-local cache；remain-on-exit=on。

## 2026-07-24T14:21:05+08:00 · run_update
- run: E005-R-001-qwen3vl-model-recovery-localdisk
- message: R-001模型恢复完整性门禁通过，正常完成。

## 2026-07-24T14:21:05+08:00 · complete
- run: E005-R-001-qwen3vl-model-recovery-localdisk
- message: Qwen3-VL本地snapshot恢复成功，retained pane exit status 0。

snapshot=/home/featurize/.cache/huggingface/hub/models--Qwen--Qwen3-VL-8B-Instruct/snapshots/0c351dd01ed87e9c1b53cbc748cba10e6187ff3b；4 shards；17,534,339,512 bytes；download 16/16。

## 2026-07-24T14:27:27+08:00 · run_created
- run: E005-R-002-qwen3vl-iplocid-single-sample-attention-smoke
- message: Agent 创建 canonical Run E005-R-002-qwen3vl-iplocid-single-sample-attention-smoke · Qwen3-VL/IPLoc-ID单样本真实attention smoke

## 2026-07-24T14:27:27+08:00 · start
- run: E005-R-002-qwen3vl-iplocid-single-sample-attention-smoke
- message: 已按顺序启动真实Qwen3-VL/IPLoc-ID单样本attention smoke。

tmux=e005_attention_smoke；max_side=224；strict offline；synthetic sample仅作工程门禁。

## 2026-07-24T14:28:44+08:00 · run_update
- run: E005-R-002-qwen3vl-iplocid-single-sample-attention-smoke
- message: R-002因重启后reference源图缺失在模型加载前失败，转入自包含synthetic reference恢复Run。

## 2026-07-24T14:28:44+08:00 · failure
- run: E005-R-002-qwen3vl-iplocid-single-sample-attention-smoke
- message: R-002 preflight失败：LaSOT reference文件缺失。

FileNotFoundError；模型尚未加载，GPU未使用；不解释为attention smoke失败。

## 2026-07-24T14:29:10+08:00 · run_created
- run: E005-R-002b-qwen3vl-self-contained-attention-smoke
- message: Agent 创建 canonical Run E005-R-002b-qwen3vl-self-contained-attention-smoke · 自包含synthetic-reference真实attention恢复smoke

## 2026-07-24T14:29:10+08:00 · start
- run: E005-R-002b-qwen3vl-self-contained-attention-smoke
- message: 已立即启动自包含真实attention恢复smoke。

reference来自query crop，仅工程验证；不进入科学head discovery。

## 2026-07-24T14:30:02+08:00 · run_update
- run: E005-R-002b-qwen3vl-self-contained-attention-smoke
- message: R-002b输入wrapper参数缺失，保留失败记录并以R-002c恢复。

## 2026-07-24T14:30:04+08:00 · run_created
- run: E005-R-002c-qwen3vl-self-contained-attention-smoke-fixed
- message: Agent 创建 canonical Run E005-R-002c-qwen3vl-self-contained-attention-smoke-fixed · 自包含真实attention smoke参数修复

## 2026-07-24T14:33:01+08:00 · run_update
- run: E005-R-002c-qwen3vl-self-contained-attention-smoke-fixed
- message: R-002c全部shape/span/finite/eager门禁通过。

## 2026-07-24T14:33:01+08:00 · complete
- run: E005-R-002c-qwen3vl-self-contained-attention-smoke-fixed
- message: 真实attention smoke通过，正常exit status 0。

36 layers、32 heads；reference/query动态grid均严格对齐；peak allocated约17.86GB。reference来自query crop，不能进入科学pilot。

## 2026-07-24T14:33:01+08:00 · blocker
- run: -
- message: 正式pilot仍被独立数据缺失阻塞。

服务器重启后/home/featurize/data/LaSOTTesting不存在；当前只有synthetic query及identity-leaking crop。不能用它们冒充独立discovery/evaluation样本。需要恢复LaSOT或接入另一份带bbox的真实数据。

## 2026-07-24T14:38:53+08:00 · run_created
- run: E005-R-003-refcoco-train-data-acquisition-split-n1220
- message: Agent 创建 canonical Run E005-R-003-refcoco-train-data-acquisition-split-n1220 · RefCOCO train数据获取与固定分区

## 2026-07-24T14:40:19+08:00 · run_update
- run: E005-R-003-refcoco-train-data-acquisition-split-n1220
- message: R-003因COCO CDN HTTPS代理证书错配主动终止，保留记录。

## 2026-07-24T14:40:22+08:00 · run_created
- run: E005-R-003b-refcoco-train-data-acquisition-http-n1220
- message: Agent 创建 canonical Run E005-R-003b-refcoco-train-data-acquisition-http-n1220 · RefCOCO train数据获取HTTP恢复

## 2026-07-24T15:13:55+08:00 · run_update
- run: E005-R-003b-refcoco-train-data-acquisition-http-n1220
- message: 按用户决定停止RefCOCO路线，切换到自有IPL oc-ID/LaSOT数据。

## 2026-07-24T15:15:18+08:00 · run_created
- run: E005-R-003c-lasot-local-manifest-rehydrate-n140
- message: Agent 创建 canonical Run E005-R-003c-lasot-local-manifest-rehydrate-n140 · 自有LaSOT/IPLoc-ID任务数据恢复

## 2026-07-24T15:15:48+08:00 · run_update
- run: E005-R-003c-lasot-local-manifest-rehydrate-n140
- message: R-003c通过：LaSOT/IPLoc-ID n140任务数据已恢复。

## 2026-07-24T15:21:13+08:00 · run_created
- run: E005-R-004-lasot-iplocid-attention-pilot-n10
- message: Agent 创建 canonical Run E005-R-004-lasot-iplocid-attention-pilot-n10 · 自有LaSOT/IPLoc-ID正负样本attention pilot n10

## 2026-07-24T15:22:34+08:00 · run_update
- run: E005-R-004-lasot-iplocid-attention-pilot-n10
- message: R-004通过：自有LaSOT/IPLoc-ID n10 attention pilot完成。

## 2026-07-24T15:23:27+08:00 · run_created
- run: E005-R-005-lasot-iplocid-attention-discovery-n100
- message: Agent 创建 canonical Run E005-R-005-lasot-iplocid-attention-discovery-n100 · 自有LaSOT/IPLoc-ID attention discovery n100

## 2026-07-24T15:26:02+08:00 · run_update
- run: E005-R-005-lasot-iplocid-attention-discovery-n100
- message: R-005通过：n100 discovery完成，保留40样本独立evaluation。

## 2026-07-24T15:30:53+08:00 · run_created
- run: E005-R-006-lasot-fixed-head-heldout-eval-n40
- message: Agent 创建 canonical Run E005-R-006-lasot-fixed-head-heldout-eval-n40 · 固定discovery heads的LaSOT held-out grounding eval n40

## 2026-07-24T15:32:41+08:00 · run_update
- run: E005-R-006-lasot-fixed-head-heldout-eval-n40
- message: R-006完成：固定top5 held-out grounding较弱，需审计role-specific selection和bbox maps，不能重选后冒充同一held-out验证。

## 2026-07-24T15:33:23+08:00 · run_created
- run: E005-R-007-positive-query-role-specific-selection-n80
- message: Agent 创建 canonical Run E005-R-007-positive-query-role-specific-selection-n80 · R-006后post-hoc positive-query role-specific selection

## 2026-07-24T15:33:40+08:00 · run_update
- run: E005-R-007-positive-query-role-specific-selection-n80
- message: R-007 schema失败：global_index不存在。

## 2026-07-24T15:34:29+08:00 · run_created
- run: E005-R-007b-positive-query-role-specific-selection-n80
- message: Agent 创建 canonical Run E005-R-007b-positive-query-role-specific-selection-n80 · positive-query role-specific selection schema recovery

## 2026-07-24T15:34:45+08:00 · run_update
- run: E005-R-007b-positive-query-role-specific-selection-n80
- message: R-007b通过：role-specific top5已冻结。

## 2026-07-24T15:35:37+08:00 · run_created
- run: E005-R-008-role-specific-internal-validation-n20
- message: Agent 创建 canonical Run E005-R-008-role-specific-internal-validation-n20 · post-hoc role-specific internal validation n20

## 2026-07-24T15:37:00+08:00 · run_update
- run: E005-R-008-role-specific-internal-validation-n20
- message: R-008完成：role-specific恢复仍弱，且无positive优于negative证据。

## 2026-07-24T16:00:35+08:00 · run_created
- run: E005-R-009-prompt-image-token-attention-budget-n20
- message: Agent 创建 canonical Run E005-R-009-prompt-image-token-attention-budget-n20 · prompt图像token多query attention-budget audit n20

## 2026-07-24T16:01:14+08:00 · run_update
- run: E005-R-009-prompt-image-token-attention-budget-n20
- message: 按用户重排链路停止R-009：先做head GT concentration与可视化审计。

## 2026-07-24T16:03:14+08:00 · run_created
- run: E005-R-010-frozen-head-gt-concentration-viz-audit-n40
- message: Agent 创建 canonical Run E005-R-010-frozen-head-gt-concentration-viz-audit-n40 · 冻结论文方法heads的GT concentration与可视化审计

## 2026-07-24T16:04:52+08:00 · run_update
- run: E005-R-010-frozen-head-gt-concentration-viz-audit-n40
- message: R-010 quality gate失败：当前论文代码移植选出的top5不是优质GT定位heads；10组可视化已归档供人工审核。

## 2026-07-24T16:11:17+08:00 · run_created
- run: E005-R-010b-turbo-visualization-and-query-token-audit-n10
- message: Agent 创建 canonical Run E005-R-010b-turbo-visualization-and-query-token-audit-n10 · R-010可视化配色修正与query-token审计

## 2026-07-24T16:12:53+08:00 · run_update
- run: E005-R-010b-turbo-visualization-and-query-token-audit-n10
- message: R-010b完成：蓝低红高turbo图已归档；确认last query是newline控制位置。

## 2026-07-24T16:17:11+08:00 · run_created
- run: E005-R-011-coordinate-prediction-query-head-recovery-n80-20
- message: Agent 创建 canonical Run E005-R-011-coordinate-prediction-query-head-recovery-n80-20 · teacher-forced coordinate-prediction query head recovery n80+20

## 2026-07-24T16:18:56+08:00 · run_update
- run: E005-R-011-coordinate-prediction-query-head-recovery-n80-20
- message: R-011严格alignment gate失败，保留失败run并修复为唯一子序列匹配。

## 2026-07-24T16:24:43+08:00 · run_created
- run: E005-R-011b-coordinate-prediction-query-head-recovery-n80-20
- message: Agent 创建 canonical Run E005-R-011b-coordinate-prediction-query-head-recovery-n80-20 · teacher-forced coordinate-prediction query recovery（唯一子序列对齐修复）

## 2026-07-24T16:26:33+08:00 · run_update
- run: E005-R-011b-coordinate-prediction-query-head-recovery-n80-20
- message: R-011b metadata index失败；保留并立即以R-011c修复重跑。

## 2026-07-24T16:27:12+08:00 · run_created
- run: E005-R-011c-coordinate-prediction-query-head-recovery-n80-20
- message: Agent 创建 canonical Run E005-R-011c-coordinate-prediction-query-head-recovery-n80-20 · coordinate-prediction query recovery（metadata修复）

## 2026-07-24T16:29:35+08:00 · run_update
- run: E005-R-011c-coordinate-prediction-query-head-recovery-n80-20
- message: R-011c通过：坐标预测rows找到合理GT定位heads，turbo图显示热点靠近GT；下一步先人工审核全部图，再用新未使用数据确认。

## 2026-07-24T16:33:58+08:00 · run_created
- run: E005-R-012-dual-span-coordinate-query-common-heads-n80-20
- message: Agent 创建 canonical Run E005-R-012-dual-span-coordinate-query-common-heads-n80-20 · dual-span coordinate-query shared localization heads n80+20

## 2026-07-24T16:36:16+08:00 · run_created
- run: E005-R-012b-query-derived-heads-cross-span-viz-n80-20
- message: Agent 创建 canonical Run E005-R-012b-query-derived-heads-cross-span-viz-n80-20 · 冻结query-derived heads的reference/query双侧可视化

## 2026-07-24T16:38:23+08:00 · run_update
- run: E005-R-012-dual-span-coordinate-query-common-heads-n80-20
- message: R-012完成：频率重叠弱且不是有效shared定义；query-derived整组跨双span通过。

## 2026-07-24T16:38:23+08:00 · run_update
- run: E005-R-012b-query-derived-heads-cross-span-viz-n80-20
- message: R-012b通过：query-derived五头双span质量门禁均过，图已归档供审核。

## 2026-07-24T16:40:59+08:00 · run_created
- run: E005-R-013-unseen-sequence-positive-manifest-n70
- message: Agent 创建 canonical Run E005-R-013-unseen-sequence-positive-manifest-n70 · 完全未使用LaSOT sequences positive-only确认manifest n70

## 2026-07-24T16:40:59+08:00 · run_update
- run: E005-R-013-unseen-sequence-positive-manifest-n70
- message: R-013 manifest通过。

## 2026-07-24T16:41:59+08:00 · run_created
- run: E005-R-014-unseen-sequence-dual-span-confirmation-n70
- message: Agent 创建 canonical Run E005-R-014-unseen-sequence-dual-span-confirmation-n70 · unseen-sequence frozen-head dual-span confirmation n70

## 2026-07-24T16:44:19+08:00 · run_update
- run: E005-R-014-unseen-sequence-dual-span-confirmation-n70
- message: R-014新sequence确认通过：main4双侧复现，负面对照有效。

## 2026-07-24T16:55:34+08:00 · run_created
- run: E005-R-014b-paired-reference-query-visualizations-n10
- message: Agent 创建 canonical Run E005-R-014b-paired-reference-query-visualizations-n10 · R-014同次推理reference-query配对可视化n10

## 2026-07-24T16:55:34+08:00 · run_update
- run: E005-R-014b-paired-reference-query-visualizations-n10
- message: R-014b配对图完成；prelaunch目录错误已单独记录。

## 2026-07-24T17:02:00+08:00 · run_created
- run: E005-R-015-reverse-reference-target-coordinate-head-discovery-n80-20
- message: Agent 创建 canonical Run E005-R-015-reverse-reference-target-coordinate-head-discovery-n80-20 · reverse-direction reference-target coordinate-query head discovery n80+20

## 2026-07-24T17:04:01+08:00 · run_update
- run: E005-R-015-reverse-reference-target-coordinate-head-discovery-n80-20
- message: R-015完成：reference-target质量通过，共同有效精确heads为L18H15/L19H03。

## 2026-07-24T17:12:22+08:00 · run_created
- run: E005-R-016-original-order-reference-grounding-vs-query-localization-heads-n80-20
- message: Agent 创建 canonical Run E005-R-016-original-order-reference-grounding-vs-query-localization-heads-n80-20 · original-order reference-grounding vs query-localization heads n80+20

## 2026-07-24T17:15:55+08:00 · run_created
- run: E005-R-017-original-order-three-channel-reference-use-heads-n80-20
- message: Agent 创建 canonical Run E005-R-017-original-order-three-channel-reference-use-heads-n80-20 · original-order three-channel reference grounding/retrieval/query localization n80+20

## 2026-07-24T17:19:12+08:00 · run_update
- run: E005-R-016-original-order-reference-grounding-vs-query-localization-heads-n80-20
- message: R-016完成。

## 2026-07-24T17:19:12+08:00 · run_update
- run: E005-R-017-original-order-three-channel-reference-use-heads-n80-20
- message: R-017完成：reference retrieval own head gate失败，需换矩阵/因果指标。

## 2026-07-24T17:26:12+08:00 · run_created
- run: E005-R-018-query-visual-to-reference-token-head-discovery-n80-20
- message: Agent 创建 canonical Run E005-R-018-query-visual-to-reference-token-head-discovery-n80-20 · query visual rows to reference token retrieval heads n80+20

## 2026-07-24T17:28:37+08:00 · run_update
- run: E005-R-018-query-visual-to-reference-token-head-discovery-n80-20
- message: R-018完成：空间reference retrieval通过，identity selectivity未通过。

## 2026-07-24T18:14:07+08:00 · run_created
- run: E005-R-019-yes-no-decision-token-reference-query-heads-n80-20
- message: Agent 创建 canonical Run E005-R-019-yes-no-decision-token-reference-query-heads-n80-20 · Yes/No decision-token reference/query attention heads n80+20

## 2026-07-24T18:15:18+08:00 · run_update
- run: E005-R-019-yes-no-decision-token-reference-query-heads-n80-20
- message: R-019失败，修正后另开R-019b。

## 2026-07-24T18:15:39+08:00 · run_created
- run: E005-R-019b-yes-no-decision-token-reference-query-heads-n80-20
- message: Agent 创建 canonical Run E005-R-019b-yes-no-decision-token-reference-query-heads-n80-20 · Yes/No decision-token reference/query heads recovery n80+20

## 2026-07-24T18:18:25+08:00 · run_update
- run: E005-R-019b-yes-no-decision-token-reference-query-heads-n80-20
- message: R-019b完成：decision双span重合高但空间门禁全失败。

## 2026-07-24T18:46:58+08:00 · run_created
- run: E005-R-020-unified-reference-query-yesno-role-visualizations-n10x2
- message: Agent 创建 canonical Run E005-R-020-unified-reference-query-yesno-role-visualizations-n10x2 · unified reference retrieval query localization YesNo visualization n10x2

## 2026-07-24T18:48:18+08:00 · run_update
- run: E005-R-020-unified-reference-query-yesno-role-visualizations-n10x2
- message: R-020失败，另开R-020b。

## 2026-07-24T18:48:45+08:00 · run_created
- run: E005-R-020b-unified-reference-query-yesno-role-visualizations-n10x2
- message: Agent 创建 canonical Run E005-R-020b-unified-reference-query-yesno-role-visualizations-n10x2 · unified three-role visualizations recovery n10x2

## 2026-07-24T18:56:16+08:00 · run_update
- run: E005-R-020b-unified-reference-query-yesno-role-visualizations-n10x2
- message: R-020b成功完成并通过20图+manifest完整性核验。

## 2026-07-24T20:50:20+08:00 · run_created
- run: E005-R-021-e003-screened-wrong-instance-natural-output-attention-n7
- message: Agent 创建 canonical Run E005-R-021-e003-screened-wrong-instance-natural-output-attention-n7 · E003 screened wrong-instance archived-natural-output attention n7

## 2026-07-24T20:52:18+08:00 · run_update
- run: E005-R-021-e003-screened-wrong-instance-natural-output-attention-n7
- message: R-021绘图失败，R-021b协议不变重跑。

## 2026-07-24T20:52:47+08:00 · run_created
- run: E005-R-021b-e003-screened-wrong-instance-natural-output-attention-n7
- message: Agent 创建 canonical Run E005-R-021b-e003-screened-wrong-instance-natural-output-attention-n7 · E003 screened wrong-instance attention visualization recovery n7

## 2026-07-24T20:53:44+08:00 · run_update
- run: E005-R-021b-e003-screened-wrong-instance-natural-output-attention-n7
- message: R-021b完成：7图，7/7 replay gate通过。

## 2026-07-28T10:11:43+08:00 · run_created
- run: E005-R-022-correct-vs-error-natural-query-attention-matched35x2
- message: Agent 创建 canonical Run E005-R-022-correct-vs-error-natural-query-attention-matched35x2 · correct vs error natural query localization attention matched35x2

## 2026-07-28T10:14:19+08:00 · run_update
- run: E005-R-022-correct-vs-error-natural-query-attention-matched35x2
- message: R-022 pre-forward缺manifest失败，保留并以R-022b恢复。

## 2026-07-28T10:14:20+08:00 · run_created
- run: E005-R-022b-correct-vs-error-natural-query-attention-matched35x2
- message: Agent 创建 canonical Run E005-R-022b-correct-vs-error-natural-query-attention-matched35x2 · correct vs error query attention recovery matched35x2

## 2026-07-28T10:16:46+08:00 · run_update
- run: E005-R-022b-correct-vs-error-natural-query-attention-matched35x2
- message: R-022b pre-forward模型缺失失败。

## 2026-07-28T12:11:24+08:00 · run_created
- run: E005-R-022c-correct-vs-error-natural-query-attention-matched35x2
- message: Agent 创建 canonical Run E005-R-022c-correct-vs-error-natural-query-attention-matched35x2 · correct vs error query attention persistent-model recovery matched35x2

## 2026-07-28T12:22:10+08:00 · run_update
- run: E005-R-022c-correct-vs-error-natural-query-attention-matched35x2
- message: R-022c完成全部forward后汇总变量遮蔽失败。

## 2026-07-28T12:22:11+08:00 · run_created
- run: E005-R-022d-correct-vs-error-natural-query-attention-matched35x2
- message: Agent 创建 canonical Run E005-R-022d-correct-vs-error-natural-query-attention-matched35x2 · R-022c summary-shadow recovery matched35x2

## 2026-07-28T13:00:55+08:00 · run_update
- run: E005-R-022d-correct-vs-error-natural-query-attention-matched35x2
- message: R-022d完成，纠正过强integrity标签：69/70 replay。

## 2026-07-28T13:02:59+08:00 · run_created
- run: E005-R-023-reference-binding-frequency-fiou-matched35x2
- message: Agent 创建 canonical Run E005-R-023-reference-binding-frequency-fiou-matched35x2 · reference target-binding four-state frequency plus token-fIoU curves matched35x2

## 2026-07-28T13:44:18+08:00 · run_update
- run: E005-R-023-reference-binding-frequency-fiou-matched35x2
- message: 补全R-023算法、coverage、完整频率、Wilson、McNemar、paired bootstrap、conditional bootstrap、fIoU AUC和结论边界。

## 2026-07-28T20:13:24+08:00 · run_created
- run: E005-R-024-unseen-multiframe-positive-manifest-n280
- message: Agent 创建 canonical Run E005-R-024-unseen-multiframe-positive-manifest-n280 · unseen70 multiframe4 positive-only n280 manifest

## 2026-07-28T20:13:36+08:00 · run_created
- run: E005-R-025-dualgpu-640-eager-attention-smoke-n5
- message: Agent 创建 canonical Run E005-R-025-dualgpu-640-eager-attention-smoke-n5 · dual RTX4090 max_side640 standard eager attention smoke n5

## 2026-07-28T20:16:40+08:00 · run_created
- run: E005-R-026-unseen-multiframe-natural-generation-n280-640
- message: Agent 创建 canonical Run E005-R-026-unseen-multiframe-natural-generation-n280-640 · natural single-bbox generation positive n280 max_side640

## 2026-07-28T20:16:41+08:00 · run_created
- run: E005-R-027-binding-discrepancy-unseen-multiframe-n280-640
- message: Agent 创建 canonical Run E005-R-027-binding-discrepancy-unseen-multiframe-n280-640 · same-resolution binding discrepancy n280 max_side640

## 2026-07-28T21:11:41+08:00 · run_created
- run: E005-R-028-r023-matched35x2-same-resolution-640
- message: Agent 创建 canonical Run E005-R-028-r023-matched35x2-same-resolution-640 · A R023 matched35x2 archived-natural replay max_side640 with 70 visualizations

## 2026-07-28T22:19:54+08:00 · result_synthesis
- run: E005-R-033-positive-full140-unified-fivepanel-640
- message: 双卡640核心结果归档：原n140最强error signature为Q→Q localization collapse；G→R grounding基本保持；G→R/Q→R discrepancy在matched与expanded分析中未统计稳定。完整公式、指标、结果与路径已写入本地高浓度总结。

{"artifact": "shell/06_experiments/E-005/dual_gpu_640_core_results.md", "configuration": {"gpus": "2xRTX4090 24GB", "max_side": 640, "attention": "standard HF eager", "model": "Qwen3-VL-8B+IPLoc-ID LoRA"}, "metric_definitions": {"G_to_R": "reference bbox p-1 rows x grounding heads -> reference keys", "Q_to_R": "natural query bbox p-1 rows x localization heads -> reference keys", "Q_to_Q": "same natural bbox p-1 rows x localization heads -> query keys", "target_mass": "normalized raw attention mass weighted by fractional GT-cell occupancy", "enrichment": "mean attention density inside fractional GT / outside", "strict_hit": "enrichment>1 AND raw argmax overlaps GT AND GT coverage>=2 merged tokens", "D_abs": "abs(logit(P_GtoR)-logit(P_QtoR))"}, "original_positive_n140": {"groups": {"error": 35, "correct": 76, "partial": 22, "fn": 7}, "GtoR_hit_error_correct": [0.942857, 0.947368], "QtoR_hit_error_correct": [0.257143, 0.342105], "QtoQ_hit_error_correct": [0.142857, 0.960526], "QtoQ_mass_median_error_correct": [0.017503, 0.437874], "QtoQ_enrichment_median_error_correct": [0.662482, 16.00419], "Dabs_median_error_correct": [2.100597, 1.52687], "Dabs_error_minus_correct": 0.573727, "cluster_ci95": [-0.221581, 1.418997], "spearman": {"rho": -0.185973, "p": 0.050671, "n": 111}, "coverage": {"median": 9, "le1": 3, "2_3": 16, "ge4": 121}}, "matched35x2_640": {"state11_error_correct": [9, 13], "state11_rates": [0.257143, 0.371429], "paired_diff_ci_pp": [-11.43, 34.29], "QtoR_mass_paired_median_correct_minus_error": 0.032297, "QtoR_mass_ci95": [0.006042, 0.08811], "GtoR_mass_diff": 0.002858, "GtoR_mass_ci95": [-0.042684, 0.039786], "coverage_median_224_640": [4, 6], "state_stable": 39}, "expanded_n280": {"groups": {"error": 48, "correct": 177, "partial": 45, "rejected": 10}, "Dabs_error_correct": [1.567379, 1.304465], "diff": 0.262913, "cluster_ci95": [-0.348299, 0.986894], "spearman": {"rho": -0.037438, "p": 0.576404, "n": 225}, "coverage_median": 8, "unalignable": 0}, "negative_n140": {"tn": 136, "fp": 4, "boundary": "candidate IoU is not personalized localization correctness"}, "visualizations": {"positive": 140, "negative": 140, "layout": ["reference clean", "G->R", "Q->R", "Q->Q", "query clean GT+pred"], "naming": "presentation/by_behavior"}, "conclusion": "Strongest error-associated attention signature is Q->Q query localization collapse, not loss of G->R grounding. G->R/Q->R discrepancy is directional but statistically unstable across matched and expanded analyses.", "boundaries": ["attention-derived non-causal", "archived-output teacher replay", "not identity selective", "paper did not disclose max_side", "local reconstructed split"]}

## 2026-07-28T22:20:42+08:00 · run_created
- run: E005-R-028-r023-matched35x2-same-resolution-640
- message: Agent 创建 canonical Run E005-R-028-r023-matched35x2-same-resolution-640 · matched35x2 same-resolution640 attention and visualization

## 2026-07-28T22:20:42+08:00 · run_created
- run: E005-R-029c-original140-positive-targets-binding-640
- message: Agent 创建 canonical Run E005-R-029c-original140-positive-targets-binding-640 · original E003 positive n140 same-resolution640 binding audit

## 2026-07-28T22:20:42+08:00 · run_created
- run: E005-R-030c-original140-negative-targets-binding-640
- message: Agent 创建 canonical Run E005-R-030c-original140-negative-targets-binding-640 · original E003 same-class negative n140 separate640 diagnostic

## 2026-07-28T22:21:10+08:00 · run_created
- run: E005-R-033-positive-full140-unified-fivepanel-640
- message: Agent 创建 canonical Run E005-R-033-positive-full140-unified-fivepanel-640 · full original n140 positive unified five-panel640 visualizations

## 2026-07-28T22:21:10+08:00 · run_created
- run: E005-R-033-negative-full140-unified-fivepanel-640
- message: Agent 创建 canonical Run E005-R-033-negative-full140-unified-fivepanel-640 · full original n140 negative unified five-panel640 visualizations

## 2026-07-28T23:12:15+08:00 · run_created
- run: E005-R-034-qr-continuous-threshold-curve-offline-640
- message: Agent 创建 canonical Run E005-R-034-qr-continuous-threshold-curve-offline-640 · offline Q→R curve analysis first implementation

## 2026-07-28T23:12:15+08:00 · run_created
- run: E005-R-034b-qr-continuous-threshold-curve-offline-640
- message: Agent 创建 canonical Run E005-R-034b-qr-continuous-threshold-curve-offline-640 · pure numpy recovery

## 2026-07-28T23:12:15+08:00 · run_created
- run: E005-R-034d-qr-continuous-threshold-curve-offline-640
- message: Agent 创建 canonical Run E005-R-034d-qr-continuous-threshold-curve-offline-640 · final frozen Q→R continuous threshold fIoU analysis

## 2026-08-17T12:53:40 · agent_run_grouping
- run: -
- message: Agent Folder 整理：已分类 8，跳过 0，未变 0

```json
{
  "applied": [
    {
      "run_id": "E005-R-028-r023-matched35x2-same-resolution-640",
      "from": "",
      "to": "resolution-stability"
    },
    {
      "run_id": "E005-R-029c-original140-positive-targets-binding-640",
      "from": "",
      "to": "positive-binding-audit"
    },
    {
      "run_id": "E005-R-030c-original140-negative-targets-binding-640",
      "from": "",
      "to": "negative-binding-audit"
    },
    {
      "run_id": "E005-R-033-positive-full140-unified-fivepanel-640",
      "from": "",
      "to": "unified-visualization"
    },
    {
      "run_id": "E005-R-033-negative-full140-unified-fivepanel-640",
      "from": "",
      "to": "unified-visualization"
    },
    {
      "run_id": "E005-R-034-qr-continuous-threshold-curve-offline-640",
      "from": "",
      "to": "offline-threshold-curve"
    },
    {
      "run_id": "E005-R-034b-qr-continuous-threshold-curve-offline-640",
      "from": "",
      "to": "offline-threshold-curve"
    },
    {
      "run_id": "E005-R-034d-qr-continuous-threshold-curve-offline-640",
      "from": "",
      "to": "offline-threshold-curve"
    }
  ],
  "skipped": [],
  "unchanged": [],
  "groups_added": [
    {
      "id": "resolution-stability",
      "name": "分辨率稳定性复核",
      "description": "复核 R023 的 224 replay 方向在 640 分辨率下是否保持，检验 paired resolution stability",
      "color": "#4F7C78"
    },
    {
      "id": "positive-binding-audit",
      "name": "正样本绑定审计",
      "description": "在原始 positive 目标上检验 G→R/Q→R discrepancy 与自然定位 IoU 的关系",
      "color": "#3B6EA5"
    },
    {
      "id": "negative-binding-audit",
      "name": "负样本绑定诊断",
      "description": "单独审计 same-class negative 的自然拒绝/接受与 reference lookback 行为",
      "color": "#B5651D"
    },
    {
      "id": "unified-visualization",
      "name": "统一五面板可视化",
      "description": "按自然行为命名提供完整 G→R/Q→R/Q→Q 统一可视化",
      "color": "#7A4B94"
    },
    {
      "id": "offline-threshold-curve",
      "name": "离线 Q→R 阈值曲线",
      "description": "离线分析 Q→R 连续指标、阈值曲线与 distributed reference-target attention signal",
      "color": "#C05780"
    }
  ],
  "totals": {
    "applied": 8,
    "skipped": 0,
    "unchanged": 0,
    "groups_added": 5
  }
}
```
