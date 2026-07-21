# E003-R-003-torch-compat-smoke-local-lasot-n1 · E003-R-003-torch-compat-smoke-local-lasot-n1

- canonical_run_id: `E003-R-003-torch-compat-smoke-local-lasot-n1`
- legacy_registry_ids: R-016

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed

## 本轮目的
验证Torch兼容shim、offline snapshot、LoRA和完整推理链路。

## 必要性 / 证据链位置
在重启n140前验证processor、GPU、LoRA、generation、Yes/No、bbox与IoU链路恢复。

## 研究依据 / 被审计对象
R-002因环境API缺失零记录。

## 实现方式（简版）
environment compatibility smoke。

## 实现方式（详细版）
缺失时注入torch.compiler.is_compiling=lambda:False；VLM_LOCAL_MODEL_PATH仅覆盖文件加载路径。

## 数据身份与构造
R-001 manifest前1 sample；1 positive+1 same-class negative。

## 数据规模
manifest前1 sample；1 positive+1 same-class negative；2 records。

## 模型、权重与关键配置
Qwen3-VL-8B+1shot LoRA；offline snapshot；is_compiling=lambda:False兼容shim。

## 变量、干预与对照
compatibility fix only；无模型/metric变更。

## 指标与计数规则
仅检查2 records与解析链路；TP/TN仅为smoke输出。

## 完整性门槛 / no-silent-zero
2 records；无processor failure/traceback；bbox/decision可解析。

## 观测结果摘要
TP=1、TN=1；链路通过。positive IoU=0.0798仅为个例。

## 局限与混杂因素
n=1；positive IoU=0.0798是个例。

## 可支持的结论
functional smoke only；不得作为科学性能结论。

## 不支持的结论 / Claim 边界
只支持链路可运行，不支持模型科学性能。

## 关键指标
{"records": 2, "TP": 1, "TN": 1, "FP": 0, "FN": 0, "status": "passed"}

## 审核入口
remote config/run.md；logs/run.log；analysis/smoke_summary.json；generated texts；metrics。

## 过程记录与补充细节
canonical_run_id=E003-R-003-torch-compat-smoke-local-lasot-n1；registry自动ID仅为工具映射。

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
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-003-torch-compat-smoke-local-lasot-n1/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-003-torch-compat-smoke-local-lasot-n1

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-003-torch-compat-smoke-local-lasot-n1

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
- run_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-003-torch-compat-smoke-local-lasot-n1
- log_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-003-torch-compat-smoke-local-lasot-n1/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-003-torch-compat-smoke-local-lasot-n1
- metrics_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-003-torch-compat-smoke-local-lasot-n1/metrics.json
- tmux_session: incontext-E-003-E003-R-003-torch-compat-smoke-local-lasot-n1
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-20T17:17:12+08:00
- updated: 2026-07-20T17:46:03

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
