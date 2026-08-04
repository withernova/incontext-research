# E006-R-011-outcome-headsets-fresh-cross-evaluation · 2x2 correct-discovered error-discovered fresh sequence confirmation

- canonical_run_id: `E006-R-011-outcome-headsets-fresh-cross-evaluation`
- run_type: confirmation
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-03T16:11:05
- approved_at: 2026-08-03T16:11:07
- execution_authorized_at: 
- execution_authorization_consumed_at: 
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
planned

## 本轮目的
在fresh sequence confirmation上验证C/E/M-discovered head sets在correct/error两组和各reference/query角色中的稳定性。

## 必要性 / 证据链位置
排除R010组内过拟合和找错head。

## 研究依据 / 被审计对象
R010 frozen head sets。

## 实现方式（简版）
每角色执行3个冻结head sets×2 outcomes矩阵，含historical、random和layer-matched controls。

## 实现方式（详细版）
输出每角色3×2热图、discovery-confirmation rank稳定性、effect forest plot和固定confirmation contact sheets。

## 数据身份与构造
R010预冻结confirmation sequences。

## 数据规模
由R010 split确定。

## 模型、权重与关键配置
同R010。

## 变量、干预与对照
head source C/E/M × outcome C/E × role；不重新发现。

## 指标与计数规则
image budget、GT mass、S50 H/M/L、head-set Jaccard/rank stability、sequence bootstrap B10000。

## 完整性门槛 / no-silent-zero
R010b head sets在看confirmation前冻结；sequence overlap0；controls和图表完整。

## 竞争假设与预期特征
区分outcome-specific routing、shared-head strength-change和discovery noise。

## 验收条件
只有held-out复现head sets进入R014 primary。

## 依赖的 Run / 证据
E006-R-010b-outcome-stratified-reference-query-allhead-discovery-viz。

## 观测结果摘要
（待补充）

## 局限与混杂因素
仍非因果。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
attention-derived、非因果。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-006/followup_validity_and_equivariance_plan.md#r-011

## 过程记录与补充细节
（待补充）

## Run 审核
### 用户补充要求
（待补充）
### 用户疑问
（待补充）
### Agent 完善说明
已同步R010b的C/E/M与多角色设计，confirmation由旧2×2扩为每角色3×2并增加可视化。
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
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-011-outcome-headsets-fresh-cross-evaluation
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-011-outcome-headsets-fresh-cross-evaluation/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-011-outcome-headsets-fresh-cross-evaluation/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-011-outcome-headsets-fresh-cross-evaluation/metrics.json
- tmux_session: incontext-E-006-E006-R-011-outcome-headsets-fresh-cross-evaluation
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-03T14:54:20
- updated: 2026-08-03T16:11:07

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
