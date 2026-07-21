# E003-R-002-joint-f1-n140-failed-env · E003-R-002-joint-f1-n140-failed-env

- canonical_run_id: `E003-R-002-joint-f1-n140-failed-env`
- legacy_registry_ids: R-015

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
failed

## 本轮目的
首次运行Joint F1 n140并审计环境兼容性。

## 必要性 / 证据链位置
记录首次主评测失败，防止零记录被误读为零性能，并定位环境阻塞。

## 研究依据 / 被审计对象
no-silent-zero与失败run保留原则。

## 实现方式（简版）
failed main diagnostic attempt。

## 实现方式（详细版）
Torch 2.2.2存在torch.compiler但缺is_compiling；processor调用失败后脚本跳过记录，随后ZeroDivisionError。

## 数据身份与构造
计划同R-001 n140；实际valid records=0。

## 数据规模
0 valid records。

## 模型、权重与关键配置
torch2.2.2缺torch.compiler.is_compiling；transformers/peft调用失败。

## 变量、干预与对照
无科学变量；环境失败审计。

## 指标与计数规则
无有效指标。

## 完整性门槛 / no-silent-zero
要求280 records且traceback=0；实际0 records并ZeroDivisionError，gate失败。

## 观测结果摘要
零有效prediction；所有零指标均非模型性能。

## 局限与混杂因素
全部输出无效。

## 可支持的结论
environment failure only；不得引用metrics或outputs。

## 不支持的结论 / Claim 边界
不得引用任何0 metric为模型性能。

## 关键指标
{"valid_records": 0, "error": "torch.compiler.is_compiling missing", "post_error": "ZeroDivisionError"}

## 审核入口
remote config/run.md；logs/run.log；空outputs/失败metrics。

## 过程记录与补充细节
canonical_run_id=E003-R-002-joint-f1-n140-failed-env；registry自动ID仅为工具映射。legacy_mapping=E-002/R-017-qwen3vl-joint-f1-iou-local-lasot-n140。

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
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-002-joint-f1-n140-failed-env/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-002-joint-f1-n140-failed-env

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-002-joint-f1-n140-failed-env

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
- run_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-002-joint-f1-n140-failed-env
- log_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-002-joint-f1-n140-failed-env/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-002-joint-f1-n140-failed-env
- metrics_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-002-joint-f1-n140-failed-env/metrics.json
- tmux_session: incontext-E-003-E003-R-002-joint-f1-n140-failed-env
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-20T17:17:11+08:00
- updated: 2026-07-20T17:46:03

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
