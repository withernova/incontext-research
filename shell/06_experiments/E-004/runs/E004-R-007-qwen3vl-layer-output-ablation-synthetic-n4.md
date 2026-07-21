# E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4 · E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4

- canonical_run_id: `E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_diagnostic

## 本轮目的
扫描36层attention-output zero-ablation的Yes/No margin效应。

## 必要性 / 证据链位置
工程漏斗与polarity诊断；后经方法审计明确不能用于CMA head发现。

## 研究依据 / 被审计对象
与Mechanisms论文方法对照后永久降级为layer-output ablation diagnostic。

## 实现方式（简版）
4 quartets×4 conditions×(clean+36 layer zero ablations)，共592 records。

## 实现方式（详细版）
（待补充）

## 数据身份与构造
synthetic double-instance 4 quartets/16 conditions。

## 数据规模
（待补充）

## 模型、权重与关键配置
（待补充）

## 变量、干预与对照
（待补充）

## 指标与计数规则
clean与layer-zero后的Yes-No signed/aligned margin effect。

## 完整性门槛 / no-silent-zero
592/592 finite records；分condition与quartet保存。

## 观测结果摘要
（待补充）

## 局限与混杂因素
zero ablation不能证明removed-object information mediation；synthetic behavioral gate失败。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
只能说明decision-polarity-sensitive layers；不得称CMA/MF或identity heads。

## 关键指标
（待补充）

## 审核入口
/home/featurize/work/mechanism/explog/E-004/runs/E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4/logs; /home/featurize/work/mechanism/explog/E-004/runs/E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4/results; /home/featurize/work/mechanism/explog/E-004/runs/E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4/analysis; shell/06_experiments/E-004/runs/E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4.md

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
（待补充）

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-004/runs/E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-004/runs/E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-004/runs/E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4

### tmux session
e004_layer_scan

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-004
- run_dir: /home/featurize/work/mechanism/explog/E-004/runs/E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4
- log_file: /home/featurize/work/mechanism/explog/E-004/runs/E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-004/runs/E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4
- metrics_file: /home/featurize/work/mechanism/explog/E-004/runs/E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4/metrics.json
- tmux_session: e004_layer_scan
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-20T22:30:50
- updated: 2026-07-20T22:30:50

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
