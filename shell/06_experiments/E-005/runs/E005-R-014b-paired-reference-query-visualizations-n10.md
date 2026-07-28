# E005-R-014b-paired-reference-query-visualizations-n10 · R-014同次推理reference-query配对可视化n10

- canonical_run_id: `E005-R-014b-paired-reference-query-visualizations-n10`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_visualization_only

## 本轮目的
把同一推理中的reference和query放在同一张图中，便于逐head双侧比较。

## 必要性 / 证据链位置
分开的单角色图不利于审阅跨span共同空间选择性。

## 研究依据 / 被审计对象
复用R-014前10个固定样本及原attention maps，不重新推理、不改变指标。

## 实现方式（简版）
两列布局：reference左/query右；顶部原图+GT，随后相同head对应行及combined。

## 实现方式（详细版）
每个样本一图；保留turbo和绿色GT；R-014无negative，明确标记negative_present=false。

## 数据身份与构造
R-014固定indices0:9，同一unseen sequence first/last frames。

## 数据规模
10 paired figures。

## 模型、权重与关键配置
无新forward；复用R-014。

## 变量、干预与对照
同样本、同heads、同query rows左右对齐。

## 指标与计数规则
仅展示；科学指标继承R-014且不重算。

## 完整性门槛 / no-silent-zero
每图reference/query同sequence；10/10输出；不得混入negative。

## 观测结果摘要
生成10张同次推理配对图：reference左、query右，clean GT与相同heads逐行对齐；无negative。

## 局限与混杂因素
positive-only；无negative列；panel各自归一化不能作绝对强度比较。

## 可支持的结论
visualization-only，不新增或改变R-014结论。

## 不支持的结论 / Claim 边界
只改善展示，不新增科学结论。

## 关键指标
paired figures=10；scientific metrics unchanged from R-014。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-014b-paired-reference-query-visualizations-n10

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r014b_pair_layout.py

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-014b-paired-reference-query-visualizations-n10/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-014b-paired-reference-query-visualizations-n10/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-014b-paired-reference-query-visualizations-n10

### tmux session
（待补充）

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-014b-paired-reference-query-visualizations-n10
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-014b-paired-reference-query-visualizations-n10/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-014b-paired-reference-query-visualizations-n10/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-014b-paired-reference-query-visualizations-n10/metrics.json
- tmux_session: incontext-E-005-E005-R-014b-paired-reference-query-visualizations-n10
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T16:55:34
- updated: 2026-07-24T16:55:34

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
