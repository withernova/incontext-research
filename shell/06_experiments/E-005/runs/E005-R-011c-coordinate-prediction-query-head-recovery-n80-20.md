# E005-R-011c-coordinate-prediction-query-head-recovery-n80-20 · coordinate-prediction query recovery（metadata修复）

- canonical_run_id: `E005-R-011c-coordinate-prediction-query-head-recovery-n80-20`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed_quality_gate

## 本轮目的
从gold bbox坐标预测rows发现并验证定位heads。

## 必要性 / 证据链位置
R-011b仅metadata索引失败；核心唯一子序列和首样本前向通过。

## 研究依据 / 被审计对象
metadata改为直接记录已唯一匹配的coord_ids。

## 实现方式（简版）
0:79 discovery，冻结top5，80:99 internal GT validation与turbo图。

## 实现方式（详细版）
teacher-forced gold answer；唯一连续bbox子序列；p-1 rows；repo-original selection。

## 数据身份与构造
positive query 0:79/80:99。

## 数据规模
80+20 samples。

## 模型、权重与关键配置
Qwen3-VL+LoRA eager bf16 224。

## 变量、干预与对照
GT不参与选头；all-head matched control。

## 指标与计数规则
frequency、GT enrichment、pointing、percentile。

## 完整性门槛 / no-silent-zero
唯一匹配、p-1、span/grid/finite、quality gates。

## 观测结果摘要
坐标预测query恢复成功：80样本repo discovery冻结5 heads，20样本内部GT审核三项quality gates全部通过；10组turbo图已生成。

## 局限与混杂因素
post-hoc；teacher-forced；非confirmatory；attention非因果。

## 可支持的结论
teacher-forced bbox-coordinate prediction rows能恢复明显GT-concentrated attention heads，支持旧失败主要源自newline query。结果为post-hoc/internal recovery且使用gold bbox teacher forcing；尚非新数据confirmatory，也非因果证据。

## 不支持的结论 / Claim 边界
恢复诊断，通过后需新数据确认。

## 关键指标
fixed=L18H15,L19H03,L24H27,L22H00,L20H08；selected median GT enrichment=7.965, mean=9.651；pointing=0.27 vs all-head 0.0698；median all-head percentile=0.9727；combined median enrichment=4.136, pointing=0.35；gates=3/3。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-011c-coordinate-prediction-query-head-recovery-n80-20

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r011c_coord_query_recovery.py

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-011c-coordinate-prediction-query-head-recovery-n80-20/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-011c-coordinate-prediction-query-head-recovery-n80-20/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-011c-coordinate-prediction-query-head-recovery-n80-20

### tmux session
e005_coord_recovery_c

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-011c-coordinate-prediction-query-head-recovery-n80-20
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-011c-coordinate-prediction-query-head-recovery-n80-20/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-011c-coordinate-prediction-query-head-recovery-n80-20/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-011c-coordinate-prediction-query-head-recovery-n80-20/metrics.json
- tmux_session: e005_coord_recovery_c
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T16:27:12
- updated: 2026-07-24T16:29:35

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
