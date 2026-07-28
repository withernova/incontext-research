# E005-R-007b-positive-query-role-specific-selection-n80 · positive-query role-specific selection schema recovery

- canonical_run_id: `E005-R-007b-positive-query-role-specific-selection-n80`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed

## 本轮目的
修复R-007 schema错误并完成post-hoc role-specific候选冻结。

## 必要性 / 证据链位置
R-007使用错误键global_index；R-005实际为sample_index。

## 研究依据 / 被审计对象
R-007 traceback与R-005 records schema。

## 实现方式（简版）
显式读取sample_index；indices0:79 positive-query top5频率。

## 实现方式（详细版）
其余协议与R-007一致。

## 数据身份与构造
R-005 records indices0:79。

## 数据规模
80 records。

## 模型、权重与关键配置
离线。

## 变量、干预与对照
positive-query only；top5。

## 指标与计数规则
frequency。

## 完整性门槛 / no-silent-zero
80 records、5 heads、exit0。

## 观测结果摘要
post-hoc positive-query role-specific selection完成。

## 局限与混杂因素
post-hoc recovery。

## 可支持的结论
仅冻结供indices80:99内部recovery diagnostic；不能覆盖R-006负结果，indices100:139禁止再次作为confirmatory held-out。

## 不支持的结论 / Claim 边界
内部诊断候选，不覆盖R-006。

## 关键指标
n=80；fixed=L02H17(40),L04H03(25),L12H21(23),L23H28(13),L21H23(12)。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-007b-positive-query-role-specific-selection-n80; /home/featurize/work/mechanism/explog/E-005/runs/E005-R-005-lasot-iplocid-attention-discovery-n100/results/attention_records.json

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r007b_role_specific_select.py --train-end 80 --top-k 5

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-007b-positive-query-role-specific-selection-n80/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-007b-positive-query-role-specific-selection-n80/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-007b-positive-query-role-specific-selection-n80

### tmux session
e005_role_select

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-007b-positive-query-role-specific-selection-n80
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-007b-positive-query-role-specific-selection-n80/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-007b-positive-query-role-specific-selection-n80/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-007b-positive-query-role-specific-selection-n80/metrics.json
- tmux_session: e005_role_select
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T15:34:29
- updated: 2026-07-24T15:34:45

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
