# E003-R-001-data-rehydrate-local-lasot-n140 · E003-R-001-data-rehydrate-local-lasot-n140

- canonical_run_id: `E003-R-001-data-rehydrate-local-lasot-n140`
- legacy_registry_ids: R-014

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed

## 本轮目的
重建本地可运行的LaSOT POIL manifest。

## 必要性 / 证据链位置
官方JSON与本地LaSOTTesting不匹配；主评测前必须建立可审计manifest并明确非官方身份。

## 研究依据 / 被审计对象
论文说明每sample共享reference并含positive/negative query，LaSOT test为140 samples且使用in-class negatives。[[personal2026]] §3.5、§3.5.1、§3.5.3。

## 实现方式（简版）
数据准备；不运行模型。

## 实现方式（详细版）
reference=目标sequence首帧；positive=同sequence末帧；negative=同类另一sequence中间帧；确定性重建。

## 数据身份与构造
reference=目标sequence首帧；positive=同sequence末帧；negative=另一同类sequence中间帧；local deterministic reconstruction，非官方split。

## 数据规模
140 samples/70 classes；140 positive+140 same-class negative。

## 模型、权重与关键配置
data preparation only；不加载模型。

## 变量、干预与对照
确定性构造；无随机模型干预。

## 指标与计数规则
完整性只计samples/classes/positive/negative/missing images/invalid bbox。

## 完整性门槛 / no-silent-zero
140 samples；70 classes；140 positive+140 negative；missing=0；invalid_bbox=0。

## 观测结果摘要
missing images=0；invalid bbox=0。

## 局限与混杂因素
未知是否与作者held-out class selection、frame uniform sampling和negative sequence选择完全一致。

## 可支持的结论
仅支持本地数据链路；不是官方IPLoc-ID split。

## 不支持的结论 / Claim 边界
仅支持本地数据链路完整；不可称官方split或论文Table8复现。

## 关键指标
{"samples": 140, "classes": 70, "positive": 140, "negative": 140, "missing": 0, "invalid_bbox": 0}

## 审核入口
remote config/run.md；logs/run.log；manifest=/home/featurize/data/e002_manifests/LASOT_local_1shot_T2_n140_v2.json。

## 过程记录与补充细节
canonical_run_id=E003-R-001-data-rehydrate-local-lasot-n140；registry自动ID仅为工具映射。legacy_mapping=E-002/R-016-data-rehydrate-joint-verifier。

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
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-001-data-rehydrate-local-lasot-n140/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-001-data-rehydrate-local-lasot-n140

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-001-data-rehydrate-local-lasot-n140

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
- run_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-001-data-rehydrate-local-lasot-n140
- log_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-001-data-rehydrate-local-lasot-n140/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-001-data-rehydrate-local-lasot-n140
- metrics_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-001-data-rehydrate-local-lasot-n140/metrics.json
- tmux_session: incontext-E-003-E003-R-001-data-rehydrate-local-lasot-n140
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-20T17:17:11+08:00
- updated: 2026-07-20T17:46:03

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
