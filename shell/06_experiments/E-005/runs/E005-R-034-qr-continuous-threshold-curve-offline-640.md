# E005-R-034-qr-continuous-threshold-curve-offline-640 · offline Q→R curve analysis first implementation

- canonical_run_id: `E005-R-034-qr-continuous-threshold-curve-offline-640`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
failed_implementation_no_scientific_output

## 本轮目的
分析Q→R连续指标与阈值曲线。

## 必要性 / 证据链位置
检查strict hit是否遗漏distributed mass。

## 研究依据 / 被审计对象
冻结R027/R028/R029c summaries。

## 实现方式（简版）
脚本启动即因系统Python缺scipy失败。

## 实现方式（详细版）
无统计结果、无新forward。

## 数据身份与构造
none consumed to completion

## 数据规模
0 valid outputs

## 模型、权重与关键配置
offline only

## 变量、干预与对照
no model

## 指标与计数规则
planned target mass/enrichment curves

## 完整性门槛 / no-silent-zero
failed before output

## 观测结果摘要
（待补充）

## 局限与混杂因素
ModuleNotFoundError scipy

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
无科学结论。

## 关键指标
（待补充）

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-034-qr-continuous-threshold-curve-offline-640/logs/run.log

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
/tmp/e005_r034_qr.py

### 配置/超参数
（待补充）

### Seed
20260728

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-034-qr-continuous-threshold-curve-offline-640/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-034-qr-continuous-threshold-curve-offline-640/analysis

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-034-qr-continuous-threshold-curve-offline-640

### tmux session
（待补充）

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-034-qr-continuous-threshold-curve-offline-640
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-034-qr-continuous-threshold-curve-offline-640/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-034-qr-continuous-threshold-curve-offline-640/analysis
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-034-qr-continuous-threshold-curve-offline-640/metrics.json
- tmux_session: incontext-E-005-E005-R-034-qr-continuous-threshold-curve-offline-640
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-28T23:12:15
- updated: 2026-07-28T23:12:15

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
