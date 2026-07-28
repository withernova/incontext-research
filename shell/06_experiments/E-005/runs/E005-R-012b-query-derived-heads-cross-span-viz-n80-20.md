# E005-R-012b-query-derived-heads-cross-span-viz-n80-20 · 冻结query-derived heads的reference/query双侧可视化

- canonical_run_id: `E005-R-012b-query-derived-heads-cross-span-viz-n80-20`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed_quality_gate

## 本轮目的
人工审核R-011c query-derived五头是否在同一coordinate-query下同时关注reference GT与query GT。

## 必要性 / 证据链位置
R-012频率交集shared set门禁失败，但query-derived整组在双span均通过聚合质量门禁；需画正确组合。

## 研究依据 / 被审计对象
query-derived=L18H15,L19H03,L24H27,L22H00,L20H08；reference median enrichment1.760，query7.965。

## 实现方式（简版）
复现0:79冻结query-derived top5，在80:99分别对reference/query输出turbo heatmaps和双侧指标。

## 实现方式（详细版）
不删除表现差的L24H27，避免按validation结果post-hoc筛头；每个样本输出reference/query两图。

## 数据身份与构造
0:79 discovery/80:99 internal validation positive。

## 数据规模
20 validation双span；前10固定样本共20组六panel图。

## 模型、权重与关键配置
Qwen3-VL+LoRA eager bf16 224 coordinate p-1 query rows。

## 变量、干预与对照
同一heads、同一forward、各自GT；all-head controls。

## 指标与计数规则
双侧每head enrichment/pointing/percentile及组合指标。

## 完整性门槛 / no-silent-zero
双span exact；finite；双侧聚合三项quality。

## 观测结果摘要
冻结query-derived五头的双span审核完成；reference/query各自3/3聚合quality gates通过，20组双角色turbo图已生成。

## 局限与混杂因素
post-hoc、teacher-forced、非因果；L24H27保留。

## 可支持的结论
同一query-derived head set在coordinate prediction阶段同时对reference/query GT呈空间选择性，支持部分共通定位signature；reference明显弱于query，且L24H27不具GT选择性。post-hoc/teacher-forced/non-causal。

## 不支持的结论 / Claim 边界
共同仅表示同一组heads在双span呈空间选择性，不代表对称或因果identity matching。

## 关键指标
reference median enrichment=1.760, percentile=.907, pointing=.11 vs .024；query median=7.965, percentile=.973, pointing=.27 vs .070；reference combined enrichment=1.094 pointing0；query combined=4.136 pointing=.35。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-012b-query-derived-heads-cross-span-viz-n80-20

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r012b_cross_span_viz.py

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-012b-query-derived-heads-cross-span-viz-n80-20/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-012b-query-derived-heads-cross-span-viz-n80-20/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-012b-query-derived-heads-cross-span-viz-n80-20

### tmux session
e005_cross_span_viz

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-012b-query-derived-heads-cross-span-viz-n80-20
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-012b-query-derived-heads-cross-span-viz-n80-20/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-012b-query-derived-heads-cross-span-viz-n80-20/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-012b-query-derived-heads-cross-span-viz-n80-20/metrics.json
- tmux_session: e005_cross_span_viz
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T16:36:16
- updated: 2026-07-24T16:38:23

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
