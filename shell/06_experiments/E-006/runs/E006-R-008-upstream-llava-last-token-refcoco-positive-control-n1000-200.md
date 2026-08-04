# E006-R-008-upstream-llava-last-token-refcoco-positive-control-n1000-200 · immutable upstream LocalizationHeads LLaVA exact last-token positive control

- canonical_run_id: `E006-R-008-upstream-llava-last-token-refcoco-positive-control-n1000-200`
- run_type: method_validation
- review_status: changes_requested
- review_round: 1
- submitted_for_review_at: 2026-08-03T15:04:59
- approved_at: 
- execution_authorized_at: 
- execution_authorization_consumed_at: 
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
cancelled

## 本轮目的
在公开仓库声明的数据/模型范式上验证last-token localization-head方法。

## 必要性 / 证据链位置
先建立upstream正对照，避免只在IPLoc-ID自定义任务内自证。

## 研究依据 / 被审计对象
LocalizationHeads public repo README/code pinned commit9ffe219。

## 实现方式（简版）
LLaVA-1.5-7B；RefCOCO discovery1000选head，confirmation200冻结评估。

## 实现方式（详细版）
保持repo top_k5、ReLU(S-2mean)、attention-mass entropy/current bbox；外加GT IoU和matched controls。

## 数据身份与构造
R007 RefCOCO unique-image split。

## 数据规模
pilot20/discovery1000/confirmation200

## 模型、权重与关键配置
upstream LLaVA-1.5-7B eager attention exact forward last-token

## 变量、干预与对照
confirmation不重选；random/layer-matched/center/area controls。

## 指标与计数规则
repo bbox；IoU success@.3/.5/.7；S50 H/M/C/CG/L。

## 完整性门槛 / no-silent-zero
confirmation200/200；解析无silent zero；冻结head。

## 竞争假设与预期特征
公开方法应在confirmation优于matched controls。

## 验收条件
若正对照失败，停止升级Qwen方法有效性结论。

## 依赖的 Run / 证据
R007；LLaVA权重可用。

## 观测结果摘要
用户审核后取消：后续研究限定Qwen，不运行LLaVA、不下载权重、无科学输出。

## 局限与混杂因素
public reconstruction非作者未公开精确1000 subset。

## 可支持的结论
仅记录scope decision。

## 不支持的结论 / Claim 边界
不得声称复现LocalizationHeads原LLaVA结果；后续只能称在Qwen上测试其公开思路。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-006/followup_validity_and_equivariance_plan.md#r-008

## 过程记录与补充细节
（待补充）

## Run 审核
### 用户补充要求
这个还是不做了，因为我们后续的研究也只是 qwen 上的
### 用户疑问
（待补充）
### Agent 完善说明
已采纳用户意见，R-008取消且从后续依赖链移除。
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
20260724

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
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-008-upstream-llava-last-token-refcoco-positive-control-n1000-200
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-008-upstream-llava-last-token-refcoco-positive-control-n1000-200/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-008-upstream-llava-last-token-refcoco-positive-control-n1000-200/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-008-upstream-llava-last-token-refcoco-positive-control-n1000-200/metrics.json
- tmux_session: incontext-E-006-E006-R-008-upstream-llava-last-token-refcoco-positive-control-n1000-200
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-03T14:54:20
- updated: 2026-08-03T15:16:11

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
