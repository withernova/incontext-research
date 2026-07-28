# E005-R-019b-yes-no-decision-token-reference-query-heads-n80-20 · Yes/No decision-token reference/query heads recovery n80+20

- canonical_run_id: `E005-R-019b-yes-no-decision-token-reference-query-heads-n80-20`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_failed_spatial_quality_gate

## 本轮目的
修正R-019控制流后完成decision p-1 row双span独立head发现。

## 必要性 / 证据链位置
R-019在first forward前失败且无科学输出。

## 研究依据 / 被审计对象
仅修正dids赋值缩进；协议不变。

## 实现方式（简版）
gold Yes/No decision p-1→reference/query spans，pooled discovery，condition-separated validation。

## 实现方式（详细版）
regional exact token match；raw ref/query/other budget；role overlap。

## 数据身份与构造
0:79 discovery positive+negative；80:99 validation。

## 数据规模
160+40 prompts。

## 模型、权重与关键配置
Qwen3-VL+LoRA eager bf16 224。

## 变量、干预与对照
同R-019。

## 指标与计数规则
GT concentration、budget、overlap。

## 完整性门槛 / no-silent-zero
exact decision alignment、p-1、finite。

## 观测结果摘要
gold Yes/No decision p-1 row双span重选完成：reference/query Top5高度重合但两侧object GT质量全部失败；attention约80%流向other history，reference/query各约9–10%；Yes/No频率近似。

## 局限与混杂因素
teacher-forced bbox/decision、post-hoc、non-causal。

## 可支持的结论
repo frequency在decision row恢复稳定但非object-localizing的浅中层attention signature；decision主要分配给非图像历史，双图预算近似，不能据此判断视觉identity依赖或因果判别heads。

## 不支持的结论 / Claim 边界
decision attention signature only。

## 关键指标
ref heads=L10H29,L12H21,L10H09,L03H20,L04H29；query heads=L12H21,L03H20,L10H29,L02H11,L04H29；intersection4,J=.667。positive ref/query own enrichment=.110/.128,pointing0/0；negative=.102/.118,pointing0/0；selected-head median budgets ref≈.085-.107,query≈.096-.101,other≈.803-.811；与grounding/retrieval/localization有效候选Top5 overlap均0。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-019b-yes-no-decision-token-reference-query-heads-n80-20

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r019b_decision_token_heads.py

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-019b-yes-no-decision-token-reference-query-heads-n80-20/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-019b-yes-no-decision-token-reference-query-heads-n80-20/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-019b-yes-no-decision-token-reference-query-heads-n80-20

### tmux session
e005_decision_b

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-019b-yes-no-decision-token-reference-query-heads-n80-20
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-019b-yes-no-decision-token-reference-query-heads-n80-20/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-019b-yes-no-decision-token-reference-query-heads-n80-20/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-019b-yes-no-decision-token-reference-query-heads-n80-20/metrics.json
- tmux_session: e005_decision_b
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T18:15:39
- updated: 2026-07-24T18:18:25

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
