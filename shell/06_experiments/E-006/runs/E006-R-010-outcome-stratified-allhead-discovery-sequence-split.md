# E006-R-010-outcome-stratified-allhead-discovery-sequence-split · correct-error separate all-head discovery for last-token and bbox rows

- canonical_run_id: `E006-R-010-outcome-stratified-allhead-discovery-sequence-split`
- run_type: discovery
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-03T15:07:34
- approved_at: 2026-08-03T15:07:37
- execution_authorized_at: 2026-08-03T15:08:28
- execution_authorization_consumed_at: 2026-08-03T15:56:18
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
planned

## 本轮目的
检验localization-correct/error是否由不同active/aligned heads表征。

## 必要性 / 证据链位置
R005固定main4可能遗漏error-specific heads。

## 研究依据 / 被审计对象
E003 endpoints；E005 enlarged sequence-aware data；R006 row gate。

## 实现方式（简版）
sequence-disjoint discovery/confirmation；全1152heads；activation budget与GT alignment分开。

## 实现方式（详细版）
last-token和bbox-row独立；每样本topK active预冻结K10；保存全head矩阵。

## 数据身份与构造
positive natural-Yes endpoints；优先R027 unseen70x4，按sequence split/bootstrap。

## 数据规模
按冻结sequence split决定；frames不作独立sequence。

## 模型、权重与关键配置
Qwen3-VL-8B+IPLoc-ID LoRA eager640

## 变量、干预与对照
outcome组、row；head发现仅discovery；不按transform结果重选。

## 指标与计数规则
full-sequence image budget B_h；conditional GT mass；S50 H/M/C/CG/L；ranking Jaccard/Spearman。

## 完整性门槛 / no-silent-zero
sequence overlap0；每组n预审；全1152 finite。

## 竞争假设与预期特征
识别shared-strength、outcome-specific或noise三种情况。

## 验收条件
若组过小扩数据，不改split；不得把GT alignment称activation。

## 依赖的 Run / 证据
R006；现有natural outputs。

## 观测结果摘要
（待补充）

## 局限与混杂因素
observational、correlated frames、attention非因果。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
只产生候选，必须R011 held-out。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-006/followup_validity_and_equivariance_plan.md#r-010

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
记得给出相应的可视化，以及图表来看 correct error correct-error-mix 的三种情况负责 reference/query 的分别 head 有没有变换

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
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-010-outcome-stratified-allhead-discovery-sequence-split
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-010-outcome-stratified-allhead-discovery-sequence-split/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-010-outcome-stratified-allhead-discovery-sequence-split/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-010-outcome-stratified-allhead-discovery-sequence-split/metrics.json
- tmux_session: incontext-E-006-E006-R-010-outcome-stratified-allhead-discovery-sequence-split
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-03T14:54:20
- updated: 2026-08-03T15:56:18

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
