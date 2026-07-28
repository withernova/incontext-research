# E005-R-022b-correct-vs-error-natural-query-attention-matched35x2 · correct vs error query attention recovery matched35x2

- canonical_run_id: `E005-R-022b-correct-vs-error-natural-query-attention-matched35x2`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
failed_missing_model_before_first_forward

## 本轮目的
恢复R-022并比较正确/错误自然bbox query attention精准度及可视化。

## 必要性 / 证据链位置
R-022在首forward前因易失manifest路径失败。

## 研究依据 / 被审计对象
改用R-004b run归档manifest；代码/匹配/heads/指标不变。

## 实现方式（简版）
35 error vs 35 geometry-matched correct；70 figures；attention前冻结pairs。

## 实现方式（详细版）
Hungarian geometry matching；natural bbox p-1；raw metrics。

## 数据身份与构造
R-004b归档本地LaSOT manifest和自然outputs。

## 数据规模
35 pairs/70 prompts。

## 模型、权重与关键配置
Qwen3-VL+IPLoc-ID LoRA eager bf16 224。

## 变量、干预与对照
L18H15,L19H03,L22H00,L20H08；seed20260724。

## 指标与计数规则
GT/pred enrichment,mass,pointing,peak distance,candidate-lock,bootstrap。

## 完整性门槛 / no-silent-zero
70 records/figures；exact token match；p-1；finite；replay记录。

## 观测结果摘要
归档manifest恢复成功，但服务器重启后固定Qwen snapshot目录不存在；AutoProcessor在首forward前失败。

## 局限与混杂因素
224 vs 640；cross-class matching；attention非因果。

## 可支持的结论
无科学结论；需恢复约16GB Qwen3-VL snapshot后新run重启。

## 不支持的结论 / Claim 边界
只支持定位成功与attention precision的相关signature。

## 关键指标
forwards=0; figures=0; exit=1

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-022b-correct-vs-error-natural-query-attention-matched35x2

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r022_correct_vs_error_query_attention.py archived manifest

### 配置/超参数
（待补充）

### Seed
20260724

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-022b-correct-vs-error-natural-query-attention-matched35x2/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-022b-correct-vs-error-natural-query-attention-matched35x2/visualizations

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-022b-correct-vs-error-natural-query-attention-matched35x2

### tmux session
e005_query_compare_b

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-022b-correct-vs-error-natural-query-attention-matched35x2
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-022b-correct-vs-error-natural-query-attention-matched35x2/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-022b-correct-vs-error-natural-query-attention-matched35x2/visualizations
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-022b-correct-vs-error-natural-query-attention-matched35x2/metrics.json
- tmux_session: e005_query_compare_b
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-28T10:14:20
- updated: 2026-07-28T10:16:46

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
