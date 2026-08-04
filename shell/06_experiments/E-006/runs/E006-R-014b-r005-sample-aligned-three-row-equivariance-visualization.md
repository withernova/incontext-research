# E006-R-014b-r005-sample-aligned-three-row-equivariance-visualization · r005-sample-aligned-three-row-equivariance-visualization

- canonical_run_id: `E006-R-014b-r005-sample-aligned-three-row-equivariance-visualization`
- run_type: hypothesis_test
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-03T20:07:03
- approved_at: 2026-08-03T20:12:21
- execution_authorized_at: 2026-08-03T20:11:24
- execution_authorization_consumed_at: 2026-08-03T20:14:20
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
completed

## 本轮目的
在E006-R-005原始positive-extremes样本上，以identity、REF-only和QUERY-only三行配对attention图直接检验Q→R是跟随reference目标，还是简单复制query空间分布；同时修复R-014可视化框坐标缩放与历史/当前行为命名混淆。

## 必要性 / 证据链位置
R-014使用fresh R-027/R-010 confirmation样本而非R-005原始n111，不能逐样本支撑R-005；其PNG还把原图bbox直接画到max_side=640显示图上，导致部分绿色/红色/洋红框错位，并仅以历史分组命名，可能与当前自然预测相反。需要独立canonical run，禁止覆盖R-014。

## 研究依据 / 被审计对象
E006-R-005冻结positive localization-error n35与localization-correct n76及historical main4=L18H15,L19H03,L22H00,L20H08；E006-R-014已验证单GPU 48GB、max_side=640、同forward bbox p-1 Q→Q/Q→R提取链并产生120/120可解析自然bbox，但当前展示合同不满足用户逐条件比较需求。

## 实现方式（简版）
从R-005原始n111中按冻结规则选6 localization-correct和6 localization-error、sequence-unique；每个样本运行identity、REF-only HFlip/VFlip/R180、QUERY-only HFlip/VFlip/R180的真实自然生成与teacher replay。每种transform输出一张三行四列主图：identity行、REF-only行、QUERY-only行；四列固定为reference+GT、query+GT+natural prediction、main4 Q→Q、main4 Q→R。

## 实现方式（详细版）
每个条件先真实自然生成，保留Yes/No/parse失败和自然bbox；可解析输出以exact bbox token p-1 rows teacher replay，同一forward提取Q→Q与Q→R。主图按HFlip/VFlip/R180分别生成，合计12×3=36张；每行注明Yes/No、IoU与当前prediction-correct/partial/error/rejected/parse-failed。绿色=当前GT，红色=当前自然预测；所有框必须从原图坐标按实际display/model-input尺寸独立缩放，reference/query各自审计。四个per-head图和projected-Q→Q/difference map仅作appendix，不挤占主图。不得从结果重选head、样本或transform。

## 数据身份与构造
严格使用E006-R-005对应的原始E003-R-004b positive target manifest：localization-error IoU<0.1 n35与localization-correct IoU>=0.7 n76；不用R-027 unseen280替代。按sha256(seed:sequence:index)在每组先取sequence-unique 6条，冻结12条。历史组仅作审计字段；图标题与文件名主要按本次每条件自然输出行为命名。

## 数据规模
12个sequence-unique样本；每样本7个条件（identity + REF-only三变换 + QUERY-only三变换）=84次自然生成及最多84次teacher replay；36张三行四列主图；per-head appendix最多84组。

## 模型、权重与关键配置
Qwen3-VL-8B-Instruct + IPLoc-ID 1-shot LoRA；bf16；attn_implementation=eager；output_attentions=True；max_side=640最长边上限；冻结main4=L18H15,L19H03,L22H00,L20H08；优先单RTX4090 48GB max_memory={0:46GiB}，模型路径与LoRA路径执行前重新核验。

## 变量、干预与对照
自变量为REF-only与QUERY-only的HFlip/VFlip/R180；identity为配对基线。REF-only同时变换reference图像和reference GT/prompt bbox，query保持不变；QUERY-only变换query图像及query GT，reference保持不变。相同样本、相同head、相同自然bbox阶段定义；不含BOTH主图。

## 指标与计数规则
每条件记录natural Yes/No、parse、bbox、IoU和当前行为标签：correct=Yes且IoU>=0.7，partial=Yes且0.1<=IoU<0.7，error=Yes且IoU<0.1，rejected=No，parse-failed单列。attention继续记录P_QR(R_t/R_0/Q_t→R)、S50、Q→R vs projected-Q→Q Pearson/Spearman/JSD/COM/peak；统计按sequence配对bootstrap B=10000。主交付首先是可审计的配对真实图。

## 完整性门槛 / no-silent-zero
1) 样本必须来自R-005 n111且两组各6、sequence唯一；2) 84个条件逐项记录，失败不得用identity bbox替代；3) exact bbox token连续唯一匹配及p-1 row；4) Q→Q/Q→R同一forward；5) reference/query原图尺寸、processor/display尺寸、缩放系数和变换后bbox逐项写manifest；6) 至少人工/程序检查四角与非640原图框缩放；7) 36张主图齐全或列出失败；8) 冻结main4，不后验挑图；9) R-014产物保持不变。

## 竞争假设与预期特征
若REF-only后Q→R随R_t移动，而QUERY-only后Q→R保持于固定reference目标/R_0，并且Q→Q随query变换，则削弱简单query-map/coordinate-copy解释并支持reference-region tracking signature；若QUERY-only的Q→R随Q_t→R移动且REF-only不跟R_t，则支持copy signature；允许mixed或inconclusive。

## 验收条件
提交36张可直接横向比较的3×4主图及manifest/raw metrics；任取非640原图样本时绿色GT和红色预测在display图上的坐标与数值缩放一致；每行明确当前prediction status与IoU；identity、REF-only、QUERY-only使用同一原始样本；完成sequence-paired汇总，不以视觉挑选代替全量统计。

## 依赖的 Run / 证据
依赖E006-R-005原始样本清单与attention角色定义、E006-R-006 alignment gate、E006-R-013/R-014已验证的自然生成+teacher replay实现；执行前需从R-014代码分支复制并修复可视化，不修改冻结上游产物。

## 观测结果摘要
exit=0，GATE_PASS；84/84自然生成与同forward bbox p-1 replay成功，0 parse failure；36/36主图、84 appendix。REF-only按sequence对三transform取均值后，P_QR(R_t)-P_QR(R_0) median=+0.01468，95% paired bootstrap CI[-0.02155,+0.06075]，8/12为正；分transform仅VFlip CI排除0。QUERY-only的P_QR(R_0)-P_QR(Q_t→R) sequence-mean median=+0.03066，CI[-0.01503,+0.07831]，7/12为正。总体为弱/混合reference-region tracking signature。

## 局限与混杂因素
attention-derived、teacher-replayed、非因果；REF-only同时变化reference视觉内容与prompt bbox，仍不能区分视觉内容追踪和reference bbox坐标寻址；12个sequence规模有限；flip可能OOD；即使跟随reference也不证明identity-selective understanding。

## 可支持的结论
本run一定程度削弱“query bbox阶段完全不看reference”和“Q→R只是直接复制Q→Q/query坐标图”两种强表述，但由于sequence n=12、整体CI跨0，只能称弱/混合空间签名，不能称问题已解决。结合R-010，correct/error的top10非GT selection head排序在T→R和B→R完全重合、B→Q高度重合(0.818)，说明“correct/error使用完全不同head集合”这一简单解释已明显减弱；T→Q仅0.429且该结果尚非fresh冻结head因果验证。

## 不支持的结论 / Claim 边界
仅判断冻结query heads的Q→R空间签名是否更符合reference-region tracking、query-map/coordinate copying、mixed或inconclusive，并提供与R-005样本对齐的展示。不得声称因果机制、identity-selective binding、模型独立理解reference或行为改进。

## 关键指标
{"exit_code":0,"gate":"GATE_PASS","n_design":84,"n_ok":84,"n_failed":0,"main_figures":36,"appendix_figures":84,"parse_failed":0,"current_behavior":{"correct":36,"partial":13,"error":31,"rejected":4},"ref_only_sequence_mean_median":0.0146841432,"ref_only_ci95":[-0.0215546022,0.0607504917],"ref_only_positive":8,"query_only_fixed_R0_preference_median":0.0306631853,"query_only_ci95":[-0.0150321908,0.0783100553],"query_only_positive":7}

## Artifacts
metrics.json; analysis/summary.json; manifests/fixed_design.json; manifests/visualization_manifest.json; artifacts/records_checkpoint.json; artifacts/maps/*.npz; visualizations/main/*.png (36); visualizations/appendix_per_condition/*.png (84)

## 审核入口
shell/06_experiments/E-006/result.md; shell/06_experiments/E-006/runs/E006-R-005-simple-top50-support-components-positive-extremes-n111-640.md; shell/06_experiments/E-006/runs/E006-R-014-qtor-reference-vs-query-coordinate-equivariance.md; /home/featurize/work/mechanism/explog/E-006/E006-R-005-simple-top50-support-components-positive-extremes-n111-640/; /home/featurize/work/mechanism/explog/E-006/E006-R-014-qtor-reference-vs-query-coordinate-equivariance/

## 过程记录与补充细节
实际执行命令、代码、日志与tmux路径见canonical note的解析后执行环境；本地统计图见shell/06_experiments/E-006/visualizations/R-014b/。

## Run 审核
### 用户补充要求
（待补充）
### 用户疑问
（待补充）
### Agent 完善说明
（待补充）
### Agent 对疑问的回应
（待补充）
### 本次执行授权备注
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
（待补充）

### 配置/超参数
（待补充）

### Seed
20260728

### 日志路径
（待补充）

### 产物目录
（待补充）

### 真实产物根目录
（待补充）

### tmux session
（待补充）

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-006
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-014b-r005-sample-aligned-three-row-equivariance-visualization
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-014b-r005-sample-aligned-three-row-equivariance-visualization/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-014b-r005-sample-aligned-three-row-equivariance-visualization/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-014b-r005-sample-aligned-three-row-equivariance-visualization/metrics.json
- tmux_session: incontext-E-006-E006-R-014b-r005-sample-aligned-three-row-equivariance-visualization
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-03T20:06:43
- updated: 2026-08-03T20:39:43

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
