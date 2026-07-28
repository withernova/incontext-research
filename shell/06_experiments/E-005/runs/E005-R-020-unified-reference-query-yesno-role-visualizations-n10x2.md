# E005-R-020-unified-reference-query-yesno-role-visualizations-n10x2 · unified reference retrieval query localization YesNo visualization n10x2

- canonical_run_id: `E005-R-020-unified-reference-query-yesno-role-visualizations-n10x2`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
failed_control_flow_before_first_forward

## 本轮目的
同一次推理中并列显示reference retrieval、query localization、Yes/No decision双图attention。

## 必要性 / 证据链位置
已有指标但缺统一视觉对照。

## 研究依据 / 被审计对象
冻结R-018 retrieval有效4头、R-014 localization main4、R-019b双侧shared decision4头。

## 实现方式（简版）
indices80:89各画positive/Yes和真实same-class negative/No；每图reference|query、4行。

## 实现方式（详细版）
retrieval=query-object visual rows→ref；localization=bbox p-1→双span；decision=Yes/No p-1→双span。

## 数据身份与构造
旧manifest80:89；每condition独立真实两图forward。

## 数据规模
20 figures/20 inferences。

## 模型、权重与关键配置
Qwen3-VL+LoRA eager bf16 224。

## 变量、干预与对照
clean+GT、retrieval row mask、localization ref control、decision双span。

## 指标与计数规则
visualization-only；turbo、green GT、per-panel minmax。

## 完整性门槛 / no-silent-zero
one inference per figure；exact bbox/decision matching；p-1；span/grid。

## 观测结果摘要
首样本forward前mm赋值误落入单行if suite，UnboundLocalError；0 figures，无科学输出。

## 局限与混杂因素
GT-conditioned retrieval rows；teacher-forced bbox/decision；decision heads failed spatial gate；non-causal。

## 可支持的结论
无科学结论；R-020b仅修正控制流后重跑。

## 不支持的结论 / Claim 边界
空间诊断图，不支持绝对强度比较或因果角色。

## 关键指标
figures=0; exit=1

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-020-unified-reference-query-yesno-role-visualizations-n10x2

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r020_unified_role_viz.py

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-020-unified-reference-query-yesno-role-visualizations-n10x2/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-020-unified-reference-query-yesno-role-visualizations-n10x2/visualizations

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-020-unified-reference-query-yesno-role-visualizations-n10x2

### tmux session
e005_role_viz

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-020-unified-reference-query-yesno-role-visualizations-n10x2
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-020-unified-reference-query-yesno-role-visualizations-n10x2/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-020-unified-reference-query-yesno-role-visualizations-n10x2/visualizations
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-020-unified-reference-query-yesno-role-visualizations-n10x2/metrics.json
- tmux_session: e005_role_viz
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T18:46:58
- updated: 2026-07-24T18:48:18

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
