# E003-R-005b-forced-candidate-verifier-local-lasot-n20 · E003-R-005b-forced-candidate-verifier-local-lasot-n20

- canonical_run_id: `E003-R-005b-forced-candidate-verifier-local-lasot-n20`
- legacy_registry_ids: R-019

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
aborted

## 本轮目的
修复PYTHONPATH后审计forced-candidate decision parser。

## 必要性 / 证据链位置
修复import后验证decision parser不会伪造candidate response。

## 研究依据 / 被审计对象
forced candidate必须基于显式decision而非任意bbox fallback。

## 实现方式（简版）
aborted parser audit。

## 实现方式（详细版）
发现repository PN_interpreter在没有显式Yes/No时会将任意非零bbox fallback标为positive。

## 数据身份与构造
n20 pilot；中止于parser audit。

## 数据规模
pilot audit；无有效科学结果。

## 模型、权重与关键配置
同主模型；显式PYTHONPATH/offline snapshot。

## 变量、干预与对照
candidate modes已构造，但decision使用repository PN_interpreter。

## 指标与计数规则
原计划Yes rate；因parser无效不计算。

## 完整性门槛 / no-silent-zero
要求decision语义来自显式Yes/No；bbox fallback违反gate。

## 观测结果摘要
parser会伪造positive decision，run中止。

## 局限与混杂因素
PN_interpreter把任意非零bbox标positive。

## 可支持的结论
不得引用中止前Yes rate；PN_interpreter不适用于forced candidate scoring。

## 不支持的结论 / Claim 边界
无科学Yes rate；只支持parser不适用。

## 关键指标
{"scientific_outputs": 0, "parser_fallback_invalid": true}

## 审核入口
config/run.md；logs/run.log。

## 过程记录与补充细节
canonical_run_id=E003-R-005b-forced-candidate-verifier-local-lasot-n20；registry自动ID仅为工具映射。

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
see config/run.md

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-005b-forced-candidate-verifier-local-lasot-n20/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-005b-forced-candidate-verifier-local-lasot-n20

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-005b-forced-candidate-verifier-local-lasot-n20

### tmux session
（待补充）

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-003
- run_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-005b-forced-candidate-verifier-local-lasot-n20
- log_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-005b-forced-candidate-verifier-local-lasot-n20/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-005b-forced-candidate-verifier-local-lasot-n20
- metrics_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-005b-forced-candidate-verifier-local-lasot-n20/metrics.json
- tmux_session: incontext-E-003-E003-R-005b-forced-candidate-verifier-local-lasot-n20
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-20T17:17:12+08:00
- updated: 2026-07-20T17:46:51

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
