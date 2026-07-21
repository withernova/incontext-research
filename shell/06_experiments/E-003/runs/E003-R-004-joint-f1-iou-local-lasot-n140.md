# E003-R-004-joint-f1-iou-local-lasot-n140 · E003-R-004-joint-f1-iou-local-lasot-n140

- canonical_run_id: `E003-R-004-joint-f1-iou-local-lasot-n140`
- legacy_registry_ids: R-017

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
aborted

## 本轮目的
运行Joint F1主实验的首次生成长度配置。

## 必要性 / 证据链位置
正式Joint F1首次尝试；检验generation长度是否覆盖最终Yes/No。

## 研究依据 / 被审计对象
主metric要求每条最终decision有效。

## 实现方式（简版）
aborted early / superseded。

## 实现方式（详细版）
max_new_tokens=80；约9/140时发现输出在verifier question处截断，未生成最终Yes/No。

## 数据身份与构造
计划同R-001完整n140。

## 数据规模
计划140 samples；未形成完整有效outputs。

## 模型、权重与关键配置
同主模型；max_new_tokens=80。

## 变量、干预与对照
仅generation length配置。

## 指标与计数规则
计划Joint F1；因截断未计算。

## 完整性门槛 / no-silent-zero
280完整records且每条有最终decision；约9/140发现截断，主动中止。

## 观测结果摘要
提前中止，无完整outputs/analysis；由R-004b t128取代。

## 局限与混杂因素
无完整outputs/analysis。

## 可支持的结论
不得引用任何科学指标。

## 不支持的结论 / Claim 边界
不得引用中止前任何指标；由R-004b取代。

## 关键指标
{"max_new_tokens": 80, "approx_progress_samples": 9, "complete": false}

## 审核入口
remote config/run.md；logs/run.log中的ABORTED_EARLY。

## 过程记录与补充细节
canonical_run_id=E003-R-004-joint-f1-iou-local-lasot-n140；registry自动ID仅为工具映射。superseded_by=E003-R-004b-joint-f1-iou-local-lasot-n140-t128。

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
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-004-joint-f1-iou-local-lasot-n140/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-004-joint-f1-iou-local-lasot-n140

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-004-joint-f1-iou-local-lasot-n140

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
- run_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-004-joint-f1-iou-local-lasot-n140
- log_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-004-joint-f1-iou-local-lasot-n140/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-004-joint-f1-iou-local-lasot-n140
- metrics_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-004-joint-f1-iou-local-lasot-n140/metrics.json
- tmux_session: incontext-E-003-E003-R-004-joint-f1-iou-local-lasot-n140
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-20T17:17:12+08:00
- updated: 2026-07-20T17:46:03

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
