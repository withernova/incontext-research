# E006-R-012-reference-query-transform-geometric-separability-gate · identity HFlip VFlip R180 reference-only query-only both offline geometry

- canonical_run_id: `E006-R-012-reference-query-transform-geometric-separability-gate`
- run_type: data_gate
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-03T16:11:34
- approved_at: 2026-08-03T16:11:41
- execution_authorized_at: 2026-08-03T16:12:19
- execution_authorization_consumed_at: 2026-08-03T16:15:23
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
planned

## 本轮目的
构建可区分reference tracking与query-coordinate copying的变换manifest。

## 必要性 / 证据链位置
原始LaSOT双图位置相关可能伪造QtoR overlap。

## 研究依据 / 被审计对象
E006 QtoR结果与用户提出的坐标照搬混杂。

## 实现方式（简版）
H/V/R180；REF-only/QUERY-only/BOTH；变换bbox并预计算reference与qcopy候选。

## 实现方式（详细版）
90/270暂不纳入primary以避免W/H和grid改变；所有排除原因保存。

## 数据身份与构造
R011 confirmation候选pair或独立fresh sequences。

## 数据规模
由IoU<=.1且centroid>=2 cells gate后的eligible数量决定。

## 模型、权重与关键配置
（待补充）

## 变量、干预与对照
transform与作用图像；identity配对。

## 指标与计数规则
候选IoU、grid centroid distance、fractional token coverage。

## 完整性门槛 / no-silent-zero
Rtarget vs Qcopy IoU<=.1；centroid>=2 cells；坐标/图像尺寸合法。

## 竞争假设与预期特征
得到在几何上真正可证伪的样本。

## 验收条件
不足则扩数据，不放宽阈值。

## 依赖的 Run / 证据
R011 head选择不影响本offline gate。

## 观测结果摘要
（待补充）

## 局限与混杂因素
变换可能OOD；bbox近似。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
无模型结果。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-006/followup_validity_and_equivariance_plan.md#r-012

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
初步尽可能只通过图像变换，防止很复杂的处理。同时尽量优先只对 reference 或者 query 进行控制变量

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
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-012-reference-query-transform-geometric-separability-gate
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-012-reference-query-transform-geometric-separability-gate/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-012-reference-query-transform-geometric-separability-gate/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-012-reference-query-transform-geometric-separability-gate/metrics.json
- tmux_session: incontext-E-006-E006-R-012-reference-query-transform-geometric-separability-gate
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-03T14:54:20
- updated: 2026-08-03T16:15:23

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
