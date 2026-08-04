# E006-R-015-reference-image-vs-prompt-bbox-mismatch-diagnostic · reference visual transform versus explicit bbox-coordinate mismatch

- canonical_run_id: `E006-R-015-reference-image-vs-prompt-bbox-mismatch-diagnostic`
- run_type: conditional_diagnostic
- review_status: draft
- review_round: 0
- submitted_for_review_at: 
- approved_at: 
- execution_authorized_at: 
- execution_authorization_consumed_at: 
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
planned

## 本轮目的
若R014歧义，区分QtoR跟随reference视觉内容还是prompt bbox坐标。

## 必要性 / 证据链位置
consistent transform同时改变visual object与显式reference bbox cue。

## 研究依据 / 被审计对象
仅在R014混合/歧义结果后触发。

## 实现方式（简版）
consistent、image-only transform、bbox-only transform三条件。

## 实现方式（详细版）
后两者是OOD mismatch，独立标记。

## 数据身份与构造
R014 eligible behavior-audited subset。

## 数据规模
条件触发后冻结。

## 模型、权重与关键配置
同R014。

## 变量、干预与对照
visual content位置与prompt bbox坐标正交操纵。

## 指标与计数规则
QtoR对visual GT与prompt-coordinate target的mass/H/L及位移。

## 完整性门槛 / no-silent-zero
不一致条件明确标记；不混入自然性能。

## 竞争假设与预期特征
诊断visual cue、coordinate cue或mixed routing。

## 验收条件
仅作diagnostic，不升级自然机制。

## 依赖的 Run / 证据
R014仍歧义时触发。

## 观测结果摘要
（待补充）

## 局限与混杂因素
有意OOD prompt-image冲突。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
不能代表正常任务行为。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-006/followup_validity_and_equivariance_plan.md#r-015

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
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-015-reference-image-vs-prompt-bbox-mismatch-diagnostic
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-015-reference-image-vs-prompt-bbox-mismatch-diagnostic/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-015-reference-image-vs-prompt-bbox-mismatch-diagnostic/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-015-reference-image-vs-prompt-bbox-mismatch-diagnostic/metrics.json
- tmux_session: incontext-E-006-E006-R-015-reference-image-vs-prompt-bbox-mismatch-diagnostic
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-03T14:54:20
- updated: 2026-08-03T14:54:20

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
