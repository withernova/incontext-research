# E007-R-002-teacher-replayed-qtor-shape-transplant-controls-n20 · teacher-replayed-qtor-shape-transplant-controls-n20

- canonical_run_id: `E007-R-002-teacher-replayed-qtor-shape-transplant-controls-n20`
- run_type: causal_pilot
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-04T20:44:51
- approved_at: 2026-08-04T20:47:11
- execution_authorized_at: 2026-08-04T20:47:14
- execution_authorization_consumed_at: 2026-08-04T20:57:36
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
planned

## 本轮目的
在exact natural bbox p-1 rows上做Q→R shape-only attention transplant，检查matched source map是否相对permuted/mismatched/uniform controls改善GT bbox token likelihood或后续Yes/No margin，并验证干预方向。

## 必要性 / 证据链位置
先在明确row对齐的teacher replay中低成本筛查干预是否可工作；避免直接自然生成时把实现错误当null。

## 研究依据 / 被审计对象
E005/E006观察到correct cases Q→R target mass更高但非因果；R014c显示main4 Q→R响应reference target。Shape-only transplant保持原Q→R total mass，可隔离reference内部空间路由。

## 实现方式（简版）
同n20、target main4、source G→R aggregate。在archived natural bbox exact p-1 rows重写Q→R：matched shape、R180 shape、within-grid fixed permutation、mismatched-sequence shape、uniform reference-bbox、uniform full-reference、Q→R knockout、identity。

## 实现方式（详细版）
每target row/head保留alpha=sum_R A；shape condition A_R=alpha*S；non-R原样。Uniform-bbox由prompt中reference bbox映射到merged-token fractional occupancy后normalize；mismatched按预冻结cyclic sequence donor并对grid做bilinear resize再normalize；permutation seed固定20260804且每grid共享。Knockout将A_R=0并把alpha按原non-R分布比例返还，row sum保持1。

## 数据身份与构造
继承R001冻结20个sequence-unique positives及其baseline natural responses；10 error/10 correct仅分层描述，不据结果换样本。

## 数据规模
20×8 conditions；同一teacher-forward response，每condition完整forward；sequence paired。

## 模型、权重与关键配置
原IPLoc-ID LoRA、原prompt、max_side640、bf16 eager。

## 变量、干预与对照
baseline/no-op/identity；matched；R180；permuted；mismatched；uniform bbox；uniform reference；knockout。source/target均预冻结。

## 指标与计数规则
原natural bbox token mean NLL；GT bbox teacher-forced mean NLL（独立response replay，不混称自然行为）；natural Yes/No next-token margin；KL/logit shifts；干预A@V norm。Primary matched-minus-R180与matched-minus-mismatched的GT-bbox NLL差。

## 完整性门槛 / no-silent-zero
identity reproduce；所有conditions row-sum/mass preservation；mismatched donor sequence不同；GT response只作oracle diagnostic；不得由teacher replay声称IoU提升；finite 20×8。

## 竞争假设与预期特征
matched若优于spatially destroyed/mismatched，支持prompt-stage reference spatial routing可改善正确bbox token compatibility；uniform-bbox同样好则更像container prior。

## 验收条件
directional pilot需matched在至少两项primary control比较上配对方向为正且无parse/logit异常，才建议R003；无论结果均完整归档。

## 依赖的 Run / 证据
R000、R001 GATE_PASS。

## 观测结果摘要
（待补充）

## 局限与混杂因素
teacher forcing、GT NLL oracle、n20；source-target value subspace兼容性不保证。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
最多支持attention-routing transplant改变bbox-token likelihood；不支持自然bbox改善或identity理解。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-005/head_role_registry.md; shell/06_experiments/E-006/result.md

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
20260804

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
- run_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-002-teacher-replayed-qtor-shape-transplant-controls-n20
- log_file: /home/featurize/work/mechanism/explog/E-007/E007-R-002-teacher-replayed-qtor-shape-transplant-controls-n20/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-002-teacher-replayed-qtor-shape-transplant-controls-n20/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-007/E007-R-002-teacher-replayed-qtor-shape-transplant-controls-n20/metrics.json
- tmux_session: incontext-E-007-E007-R-002-teacher-replayed-qtor-shape-transplant-controls-n20
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T20:44:43
- updated: 2026-08-04T20:57:36

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
