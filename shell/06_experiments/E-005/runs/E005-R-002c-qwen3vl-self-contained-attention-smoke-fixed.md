# E005-R-002c-qwen3vl-self-contained-attention-smoke-fixed · 自包含真实attention smoke参数修复

- canonical_run_id: `E005-R-002c-qwen3vl-self-contained-attention-smoke-fixed`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed

## 本轮目的
修复R-002b输入wrapper的data_path字段后完成真实模型attention工程门禁。

## 必要性 / 证据链位置
R-002b在模型加载前失败；需继续顺序验证。

## 研究依据 / 被审计对象
R-002b traceback明确指向IArgs.data_path缺失。

## 实现方式（简版）
补充ia.data_path=a.manifest，其余设置不变。

## 实现方式（详细版）
reference仍为query crop，严格工程用途；失败attempt单独保留。

## 数据身份与构造
自包含synthetic reference/query，identity leakage。

## 数据规模
1 prompt，2 spans，2 forwards。

## 模型、权重与关键配置
Qwen3-VL-8B+IPLoc-ID LoRA；bf16 eager；max_side=224；offline。

## 变量、干预与对照
与R-002b仅wrapper字段修复。

## 指标与计数规则
shape/finite/grid/eager/GPU peak/selected count。

## 完整性门槛 / no-silent-zero
36×32×1×V；两spans；finite；正常退出。

## 观测结果摘要
真实Qwen3-VL/IPLoc-ID eager-attention工程链通过；双图动态矩形span与repo-original分析均成功。

## 局限与混杂因素
synthetic self-reference；非科学数据。

## 可支持的结论
支持24GB GPU上的低分辨率单样本eager-attention工程可行性；不支持稳定head或grounding结论。

## 不支持的结论 / Claim 边界
只支持工程链可行；正式pilot必须独立数据。

## 关键指标
reference [36,32,1,78], grid 6x13, selected=85；query [36,32,1,72], grid 6x12, selected=217；均finite；peak allocated=17,859,711,488 bytes，reserved=18,041,798,656 bytes；first forward=3.708s，second=0.173s。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-002c-qwen3vl-self-contained-attention-smoke-fixed

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r002_attention_smoke.py --max-side 224

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-002c-qwen3vl-self-contained-attention-smoke-fixed/logs/smoke.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-002c-qwen3vl-self-contained-attention-smoke-fixed/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-002c-qwen3vl-self-contained-attention-smoke-fixed

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
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-002c-qwen3vl-self-contained-attention-smoke-fixed
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-002c-qwen3vl-self-contained-attention-smoke-fixed/logs/smoke.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-002c-qwen3vl-self-contained-attention-smoke-fixed/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-002c-qwen3vl-self-contained-attention-smoke-fixed/metrics.json
- tmux_session: e005_attention_smoke
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T14:30:04
- updated: 2026-07-24T14:33:01

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
