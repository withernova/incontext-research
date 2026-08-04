# E007-R-004-fresh-sequence-qtor-transplant-joint-f1-n140 · fresh-sequence-qtor-transplant-joint-f1-n140

- canonical_run_id: `E007-R-004-fresh-sequence-qtor-transplant-joint-f1-n140`
- run_type: causal_behavior_confirmation
- review_status: pending_review
- review_round: 1
- submitted_for_review_at: 2026-08-04T20:44:51
- approved_at: 
- execution_authorized_at: 
- execution_authorization_consumed_at: 
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
planned

## 本轮目的
在fresh sequence-disjoint positive/negative POIL数据上确认matched Q→R shape transplant对自然localization与Joint F1的影响，并与空间破坏、mismatch、uniform-container和knockout对照。

## 必要性 / 证据链位置
只有fresh自然行为和Joint F1才能支持输出阶段reference-target routing的有限因果重要性，并排除只改善旧positive bbox或牺牲negative rejection。

## 研究依据 / 被审计对象
E003显示Identification F1高但Joint F1随IoU阈值下降；未来改进必须提升natural bbox IoU与Joint F1。R003仅pilot，不能确认。

## 实现方式（简版）
从未用于R001-R003选择/调参的新LaSOT sequences构造70 positive+70 same-class negative（或可用fresh manifest的等量冻结集），只运行R003预先胜出的matched condition和预注册controls：baseline/identity、best spatial-destruction control、mismatched、uniform-bbox、knockout。不得根据fresh结果换condition/head。

## 实现方式（详细版）
source/target heads、window、donor规则、resize、mass preservation全部继承冻结。对positive与negative均自然生成；negative source map来自各自reference prompt，mismatch donor保持label/category匹配如可用并预冻结。所有queries按sequence cluster拆分/bootstrap。

## 数据身份与构造
fresh sequence-disjoint manifest，目标70 pairs=140 query cases；不得与R001-R003 sequences重叠。若fresh same-class negative不足，先GATE_STOP而非改为out-class。

## 数据规模
140 cases×至多6 conditions；B=10000 sequence-cluster bootstrap。

## 模型、权重与关键配置
同一IPLoc-ID LoRA、原prompt、max_side640、greedy。

## 变量、干预与对照
baseline/identity；matched shape；R003冻结的spatial destruction；mismatched; uniform bbox；knockout。Primary matched vs baseline；mechanism specificity matched vs each control。

## 指标与计数规则
Identification F1；natural positive bbox mIoU（all positives missing=0）；Joint F1@IoU .3/.5/.7；TP/TN/FP/FN；parse/Yes/No；paired deltas和sequence-bootstrap CI。Holm校正仅用于预注册primary family。

## 完整性门槛 / no-silent-zero
fresh overlap=0；identity exact；all responses preserved；negative无GT target localization混入positive mIoU；run id-condition一一对应；missing bbox=0 IoU；head/window不重选；完整失败表。

## 竞争假设与预期特征
matched提升mIoU与Joint F1且优于controls→支持query-stage reference spatial routing具有行为因果作用；uniform同等→container prior；knockout变差但rescue不升→必要但当前source不充分；null保持有界。

## 验收条件
科学支持要求Joint F1@.5 matched-baseline CI>0，并且mIoU方向一致、Identification F1不下降超过.02、matched优于mismatched/spatial control；否则结论mixed/null。

## 依赖的 Run / 证据
R003升级gate通过；fresh manifest；单独审核授权。

## 观测结果摘要
（待补充）

## 局限与混杂因素
非官方本地LaSOT split；attention intervention分布外；即便成功也不证明identity-selective semantics。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
最多支持冻结query heads在bbox生成窗口内对reference visual values的空间路由对POIL行为有因果贡献；不支持全模型唯一电路或独立理解reference。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-003/result.md; shell/06_experiments/E-005/dual_gpu_640_core_results.md

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
- run_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-004-fresh-sequence-qtor-transplant-joint-f1-n140
- log_file: /home/featurize/work/mechanism/explog/E-007/E007-R-004-fresh-sequence-qtor-transplant-joint-f1-n140/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-004-fresh-sequence-qtor-transplant-joint-f1-n140/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-007/E007-R-004-fresh-sequence-qtor-transplant-joint-f1-n140/metrics.json
- tmux_session: incontext-E-007-E007-R-004-fresh-sequence-qtor-transplant-joint-f1-n140
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T20:44:43
- updated: 2026-08-04T20:44:51

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
