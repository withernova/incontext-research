# state.md

state: E002_PLANNING
iteration: 1
budget:
  max_iterations: 3
  max_wall_seconds: 600
blockers:
  - E-002 需要确认 `iplocid` 官方仓库、数据构造脚本与最小模型是否可访问。
next_actions:
  - 阅读并核验 `personal2026` 的官方代码/数据链接。
  - 参考 `shell/06_experiments/E-002/base_repo_comparison.md` 选择 E-002 主 base repo。
  - 创建 E-002 远程目录：`/home/featurize/work/mechanism/explog/E-002` 与 `/home/featurize/work/mechanism/Rex-Omni/tmp/e002`。
  - 先做 R-001 POIL dataset acquisition / format inspection，不立即训练或跑大规模推理。
  - 基于 POIL manifest 再运行 R-002 localization-only baseline 与 R-003 prompt-only self-posed identification baseline。
last_updated: 2026-07-16T15:00:00+08:00

## 阶段历史（append-only）
- 2026-07-09T15:31:09 | AWAIT_INTAKE | 创建项目骨架
- 2026-07-09T15:31:09 | MATERIALIZE | INTAKE 解析 -> context/idea/AGENTS 已写入
- 2026-07-13T00:00:00 | E001_SUMMARY | E-001 containerization 阶段性收束，写入 `shell/06_experiments/E-001/final_summary.md`
- 2026-07-13T00:00:00 | E002_PLANNING | 新建 E-002：使用 Personalize / POIL 数据集与协议
## 2026-07-13 E-002 mechanism clarification
- User clarified: E-002 aims to test whether IPLoc/MLLM bottleneck is insufficient use of object-internal visual-token detail/order, not merely POIL rejection.
- Patch-level perturbation is only a proxy; token-level visual-embedding intervention is the mechanism-critical experiment and must be distinguished.
- Added plan: `shell/06_experiments/E-002/internal_token_mechanism_plan.md`.
- Hard samples should be mined using model visual-layer object-token similarity: same category, similar silhouette, high unordered internal-token similarity, but different identity/order-aware structure.
- 2026-07-13 | E002_MECHANISM_PROTOCOL | Read Mechanisms of Object Localization paper. Token interventions should follow: mask-to-token-grid by any overlap, LLM-input intervention after multimodal projection, global-average embedding ablation, object-token shuffle vs full shuffle, copy-padding/container extension, and global/local view separation when applicable.
- 2026-07-16 | E003_CREATED | 将 Joint F1@IoU 与 forced-candidate verifier 从 E-002 独立为 E-003。E-002 保留 hidden-token/container mechanism；E-003 检验 identification-only F1 是否与 localization correctness 解耦并高估 joint task success。
- 2026-07-16 | E003_R001 | 重建本地 LaSOT POIL manifest：140 samples / 70 classes / 140 positive + 140 same-class negative，missing=0、invalid bbox=0；非官方 split。
- 2026-07-16 | E003_R002_FAILED | 首次 Joint F1 n140 因 Torch/Transformers 不兼容导致所有 processor 调用失败，零有效记录；run 保留为 failed audit，不得引用。
- 2026-07-16 | ARCHIVE_RECENT_RUNS | 按 ledger_filling_skill 审计归档 E-002 R-010–R-015（含 R-014b/R-014c）与 E-003 R-001–R-004b；明确记录 failed/aborted/smoke/main 状态、exact remote paths、R-014c geometry caveat 与 E003 Joint F1 结论边界。
- 2026-07-16 | E003_R005_R005D_AUDIT | Forced-candidate pilot 连续暴露三类实现问题并均保留独立失败/中止 run：R-005 缺 PYTHONPATH；R-005b 的 PN_interpreter bbox fallback 会伪造 positive；R-005c user-turn candidate 未形成 assistant prefix；R-005d assistant prefix 可生成 Yes/No 但自由文本有歧义/unparsed。下一版改为 next-token Yes-vs-No logit probe；不得引用上述中止 run 的科学指标。
- 2026-07-16 | E004_CREATED | Q-001 推论归档并新建 E-004 reference-conditioned causal token routing。已完成 Qwen3-VL module audit（36层/32 Q heads/8 KV heads/head_dim128），构建4个 synthetic double-instance quartets，并启动 E004-R-001 behavioral gate；synthetic结果仅用于实现 sanity，正式机制结论要求真实同图双实例。
- 2026-07-20 | E003_R005E_AUDIT | R-005e 写出240条 finite logit records 且实际12个 role/mode cell 各20条，但脚本 post-output gate 错把 positive role 的 mode 要求为 annotated_distractor（实际为 annotated_target），末尾 AssertionError 且无正式 analysis；保留为 failed_post_output_integrity_assertion，修复须用新 run id。
- 2026-07-20 | E004_R000_R001_AUDIT | R-000 完成 Qwen3-VL head-hook module audit；R-001 synthetic 2×2 behavioral sanity 为9/16、0/4 quartets全对，behavioral gate failed，不进入科学 head scan。
- 2026-07-20 | SURVEY_TOOL_SYNC_BLOCKED | 已通过 surveyctl 在 E-002 记录同步 blocker；当时工具无 experiment-create，run create E-003 返回 not found，故 E-003/E-004 canonical runs 暂不能写入 registry；未直接编辑 `.survey-tool/`。
- 2026-07-20 | SURVEY_TOOL_SYNC_RECOVERED | surveyctl 新增 experiment create 后，已通过公开接口创建 E-003/E-004。E-003 同步10条 runs（R-001–R-005e，含 failed/aborted/smoke/main）；E-004 同步R-000 module audit与R-001 completed_gate_failed。未直接编辑 `.survey-tool/`。
- 2026-07-20 | CANONICAL_RUN_REKEY | 工具新增canonical run-ID约束后，已用 `surveyctl run rekey --adopt-existing-note` 将E-003/E-004全部历史自动R-ID迁移为与真实目录和note一致的descriptive IDs；不再使用variant/notes旁路映射。
- 2026-07-20 | E003_DETAILED_AUDIT_REGISTRATION | 新增 `evaluation_audit_rationale.md` 与 `experiment_audit_notes.md`；明确论文任务定义→component metrics→joint-metric coverage gap的证据链、Joint F1计数规则、官方/本地边界、forced-candidate gate与论文级结论升级条件。工具内主run/R-005e及R-001–R-004已补充necessity、evidence basis、data definition、model config、metric definition、integrity gates、limitations、claim boundary和audit paths。
- 2026-07-20 | SURVEY_TOOL_CROSS_PROJECT_AUDIT_SCHEMA | 更新共享survey-tool：Run CLI/schema/canonical note新增必要性、研究依据、数据身份、模型配置、变量对照、指标定义、完整性gate、局限、claim边界、审核入口；DATA_CONTRACT加入no-silent-zero与evaluation-audit约束；`result.md`新增不会被run更新覆盖的canonical详细审计正文区。
- 2026-07-21 | E003_R006_REJECTION_LINKED_BBOX_AUDIT | 完成140-pair离线geometry/低IoU可视化审计。35个IoU<0.1 positive TP与paired negative prediction/annotation并不比same-class swap更近（negPred delta=+0.0353,p_lower=0.918；negGT delta=+0.0152,p_lower=0.664），原“跨图像paired rejected bbox接近”假设未支持。辅助发现83/140 negative candidates IoU>=0.5，其中82个最终No，说明模型经常能定位同类distractor后拒绝identity，与sequential design相容。35张图提示下一步应直接标注positive图像内wrong-instance，而非用跨图像坐标相似替代identity证据。attempt-001/002失败日志均保留。
- 2026-07-21 | Q003_SAME_IMAGE_INSTANCE_BINDING | 登记Q-003。核验论文§3.5与公开LaSOT/VastTrack/GOT-10K/PDM manifests/scripts：所有正式negative均为独立query image；公开T2 manifest中positive-negative同路径及同sequence均为0。不能据此断言图像物理上绝无其他实例，但benchmark没有显式candidate-level同图消歧cell。论文§5承认single-object/multi-object limitation，却未直接讨论`Yes + wrong-instance bbox`、candidate-answer consistency或F1的同图instance-binding覆盖缺口。
- 2026-07-21 | E003_R010_SAME_IMAGE_BINDING_GATE_FAILED | natural same-image wrong-instance n7 pilot完成工程运行：21 records/7×3、finite、7张图。审计发现4个`.incomplete`命名文件实际是key-complete valid safetensors并恢复symlink；旧manifest路径也由R-004b归档副本修复。科学replay gate仍失败：R-004b 7/7自然Yes，但exact source wrong-prefix截至`?`、正确评分leading-space ` Yes`=7414/` No`=2308后仅1/7 Yes。故target/wrong margin不可解释，run=`completed_gate_failed`。同时确认R-005e曾在trailing-space prefix后错误评分9454/2753，其logits不可引用；下一步先做模型/LoRA/chat-token/image-tensor exact replay对齐。
- 2026-07-20 | E004_METHOD_CORRECTION | 用户指出 head 发现应严格参照 Mechanisms 论文的 object-present source / object-removed base causal mediation，而非仅用 zero ablation。确认 R-007 只是 layer-output ablation diagnostic，不是 CMA/MF；后续正式 head 排名改为逐 head source→base head-output activation patching、teacher-forced gold-token perplexity MF、source/base行为与token对齐gate、held-out cumulative ablation，并增加双向 reference-switch CMA 排除统一 Yes/No polarity。
- 2026-07-20 | E004_R008_R009 | R-008 neutral-fill controlled object-removal proxy gate 完成：16/16 token/grid aligned、8 broad gap、6 strict source-correct/base-wrong。R-009 layer-level source→base activation-patching recoverability pilot 完成216/216 records并通过 gate；L18 mean MF=0.728、median=0.879、positive=6/6，L16 mean受max MF=12.753极值影响。该结果仍是 deepstack-uncontrolled、all-sequence-position、neutral-fill proxy，不是per-head或identity-routing证据。
- 2026-07-20 | E004_R010_PASSED | single-pair/single-head activation-patching correctness smoke 通过（tmux `e004_head_patch_smoke`，正常status 0 retained pane）：source/base重复、no-op、full-layer重复、single-head重复和32个head slices=full-layer patch的max abs diff均为0，finite=true。L18 full-layer MF=0.969；head0 MF=-0.141仅为工程测试值，不构成head证据。下一科学流程仍需官方LaMa base、严格prompt-position审计及discovery/evaluation split。
- 2026-07-20 | E004_R011_AND_REGISTRY_SYNC | 官方LaMa仓库已固定至`advimman/lama@786f5936b27fb3dacd2b1ad799e4de968ea697e7`，remote匹配且dirty=0；checkpoint与inpainting尚未执行。通过`surveyctl.py`公开接口成功补登记E004 R-006至R-011，E-004 registry现共8条canonical runs（R-000、R-001、R-006–R-011）；未直接编辑`.survey-tool/`。
- 2026-07-21 | Q003_MANIFEST_BIDIRECTIONAL_AUDIT | 全量公开T2 manifest进一步审计同一query是否被不同reference identity复用。LaSOT/VastTrack均0；PDM虽有重复query但reference set不变；GOT-10K各shot有3个跨reference复用，但均是同一单目标frame对自身reference为positive、对无关类别reference为out-class negative，不是同图A/B candidate四格。LaSOT train有28对跨不同query images的reciprocal sequence-level negatives，也不是固定query(A,B)的candidate A/B switch。故可确定公开manifest未显式构造/计分双向同图identity-binding；这仅是评测覆盖判断，不证明模型失败或source frame无额外实例。
- 2026-07-21 | E003_BACKGROUND_DESIGN_REMOVED | 用户复核后，从后续E-003科学设计完全删除background candidate；主实验唯一设计为真实`ref A/B × candidate A/B`四格。R-010历史产物不删除但标为废弃且replay-gate failed；R-011 attempt-001因generation trimming实现错误在0 scientific records处失败，run标记aborted且不重试。
- 2026-07-21 | E003_R007_IOU_CURVE_BOOTSTRAP | 完成现有n140上的离线Joint F1–IoU完整阈值曲线，不扩充数据集。τ=0.00..1.00步长0.01；140个positive/negative pair按sample聚类做10,000次bootstrap（seed=20260721）。Identification F1=0.9603 [0.9348,0.9819]；Joint F1@0.3/0.5/0.7=0.8050 [0.7468,0.8583] / 0.7639 [0.6996,0.8216] / 0.6909 [0.6161,0.7598]；对应paired F1 gap CI均不含0。所有gate通过并严格复现R-004b三个注册点。attempt-001因cluster子字段索引错误在任何科学summary前失败，日志单独保留。曲线为本地非官方split的evaluation-coverage evidence，不证明wrong-instance或机制。
