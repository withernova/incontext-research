# E006-R-006-exact-last-token-bbox-row-alignment-gate-n10-640 · exact last-token vs first-generate-step vs bbox-pminus1 row gate

- canonical_run_id: `E006-R-006-exact-last-token-bbox-row-alignment-gate-n10-640`
- run_type: engineering_gate
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-03T15:05:27
- approved_at: 2026-08-03T15:06:15
- execution_authorized_at: 2026-08-03T15:06:32
- execution_authorization_consumed_at: 2026-08-03T15:24:22
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
planned

## 本轮目的
精确复现公开LocalizationHeads的last-token row并与E006 bbox p-1 rows对齐审计。

## 必要性 / 证据链位置
R-005不是repo-original last-token，不能作为原方法复现。

## 研究依据 / 被审计对象
LocalizationHeads README How Attention Is Collected；E006-R-005。

## 实现方式（简版）
同样本收集forward最后非padding输入token、generate first-step、natural bbox p-1 rows到双图spans。

## 实现方式（详细版）
记录token id/string/position、chat template、tensor shape、A/B差、bbox exact match；不重选head。

## 数据身份与构造
固定5 localization-error+5 localization-correct，仅工程gate。

## 数据规模
n=10

## 模型、权重与关键配置
Qwen3-VL-8B+IPLoc-ID LoRA, bf16 eager, max_side640

## 变量、干预与对照
row是唯一变量；相同prompt/image/model/head/span。

## 指标与计数规则
position/token audit；attention finite；last-token vs first-step max-abs diff；S50 maps仅可视化。

## 完整性门槛 / no-silent-zero
唯一image spans和bbox match；last nonpad token明确；first-step shape语义对齐；finite。

## 竞争假设与预期特征
确定repo last-token在Qwen模板中的真实token身份及其与bbox-row是否不同。

## 验收条件
10/10 alignment；零多重match；不静默删除newline。

## 依赖的 Run / 证据
现有model/LoRA与E003 manifests。

## 观测结果摘要
（待补充）

## 局限与混杂因素
工程gate无科学推断。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
通过仅表示row实现正确。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-006/followup_validity_and_equivariance_plan.md#r-006

## 过程记录与补充细节
（待补充）

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
20260728

### 日志路径
（待补充）

### 产物目录
（待补充）

### 真实产物根目录
（待补充）

### tmux session
（待补充）

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-006
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-006-exact-last-token-bbox-row-alignment-gate-n10-640
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-006-exact-last-token-bbox-row-alignment-gate-n10-640/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-006-exact-last-token-bbox-row-alignment-gate-n10-640/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-006-exact-last-token-bbox-row-alignment-gate-n10-640/metrics.json
- tmux_session: incontext-E-006-E006-R-006-exact-last-token-bbox-row-alignment-gate-n10-640
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-03T14:54:20
- updated: 2026-08-03T15:24:22

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
