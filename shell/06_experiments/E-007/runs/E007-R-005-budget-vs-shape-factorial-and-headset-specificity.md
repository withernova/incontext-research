# E007-R-005-budget-vs-shape-factorial-and-headset-specificity · budget-vs-shape-factorial-and-headset-specificity

- canonical_run_id: `E007-R-005-budget-vs-shape-factorial-and-headset-specificity`
- run_type: mechanism_ablation
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
在R004成功或出现mixed rescue时，将Q→R总预算与reference内部shape正交分解，并比较historical main4与fresh B→Q headset，避免把更多reference attention误解为更好空间理解。

## 必要性 / 证据链位置
shape-only保持alpha但实际行为可能受alpha过小限制；full transplant同时改mass与shape解释不清。需要2×2 factorial和headset specificity。

## 研究依据 / 被审计对象
E005区分full-sequence target budget与target-conditional spatial alignment；Q→R enrichment不稳定，absolute target mass更稳但有混杂。

## 实现方式（简版）
在冻结fresh subset上做2×2：original/frozen-discovery target mass × original/matched source shape；另加入wrong shape。分别对historical main4和R010 B→Q fresh Top5执行，不从本run重选。

## 实现方式（详细版）
target mass值由独立discovery正确cases按layer/head/row-stage冻结为分位数或median；不得使用当前sample outcome/GT。改变mass时从non-reference keys按原相对分布抽取/返还，保持row sum。shape与mass完全正交。

## 数据身份与构造
R004 fresh数据的预冻结分析子集或额外fresh sequences；按sequence聚类。

## 数据规模
由R004效应量预注册功效后确定，最低40 sequence pairs；不得事后缩放后声称确认。

## 模型、权重与关键配置
同R004。

## 变量、干预与对照
mass original/frozen × shape original/matched；wrong-shape；两套target heads；identity。

## 指标与计数规则
natural mIoU、Joint F1@.5、mass主效应、shape主效应、interaction；headset×condition interaction；cluster bootstrap。

## 完整性门槛 / no-silent-zero
mass/shape数值独立验证；target mass仅discovery冻结；两headsets同conditions；无当前outcome leakage；identity exact。

## 竞争假设与预期特征
shape主效应支持reference内部空间路由；mass主效应支持activation budget；interaction说明二者共同限制；仅某headset有效提示target-subspace compatibility。

## 验收条件
报告完整factorial，不只选最好cell；效应CI与行为稳定性。

## 依赖的 Run / 证据
R004完成且结果支持继续；需新审核授权。

## 观测结果摘要
（待补充）

## 局限与混杂因素
多条件算力大；冻结mass可能仍是task-distribution prior；headset差异非身份专属性。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
区分预算和shape的行为作用，不证明semantic identity。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-005/qr_continuous_curve_analysis_R034d.md; E007-R-004 artifacts

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
- run_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-005-budget-vs-shape-factorial-and-headset-specificity
- log_file: /home/featurize/work/mechanism/explog/E-007/E007-R-005-budget-vs-shape-factorial-and-headset-specificity/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-005-budget-vs-shape-factorial-and-headset-specificity/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-007/E007-R-005-budget-vs-shape-factorial-and-headset-specificity/metrics.json
- tmux_session: incontext-E-007-E007-R-005-budget-vs-shape-factorial-and-headset-specificity
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T20:44:44
- updated: 2026-08-04T20:44:51

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
