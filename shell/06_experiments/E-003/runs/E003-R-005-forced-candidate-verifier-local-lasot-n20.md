# E003-R-005-forced-candidate-verifier-local-lasot-n20 · E003-R-005-forced-candidate-verifier-local-lasot-n20

- canonical_run_id: `E003-R-005-forced-candidate-verifier-local-lasot-n20`
- legacy_registry_ids: R-018

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
failed

## 本轮目的
启动forced-candidate verifier pilot。

## 必要性 / 证据链位置
验证candidate-conditioned verifier前先跑n20 pilot。

## 研究依据 / 被审计对象
论文将answer描述为p(A|x,B,Q)，需要固定B的反事实probe。

## 实现方式（简版）
failed pre-inference。

## 实现方式（详细版）
外部script路径启动时未设置IPLoc-ID PYTHONPATH，loc_dataset导入失败。

## 数据身份与构造
计划manifest前20samples/40targets/六modes；实际pre-inference失败。

## 数据规模
0 valid scientific outputs。

## 模型、权重与关键配置
Qwen3-VL-8B+IPLoc-ID LoRA；外部script入口。

## 变量、干预与对照
尚未形成有效candidate变量。

## 指标与计数规则
无科学metric。

## 完整性门槛 / no-silent-zero
要求成功import并产生记录；实际ModuleNotFoundError且0 outputs。

## 观测结果摘要
ModuleNotFoundError: No module named loc_dataset。

## 局限与混杂因素
缺PYTHONPATH。

## 可支持的结论
engineering failure only；无模型指标。

## 不支持的结论 / Claim 边界
engineering failure only；无模型结论。

## 关键指标
{"valid_outputs": 0, "error": "ModuleNotFoundError: loc_dataset"}

## 审核入口
config/run.md；logs/run.log。

## 过程记录与补充细节
canonical_run_id=E003-R-005-forced-candidate-verifier-local-lasot-n20；registry自动ID仅为工具映射。

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
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-005-forced-candidate-verifier-local-lasot-n20/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-005-forced-candidate-verifier-local-lasot-n20

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-005-forced-candidate-verifier-local-lasot-n20

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
- run_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-005-forced-candidate-verifier-local-lasot-n20
- log_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-005-forced-candidate-verifier-local-lasot-n20/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-005-forced-candidate-verifier-local-lasot-n20
- metrics_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-005-forced-candidate-verifier-local-lasot-n20/metrics.json
- tmux_session: incontext-E-003-E003-R-005-forced-candidate-verifier-local-lasot-n20
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-20T17:17:12+08:00
- updated: 2026-07-20T17:46:51

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
