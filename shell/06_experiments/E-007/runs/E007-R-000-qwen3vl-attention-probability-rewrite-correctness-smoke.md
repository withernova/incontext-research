# E007-R-000-qwen3vl-attention-probability-rewrite-correctness-smoke · qwen3vl-attention-probability-rewrite-correctness-smoke

- canonical_run_id: `E007-R-000-qwen3vl-attention-probability-rewrite-correctness-smoke`
- run_type: engineering_smoke
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-04T20:44:51
- approved_at: 2026-08-04T20:45:57
- execution_authorized_at: 2026-08-04T20:46:00
- execution_authorization_consumed_at: 2026-08-04T20:57:36
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
planned

## 本轮目的
验证Qwen3-VL eager attention中可在softmax后、dropout前、A@V前精确重写指定layer/head/query-row→reference-key span的attention probabilities，并确保identity rewrite严格复现baseline。

## 必要性 / 证据链位置
若hook只改输出attention张量而未进入A@V，后续所有行为变化/不变均不可解释；先建立最小数学与实现correctness gate。

## 研究依据 / 被审计对象
E004-R-010已验证pre-o_proj head-output activation patch slice correctness，但尚未验证attention-probability级A@V rewrite。Qwen3-VL为36层×32Q heads，GQA 8KV heads，head_dim128。

## 实现方式（简版）
单个已归档正样本、单层单head单row开始；捕获原softmax A，执行identity、shape rewrite、zero-reference、one-hot-reference，比较手算A@V、module head output、o_proj前后差异。之后扩展到main4四heads和bbox rows。

## 实现方式（详细版）
hook层级固定为attention forward内部softmax后/dropout前。Primary rewrite：对reference span R，alpha=sum_R A；给定归一化S，A_R←alpha*S，非R保持原值；数值和应为1。Identity S=A_R/alpha；alpha=0时只允许identity/no-op并记录，不做除零。GQA target head使用其对应KV group，但继续使用target自身V，不移植source V/output。

## 数据身份与构造
复用E006-R-006中1个parseable positive及其exact natural response；两个image spans、bbox token positions与p-1 rows必须重新审计。此run仅工程smoke，不产生科学样本结论。

## 数据规模
n=1；单head/单row→单head/all bbox rows→historical main4/all bbox rows；每个condition重复2次。

## 模型、权重与关键配置
Qwen3-VL-8B-Instruct+IPLoc-ID 1shot LoRA，bf16 eager，max_side=640，max_memory={0:22GiB}+CPU offload；同一次load。

## 变量、干预与对照
baseline unhooked；hook no-op；identity rewrite；reference-zero并将mass按原比例返还non-reference；one-hot/reference-shape synthetic；full-reference uniform。干预层级=attention probability representation-level。

## 指标与计数规则
baseline/no-op/identity logits max_abs_diff；pre-o_proj head output max_abs_diff；手算(A@V)与module output误差；attention row sum误差；非target layer/head/row差异；重复运行误差。

## 完整性门槛 / no-silent-zero
identity logits max_abs_diff<=1e-5(fp32 hook accumulation后回原dtype可放宽至5e-4并预声明实际阈值)；no-op相同；手算A@V误差<=5e-4；仅target slices变化；row sums误差<=1e-6 fp32；全部finite；hook移除后baseline恢复。任一失败停止E007后续。

## 竞争假设与预期特征
identity/no-op完全复现，nontrivial rewrite改变target A@V与logits；否则修复实现，不解释科学结果。

## 验收条件
GATE_PASS及完整tensor-shape/hash/误差summary；失败尝试独立归档。

## 依赖的 Run / 证据
E006-R-006；E004-R-010；Qwen eager attention local code。

## 观测结果摘要
（待补充）

## 局限与混杂因素
单样本纯工程验证；nontrivial输出变化不代表有益或机制重要。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
只验证干预真实进入A@V且实现数值正确。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-004/runs/E004-R-010-single-head-activation-patching-correctness-smoke.md; shell/06_experiments/E-006/runs/E006-R-006-exact-last-token-bbox-row-alignment-gate-n10-640.md

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
20260804

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
- project_dir: /home/featurize/work/mechanism/E-007
- run_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-000-qwen3vl-attention-probability-rewrite-correctness-smoke
- log_file: /home/featurize/work/mechanism/explog/E-007/E007-R-000-qwen3vl-attention-probability-rewrite-correctness-smoke/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-000-qwen3vl-attention-probability-rewrite-correctness-smoke/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-007/E007-R-000-qwen3vl-attention-probability-rewrite-correctness-smoke/metrics.json
- tmux_session: incontext-E-007-E007-R-000-qwen3vl-attention-probability-rewrite-correctness-smoke
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T20:44:43
- updated: 2026-08-04T20:57:36

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
