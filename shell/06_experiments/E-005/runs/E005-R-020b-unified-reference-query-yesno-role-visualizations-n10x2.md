# E005-R-020b-unified-reference-query-yesno-role-visualizations-n10x2 · unified three-role visualizations recovery n10x2

- canonical_run_id: `E005-R-020b-unified-reference-query-yesno-role-visualizations-n10x2`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_visualization_only

## 本轮目的
修正R-020 mm控制流并生成20张统一图。

## 必要性 / 证据链位置
R-020 first forward前失败。

## 研究依据 / 被审计对象
仅缩进修复，冻结heads与协议不变。

## 实现方式（简版）
positive/Yes与真实negative/No各10图；reference|query四行。

## 实现方式（详细版）
retrieval、bbox localization、decision p-1双span。

## 数据身份与构造
manifest80:89。

## 数据规模
20 figures。

## 模型、权重与关键配置
Qwen3-VL+LoRA eager bf16 224。

## 变量、干预与对照
同R-020。

## 指标与计数规则
visualization-only。

## 完整性门槛 / no-silent-zero
20 files+manifest+one inference per figure。

## 观测结果摘要
成功生成20张统一三角色图：indices80:89各positive/Yes与真实same-class negative/No；每图来自单次推理。

## 局限与混杂因素
GT/teacher-forced/non-causal/per-panel minmax。

## 可支持的结论
visualization-only；per-panel minmax仅供空间解释；retrieval GT-conditioned、bbox/decision teacher-forced、attention非因果。

## 不支持的结论 / Claim 边界
空间诊断。

## 关键指标
figures=20; one_inference_per_figure=true; runtime=14.84s; manifest完整。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-020b-unified-reference-query-yesno-role-visualizations-n10x2

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r020b_unified_role_viz.py

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-020b-unified-reference-query-yesno-role-visualizations-n10x2/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-020b-unified-reference-query-yesno-role-visualizations-n10x2/visualizations

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-020b-unified-reference-query-yesno-role-visualizations-n10x2

### tmux session
e005_role_viz_b

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-020b-unified-reference-query-yesno-role-visualizations-n10x2
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-020b-unified-reference-query-yesno-role-visualizations-n10x2/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-020b-unified-reference-query-yesno-role-visualizations-n10x2/visualizations
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-020b-unified-reference-query-yesno-role-visualizations-n10x2/metrics.json
- tmux_session: e005_role_viz_b
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T18:48:45
- updated: 2026-07-24T18:56:16

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
