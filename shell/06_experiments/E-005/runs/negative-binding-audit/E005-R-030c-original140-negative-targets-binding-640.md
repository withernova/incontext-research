# E005-R-030c-original140-negative-targets-binding-640 · original E003 same-class negative n140 separate640 diagnostic

- canonical_run_id: `E005-R-030c-original140-negative-targets-binding-640`
- group_id: negative-binding-audit
- run_type: （待分类）
- review_status: legacy
- review_round: 0
- submitted_for_review_at: 
- approved_at: 
- approved_by: 
- execution_authorized_at: 
- execution_authorized_by: 
- execution_authorization_consumed_at: 
- execution_dispatch_id: 
- execution_dispatch_latest_status: 
- legacy_registry_ids: （无）

> 已分组 Run 位于 `runs/<group-id>/<run-id>.md`；未分组 Run 位于 `runs/<run-id>.md`。
> Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
completed_passed_integrity

## 本轮目的
单独审计negative自然拒绝/接受及reference lookback。

## 必要性 / 证据链位置
negative不得与positive localization error/correct混算。

## 研究依据 / 被审计对象
E003-R004b冻结negative targets与归档自然输出。

## 实现方式（简版）
140/140标准eager640 archived-output replay。

## 实现方式（详细版）
candidate IoU仅表示与distractor GT重叠。

## 数据身份与构造
same-class negative targets n140；TN136/FP4。

## 数据规模
140 records,0 unalignable

## 模型、权重与关键配置
Qwen3-VL-8B+IPLoc LoRA bf16 max_side640 eager

## 变量、干预与对照
positive/negative结论严格分离

## 指标与计数规则
TN/FP；attention target mass/hit为独立诊断

## 完整性门槛 / no-silent-zero
140/140 aligned,finite,exit0

## 竞争假设与预期特征
（待补充）

## 验收条件
（待补充）

## 依赖的 Run / 证据
（待补充）

## 观测结果摘要
negative n140：identification TN136，FP4；140/140 aligned。TN的G→R/Q→R/Q→Q hit=93.4%/14.7%/65.4%；FP n4只描述不推断。

## 局限与混杂因素
FP仅4；generic error/correct标签不具定位含义

## 可支持的结论
negative单列；candidate-IoU不是personalized localization correctness；generic discrepancy group标签不解释。

## 不支持的结论 / Claim 边界
candidate-IoU不是personalized localization correctness。

## Artifacts
（待补充）

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-030c-original140-negative-targets-binding-640; shell/06_experiments/E-005/dual_gpu_640_core_results.md

## 过程记录与补充细节
（待补充）

## 指标观测
（尚无结构化观测）

## Run 审核
### 用户补充要求
（待补充）
### 用户疑问
（待补充）
### Agent 完善说明
（待补充）
### Agent 对疑问的回应
（待补充）
### 本次执行授权备注
（待补充）
### 自动审核快照
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r029c_r030c_B_640.sh

### 配置/超参数
（待补充）

### Seed
20260728

### 日志路径
/home/featurize/work/mechanism/explog/E-005/e005_original140_640_recovery_c.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-030c-original140-negative-targets-binding-640/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-030c-original140-negative-targets-binding-640

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
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-030c-original140-negative-targets-binding-640
- log_file: /home/featurize/work/mechanism/explog/E-005/e005_original140_640_recovery_c.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-030c-original140-negative-targets-binding-640/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-030c-original140-negative-targets-binding-640/metrics.json
- tmux_session: incontext-E-005-E005-R-030c-original140-negative-targets-binding-640
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 Steward/Watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-28T22:20:42
- updated: 2026-08-17T12:53:40

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
