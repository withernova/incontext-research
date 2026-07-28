# E005-R-022c-correct-vs-error-natural-query-attention-matched35x2 · correct vs error query attention persistent-model recovery matched35x2

- canonical_run_id: `E005-R-022c-correct-vs-error-natural-query-attention-matched35x2`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
failed_summary_variable_shadow_after_all_forwards

## 本轮目的
比较自然定位正确与accepted-low-IoU错误样本中冻结query-localization heads对query GT的精准度，并生成matched可视化。

## 必要性 / 证据链位置
这是Q-004一致性idea成立前的关键判别实验；R-022/R-022b均为首forward前基础设施失败。

## 研究依据 / 被审计对象
E003-R-004b归档自然输出；R-014冻结query-localization heads；persistent Qwen 10/10 repacked shards已逐文件SHA-256通过。

## 实现方式（简版）
35 error Yes IoU<.1 vs 35 correct Yes IoU>=.7；attention前Hungarian几何匹配；70 prompts/70 figures。

## 实现方式（详细版）
匹配=标准化reference/query log-area与log-aspect L1，same-class固定偏好；natural bbox p-1；raw unsmoothed统计，Gaussian仅可视化。

## 数据身份与构造
R-004b归档本地确定性LaSOT reconstruction，非官方split；error不自动等于wrong-instance。

## 数据规模
35 matched pairs, 70 prompts, 70 one-inference figures。

## 模型、权重与关键配置
persistent /home/featurize/work/mechanism/models/Qwen3-VL-8B-Instruct + IPLoc-ID LoRA；eager bf16 max_side224；原自然生成640。

## 变量、干预与对照
heads=L18H15,L19H03,L22H00,L20H08；pair manifest在forward前冻结；seed=20260724。

## 指标与计数规则
GT enrichment/mass/pointing/peak distance；pred enrichment；candidate-lock log ratio；10000 bootstrap CI；IoU-enrichment rank corr。

## 完整性门槛 / no-silent-zero
persistent 10/10 shards；processor/base/LoRA实际加载；exact bbox/Yes regional token match；p-1；70 records/figures；finite；replay逐样本记录。

## 观测结果摘要
70/70 forwards、70 figures、70/70 replay均完成；最终metrics汇总因局部list变量a遮蔽argparse a，访问a.seed触发AttributeError，summary/record manifest未写出。

## 局限与混杂因素
224 replay vs 640 generation；部分cross-class matching；attention非因果；correct pred与GT重叠。

## 可支持的结论
可视化产物保留，但无完整raw-record summary，不能据此报告组间统计；R-022d固定seed常量后原协议重跑。

## 不支持的结论 / Claim 边界
仅检验query attention precision与自然定位正确性的关联，不确认wrong-instance、identity binding或因果性能提升。

## 关键指标
forwards=70; figures=70; replay=70/70; summary=missing; exit=1

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-022c-correct-vs-error-natural-query-attention-matched35x2

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r022_correct_vs_error_query_attention.py persistent model

### 配置/超参数
（待补充）

### Seed
20260724

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-022c-correct-vs-error-natural-query-attention-matched35x2/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-022c-correct-vs-error-natural-query-attention-matched35x2/visualizations

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-022c-correct-vs-error-natural-query-attention-matched35x2

### tmux session
e005_query_compare_c

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-022c-correct-vs-error-natural-query-attention-matched35x2
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-022c-correct-vs-error-natural-query-attention-matched35x2/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-022c-correct-vs-error-natural-query-attention-matched35x2/visualizations
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-022c-correct-vs-error-natural-query-attention-matched35x2/metrics.json
- tmux_session: e005_query_compare_c
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-28T12:11:24
- updated: 2026-07-28T12:22:10

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
