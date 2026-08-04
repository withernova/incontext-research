# E007-R-004b-fresh-top3-mapping-family-joint-f1-n140 · fresh-top3-mapping-family-joint-f1-n140

- canonical_run_id: `E007-R-004b-fresh-top3-mapping-family-joint-f1-n140`
- run_type: post_selection_fresh_causal_behavior_evaluation
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-04T22:44:35
- approved_at: 2026-08-04T22:46:08
- execution_authorized_at: 2026-08-04T22:46:10
- execution_authorization_consumed_at: 
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
draft

## 本轮目的
在fresh sequence-disjoint 70 positive+70 same-class negative上评估R-003c冻结的至多Top-3 mapping变体，报告自然mIoU、Identification F1和Joint F1，并检验是否存在matched-control特异性。

## 必要性 / 证据链位置
旧n20既小又用于算法探索；只有fresh正负大样本才能判断候选是否泛化、是否以损害negative rejection换取positive定位，并提供完整Joint F1。

## 研究依据 / 被审计对象
E-003已显示Identification F1与Joint F1存在明显差距；R-003b当前full-L1没有自然rescue。大样本必须评估预冻结候选而非继续在fresh数据上调参。

## 实现方式（简版）
R-003c结束后机器读取其冻结Top-3（不足则按实际合格数量），在构建前未用于E-007调参的fresh sequences上运行baseline、identity、Top-3、current-A、R180、mismatched、uniform_bbox；每个condition从相同原prompt独立自然生成。positive和same-class negative均评估Yes/No；positive bbox计mIoU，完整数据计Identification/Joint F1。

## 实现方式（详细版）
候选公式和超参逐字继承R-003c conditions.json，不得在fresh结果后修改。source maps对每case从其prompt reference bbox rows重算；mismatched donor预先按label、category和sequence约束冻结，无法匹配时使用预注册全局cyclic donor并单列。所有shape-only条件保持当前row/head alpha、非R不变、target V不变；不探索alpha增益、heads或window。baseline/identity和所有条件保存完整response/token/parser/rewrite audit。

## 数据身份与构造
冻结70个此前未进入E007 R001/R002v/R003b/R003c的positive sequences及其70个same-class negative cases；positive/negative按pair共享cluster，所有sequence与旧E007 overlap=0。若无法获得70对，GATE_STOP并提交新数据方案，不以重复sequence填充。

## 数据规模
140 cases×(baseline+identity+current-A+至多Top3+R180+mismatched+uniform_bbox)=最多9 conditions/1260次独立生成；单模型持久队列，可checkpoint续跑但同case-condition不得重复计数。B=10000 pair/sequence-cluster bootstrap。

## 模型、权重与关键配置
与R-003c一致：Qwen3-VL-8B-Instruct+IPLoc-ID LoRA，bf16 eager，max_side640，22GiB GPU上限+CPU offload，官方原prompt，greedy，max_new_tokens128，seed=20260805。

## 变量、干预与对照
Primary family=至多Top3候选各自vs baseline；confirmatory specificity=候选vs current-A、R180、mismatched、uniform_bbox。identity为工程control。Top3之间只比较预注册公式，不事后混合。

## 指标与计数规则
Primary：Joint F1@IoU=.5的candidate-baseline paired cluster-bootstrap delta；co-primary positive mIoU delta。Secondary：Identification F1、Joint F1@.3/.7、TP/TN/FP/FN、parse、Yes/No、rescue/newly-broken、positive/negative strata。Top3 primary p/CI family用Holm校正；报告所有条件点估计与95% cluster CI，不仅报告最佳者。missing/unparseable bbox按IoU0。

## 完整性门槛 / no-silent-zero
fresh sequence overlap=0；70+70且same-class negative；baseline/identity 140/140 token exact；每case-condition唯一且完整；模型/prompt/preprocess/generation相同；rewrite命中、finite、mass/row-sum<=5e-5；candidate公式hash匹配R-003c冻结文件；失败与restart完整保留；bootstrap按pair/sequence cluster。

## 竞争假设与预期特征
若某候选在fresh数据同时提升mIoU与Joint F1、保持Identification且优于空间/容器controls，才支持有限的query-stage reference spatial routing行为贡献；若仅current/bbox/control同涨则偏向container/OOD；若均null/负则停止该mapping family。

## 验收条件
科学正向要求至少一个预冻结candidate：Holm校正后Joint F1@.5 delta 95% CI>0；positive mIoU delta CI>0；Identification F1下降不超过.02；parse下降<=1%；且candidate相对R180和mismatched的paired median/mean方向为正、相对uniform_bbox至少方向为正。否则记mixed/null，不继续同family事后调参。

## 依赖的 Run / 证据
R-003c完成并在fresh数据加载前写出不可变Top3候选/hash；fresh manifest gate通过；本run单独审核与执行授权。明确替代旧pending R-004，而不是把R-003b失败条件静默改写。

## 观测结果摘要
（待补充）

## 局限与混杂因素
本地非官方LaSOT重建split；mapping由旧n20选择；attention rewrite分布外；即使正向也不能区分视觉内容和显式reference bbox/container routing，uniform_bbox control仅部分约束。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
最多支持某个预冻结Q→R probability mapping在该模型/数据上改善自然Joint F1且具有有限空间特异性；不证明identity-selective semantics、唯一共享电路或训练方法泛化。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
E007-R-003c frozen_top3.json/conditions.json; E003-R-004b joint protocol; E007-R-003b summary; official vlm_build_messages.py

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
20260805

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
- project_dir: /home/featurize/work/mechanism/E-007
- run_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-004b-fresh-top3-mapping-family-joint-f1-n140
- log_file: /home/featurize/work/mechanism/explog/E-007/E007-R-004b-fresh-top3-mapping-family-joint-f1-n140/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-004b-fresh-top3-mapping-family-joint-f1-n140/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-007/E007-R-004b-fresh-top3-mapping-family-joint-f1-n140/metrics.json
- tmux_session: incontext-E-007-E007-R-004b-fresh-top3-mapping-family-joint-f1-n140
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T22:44:35
- updated: 2026-08-04T22:46:10

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
