# E005-R-002b-qwen3vl-self-contained-attention-smoke · 自包含synthetic-reference真实attention恢复smoke

- canonical_run_id: `E005-R-002b-qwen3vl-self-contained-attention-smoke`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
failed_preflight

## 本轮目的
在LaSOT源数据恢复前，用存活query生成的自包含reference crop完成真实模型/eager attention工程门禁。

## 必要性 / 证据链位置
尽早验证模型、LoRA、显存和span实现，同时不等待数据恢复；失败R-002保持独立。

## 研究依据 / 被审计对象
R-002仅因reference FileNotFoundError失败；synthetic query图像仍完整。

## 实现方式（简版）
从query A bbox加10% padding裁出reference，使用同一Qwen attention脚本运行双图eager forward。

## 实现方式（详细版）
reference来源于query，存在身份泄漏；严格限定为工程恢复smoke，不进入head discovery数据。

## 数据身份与构造
E004 synthetic sample 0 query及其A实例crop；reference/query非独立。

## 数据规模
1 prompt，2 spans，2 forwards。

## 模型、权重与关键配置
Qwen3-VL-8B + IPLoc-ID LoRA；bf16 eager；max_side=224；offline。

## 变量、干预与对照
同一prompt分别导出reference/query span；无科学处理组。

## 指标与计数规则
shape、finite、grid/span一致、eager、GPU peak、repo-original selected count。

## 完整性门槛 / no-silent-zero
36×32×1×V；V=HxW；两spans；finite；正常退出。

## 观测结果摘要
输入构造阶段失败：smoke wrapper遗漏IArgs.data_path，尚未加载模型。

## 局限与混杂因素
reference由query裁出，identity leakage严重；不能进入pilot/discovery结论。

## 可支持的结论
wrapper参数缺失，不是模型/attention失败；修复后另建R-002c。

## 不支持的结论 / Claim 边界
只允许确认真实attention工程链可运行；正式pilot仍需恢复独立reference数据。

## 关键指标
0 forwards；AttributeError IArgs.data_path。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-002b-qwen3vl-self-contained-attention-smoke; /home/featurize/work/mechanism/explog/E-005/recovery_manifests/E005_R002b_self_contained_smoke.json

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
/home/featurize/work/mechanism/scripts/e005/e005_r002_attention_smoke.py --max-side 224

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-002b-qwen3vl-self-contained-attention-smoke/logs/smoke.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-002b-qwen3vl-self-contained-attention-smoke/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-002b-qwen3vl-self-contained-attention-smoke

### tmux session
e005_attention_smoke

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-002b-qwen3vl-self-contained-attention-smoke
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-002b-qwen3vl-self-contained-attention-smoke/logs/smoke.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-002b-qwen3vl-self-contained-attention-smoke/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-002b-qwen3vl-self-contained-attention-smoke/metrics.json
- tmux_session: e005_attention_smoke
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T14:29:10
- updated: 2026-07-24T14:30:02

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
