# E006-R-013-natural-behavior-transform-gate · natural Yes bbox under REF-only QUERY-only BOTH H V R180

- canonical_run_id: `E006-R-013-natural-behavior-transform-gate`
- run_type: behavioral_gate
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-03T18:02:02
- approved_at: 2026-08-03T18:02:05
- execution_authorized_at: 2026-08-03T19:02:26
- execution_authorization_consumed_at: 2026-08-03T19:02:26
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
planned

## 本轮目的
确认变换后模型行为仍可解释，再分析attention。

## 必要性 / 证据链位置
若变换导致任务失败，attention位移不能解释正常reference use。

## 研究依据 / 被审计对象
R012 eligible manifest。

## 实现方式（简版）
identity及9个变换条件自然生成；reference变换时同步prompt bbox。

## 实现方式（详细版）
行为稳定与行为改变样本分层，不删除失败。

## 数据身份与构造
R012 eligible pairs。

## 数据规模
eligible pairs×10 conditions。

## 模型、权重与关键配置
Qwen3-VL-8B+IPLoc-ID LoRA natural generation max_side640

## 变量、干预与对照
REF-only/QUERY-only/BOTH×H/V/R180；identity paired。

## 指标与计数规则
Yes保持、parse、natural IoU、Joint F1、bbox equivariance。

## 完整性门槛 / no-silent-zero
所有conditions完整；变换bbox审计；不复用identity archived bbox冒充natural。

## 竞争假设与预期特征
界定可用于R014正常机制分析的behavior-stable subset。

## 验收条件
大规模失败则R014降级为OOD diagnostic。

## 依赖的 Run / 证据
R012。

## 观测结果摘要
（待补充）

## 局限与混杂因素
图像变换可能改变模型置信度/行为。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
行为gate不证明attention机制。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-006/followup_validity_and_equivariance_plan.md#r-013

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
Retry under current explicit user request to complete R-013/R-014 after attempt-001 failed before model load/scientific records due implementation assertion selecting repeated sequence rows; attempt-001 preserved, scope unchanged, selection corrected to unique sequences.

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
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-013-natural-behavior-transform-gate
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-013-natural-behavior-transform-gate/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-013-natural-behavior-transform-gate/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-013-natural-behavior-transform-gate/metrics.json
- tmux_session: incontext-E-006-E006-R-013-natural-behavior-transform-gate
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-03T14:54:20
- updated: 2026-08-03T19:02:26

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
