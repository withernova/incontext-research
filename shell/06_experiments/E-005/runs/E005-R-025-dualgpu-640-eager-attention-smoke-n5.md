# E005-R-025-dualgpu-640-eager-attention-smoke-n5 · dual RTX4090 max_side640 standard eager attention smoke n5

- canonical_run_id: `E005-R-025-dualgpu-640-eager-attention-smoke-n5`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed_integrity

## 本轮目的
验证双卡能否在公开代码默认640分辨率收集Qwen3-VL完整标准eager attention。

## 必要性 / 证据链位置
后续n280核心discrepancy需消除640自然生成到224 replay的分辨率混杂。

## 研究依据 / 被审计对象
双RTX4090各24GB；模型10 shards；公开代码max_side默认640。

## 实现方式（简版）
5个分散样本；两图；output_attentions=True；eager；device_map auto；每卡max_memory22GiB。

## 实现方式（详细版）
记录sequence length、merged grids、attention shape/finite与双卡peak allocated。

## 数据身份与构造
R-024 positive-only n280的indices 0,57,114,171,279。

## 数据规模
n5 smoke

## 模型、权重与关键配置
Qwen3-VL-8B+IPLoc LoRA bf16 dual GPU max_side640

## 变量、干预与对照
标准HF eager，不做selective近似

## 指标与计数规则
5/5 forwards finite and span/grid valid; peak memory

## 完整性门槛 / no-silent-zero
5 records; 36 layers; two spans; finite; exit0

## 观测结果摘要
5/5 max_side640 standard eager forwards passed; 36 layers finite; peak GPU memory 8.17/9.71 GiB; exit0.

## 局限与混杂因素
smoke不提供科学组间结果

## 可支持的结论
双RTX4090可运行两图640标准完整eager attention。

## 不支持的结论 / Claim 边界
只决定是否可运行640正式attention实验。

## 关键指标
（待补充）

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-025-dualgpu-640-eager-attention-smoke-n5

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r025_640_attention_smoke.py

### 配置/超参数
（待补充）

### Seed
20260728

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-025-dualgpu-640-eager-attention-smoke-n5/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-025-dualgpu-640-eager-attention-smoke-n5/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-025-dualgpu-640-eager-attention-smoke-n5

### tmux session
e005_640_smoke

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-025-dualgpu-640-eager-attention-smoke-n5
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-025-dualgpu-640-eager-attention-smoke-n5/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-025-dualgpu-640-eager-attention-smoke-n5/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-025-dualgpu-640-eager-attention-smoke-n5/metrics.json
- tmux_session: e005_640_smoke
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-28T20:13:36
- updated: 2026-07-28T21:01:08

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
