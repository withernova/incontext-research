# E006-R-014c-prediction-projection-expanded-equivariance-audit · prediction-projection-expanded-equivariance-audit

- canonical_run_id: `E006-R-014c-prediction-projection-expanded-equivariance-audit`
- run_type: hypothesis_test
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-04T15:30:31
- approved_at: 2026-08-04T15:41:51
- execution_authorized_at: 2026-08-04T15:41:53
- execution_authorization_consumed_at: 2026-08-04T15:46:45
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
completed

## 本轮目的
修正R-014b只用query GT投影作为洋红候选的缺漏：直接检验模型当前自然query预测框的归一化坐标投影到reference后，Q→R是否跟随该预测投影；同时扩大冻结可视化与统计样本。

## 必要性 / 证据链位置
R-014b的Q_t→R由query GT投影，只能检验GT/几何候选，不能直接回答模型是否复制自己的自然预测位置。若研究prediction-copy，必须把每个条件自己的natural predicted query bbox投影到reference。R-014b n=12且整体sequence CI跨0，扩大到R-005全部111个sequence-unique positive extremes可提高展示覆盖与区间稳定性。

## 研究依据 / 被审计对象
R-014b 84/84成功并保存自然pred_bbox、current query/reference dimensions和raw Q→R/Q→Q maps；其main Q→R列未画projected candidate，appendix洋红Q→R candidate来自query GT而非prediction。R-005有76 correct+35 error，111 records且sequence唯一，可作预冻结全量。

## 实现方式（简版）
使用R-005全部111条positive extremes，每条运行identity、REF-only HFlip/VFlip/R180、QUERY-only HFlip/VFlip/R180的真实自然生成和同forward bbox p-1 replay；新增P_t→R=当前条件natural predicted query bbox按当前query/reference原始尺寸归一化投影。主图同时画GT投影和prediction投影，统计Q→R对R_t/R_0/GT_t→R/P_t→R的mass、S50与距离。

## 实现方式（详细版）
颜色固定：绿色=current GT；红色=current query natural prediction；洋红=current query GT projected to reference（保留R-014b语义）；蓝色=current natural prediction projected query→reference（新增核心候选）。若current natural response No或bbox parse失败，蓝框严格缺失并标注，不得借用identity或GT。每条件从自己的自然输出构造P_t→R。Q→Q与Q→R仍来自同一teacher-replay forward、exact bbox token p-1 rows、frozen main4。主图扩为每transform 3×5：Reference+GT+两投影候选；Query+GT+prediction；Q→Q；Q→R+候选；Q→R−projected(Q→Q) difference。另输出每样本7-condition overview、每head appendix和全量统计图。

## 数据身份与构造
严格复用E006-R-005 original positive-extremes n111：localization-correct 76、localization-error 35，现已核验111 records对应111 distinct sequence；不另挑样本。historical group仅作分层，当前行为由每条件Yes/IoU重新命名。

## 数据规模
111 samples×7 conditions=777自然生成及最多777 teacher replays；333个transform主图（111×3）；111个7-condition overview；最多777 appendix；不含BOTH。若单次模型驻留执行，预计约R-014b的9.25倍，需顺序checkpoint与可恢复分片。

## 模型、权重与关键配置
Qwen3-VL-8B-Instruct + IPLoc-ID 1-shot LoRA；bf16 eager；output_attentions=True；max_side=640；frozen main4=L18H15,L19H03,L22H00,L20H08；单RTX4090，按当前服务器实际24GB使用22GiB max_memory并必要时CPU offload，但不得改分辨率。

## 变量、干预与对照
REF-only共同变换reference image与prompt bbox；QUERY-only共同变换query image与query GT。identity配对基线。同一sample/head/row/processor控制。prediction投影P_t→R和GT投影G_t→R分栏，避免把oracle GT复制和model prediction复制混称。

## 指标与计数规则
Primary prediction-copy contrast：QUERY-only下P_QR(P_t→R)-P_QR(R_0)，并与P_QR(G_t→R)-P_QR(R_0)并列；fractional mass、S50、pointing、COM/peak distance。计算Q→R与projected Q→Q Pearson/Spearman/JSD。REF-only继续P_QR(R_t)-P_QR(R_0)。按sequence对transform取均值后paired bootstrap B=10000；historical correct/error仅分层、不独立挑head。另按current correct/partial/error/rejected/parse-failed报告。

## 完整性门槛 / no-silent-zero
1) n=111且sequence unique=111；2) design=777，无静默缺失；3)每条件使用自己的natural prediction，No/parse失败无蓝框；4)P_t→R用当前条件query/reference原始尺寸归一化投影，并分别记录display scaling；5)exact bbox IDs唯一且p-1；6)Q→Q/Q→R同forward；7)main4/sample/transform冻结；8)R-014b/R-014不覆盖；9)先程序检查投影可逆性和identity P投影；10)统计按sequence而非777独立。

## 竞争假设与预期特征
若QUERY-only Q→R显著偏向蓝色P_t→R且与projected Q→Q高相似，支持模型prediction/query-map copy signature；若仍偏R_0且远离蓝框，进一步削弱prediction-copy；若只偏洋红GT投影而不偏蓝框，提示GT几何/目标位置与模型预测位置需分开；允许mixed及按行为分层异质性。

## 验收条件
777条件完整或逐项列失败；333张3×5主图、111 overview；蓝/洋红图例明确且数值manifest可复算；给出全量sequence-bootstrap及correct/error分层；输出prediction-copy/reference-tracking/mixed/inconclusive判定。

## 依赖的 Run / 证据
依赖R-005 n111、R-006 row alignment、R-014b已验证生成/replay/scaling代码；须复制到新run，不修改已完成R-014b。当前R-009可继续独立运行，R-014c不得并发抢占同一GPU。

## 观测结果摘要
exit=0；777/777 natural conditions完成，776 teacher replays成功，1个真实自然输出仅二维点而parse-failed；main figures=332/333，overview=110/111，appendix=776。REF-only sequence mean P_QR(R_t)-P_QR(R_0) median=.02284, CI[.01724,.03340]；QUERY-only prediction-projection P_QR(P_t→R)-P_QR(R_0) median=-.000616, CI[-.01808,.02349]。

## 局限与混杂因素
attention-derived、teacher replay、非因果；natural predicted bbox可能与GT高度相关造成候选重叠；REF-only仍混合图像与prompt bbox变换；flip OOD；777 forwards成本高；即便蓝候选命中也不能区分坐标复制和更一般query-conditioned routing。

## 可支持的结论
扩大到111个sequence后，固定main4的Q→R对联合变换后的reference target呈正向attention-mass偏好；QUERY-only不跟随当前自然prediction投影，因而不支持直接prediction-coordinate copy。仍为attention-derived、REF image+bbox联合变换、非因果，且1个自然parse failure被如实保留。

## 不支持的结论 / Claim 边界
最多判断冻结main4的Q→R空间签名是否跟随模型自身prediction projection，而非证明因果复制、identity understanding或训练效果。R-014b历史结论保持不变，新结果独立报告。

## 关键指标
{"exit_code":0,"n_design":777,"n_ok":776,"n_failed":1,"parse_failed":1,"main_figures":332,"overview_figures":110,"appendix_figures":776,"ref_only_sequence_median":0.022839472025801624,"ref_only_ci95":[0.017241721963701252,0.033404342560741214],"query_prediction_projection_sequence_median":-0.0006159337667415657,"query_prediction_projection_ci95":[-0.01807702570087052,0.0234938389689921]}

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-006/runs/E006-R-014b-r005-sample-aligned-three-row-equivariance-visualization.md; /home/featurize/work/mechanism/explog/E-006/E006-R-014b-r005-sample-aligned-three-row-equivariance-visualization/config/e006_r014b_run.py; /home/featurize/work/mechanism/explog/E-006/runs/E006-R-005-simple-top50-support-components-positive-extremes-n111-640/analysis/summary.json

## 过程记录与补充细节
（待补充）

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
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-014c-prediction-projection-expanded-equivariance-audit
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-014c-prediction-projection-expanded-equivariance-audit/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-014c-prediction-projection-expanded-equivariance-audit/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-014c-prediction-projection-expanded-equivariance-audit/metrics.json
- tmux_session: incontext-E-006-E006-R-014c-prediction-projection-expanded-equivariance-audit
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T15:30:31
- updated: 2026-08-04T17:25:21

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
