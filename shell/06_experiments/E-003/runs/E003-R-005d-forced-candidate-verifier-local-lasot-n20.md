# E003-R-005d-forced-candidate-verifier-local-lasot-n20 · E003-R-005d-forced-candidate-verifier-local-lasot-n20

- canonical_run_id: `E003-R-005d-forced-candidate-verifier-local-lasot-n20`
- legacy_registry_ids: R-021

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
aborted

## 本轮目的
验证assistant autoregressive candidate prefix与自由文本Yes/No continuation。

## 必要性 / 证据链位置
将candidate放入assistant history后验证自由文本decision稳定性。

## 研究依据 / 被审计对象
正确prefix位置仍需无歧义readout才能计算candidate sensitivity。

## 实现方式（简版）
aborted text-generation/parser audit。

## 实现方式（详细版）
candidate+question直接追加为assistant prefix；出现Yes/No但也出现“1. Yes. 2. No.”和纯数字等歧义文本。

## 数据身份与构造
n20 pilot；满足assistant prefix但提前中止。

## 数据规模
pilot audit；预注册unparsed=0 gate未通过。

## 模型、权重与关键配置
同主模型；candidate+question直接追加assistant prefix。

## 变量、干预与对照
六candidate modes；自由生成最多decision continuation。

## 指标与计数规则
只接受唯一显式Yes或No。

## 完整性门槛 / no-silent-zero
预注册unparsed=0；出现1.Yes.2.No.和纯数字，gate失败。

## 观测结果摘要
assistant prefix位置可行，但自由文本decision不稳定，提前中止。

## 局限与混杂因素
自由文本generation不稳定。

## 可支持的结论
无有效科学指标；后继必须使用constrained next-token logits。

## 不支持的结论 / Claim 边界
无科学Yes rate；只支持改用constrained logits的工程决策。

## 关键指标
{"scientific_outputs": 0, "assistant_prefix": true, "unparsed_zero_gate_passed": false}

## 审核入口
config/run.md；logs/run.log。

## 过程记录与补充细节
canonical_run_id=E003-R-005d-forced-candidate-verifier-local-lasot-n20；registry自动ID仅为工具映射。

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
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-005d-forced-candidate-verifier-local-lasot-n20/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-005d-forced-candidate-verifier-local-lasot-n20

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-005d-forced-candidate-verifier-local-lasot-n20

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
- run_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-005d-forced-candidate-verifier-local-lasot-n20
- log_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-005d-forced-candidate-verifier-local-lasot-n20/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-005d-forced-candidate-verifier-local-lasot-n20
- metrics_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-005d-forced-candidate-verifier-local-lasot-n20/metrics.json
- tmux_session: incontext-E-003-E003-R-005d-forced-candidate-verifier-local-lasot-n20
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-20T17:17:12+08:00
- updated: 2026-07-20T17:46:51

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
