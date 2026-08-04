# E007-R-003-natural-generation-qtor-shape-transplant-pilot-n20 · natural-generation-qtor-shape-transplant-pilot-n20

- canonical_run_id: `E007-R-003-natural-generation-qtor-shape-transplant-pilot-n20`
- run_type: causal_behavior_pilot
- review_status: pending_review
- review_round: 1
- submitted_for_review_at: 2026-08-04T20:44:51
- approved_at: 
- execution_authorized_at: 
- execution_authorization_consumed_at: 
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
planned

## 本轮目的
在online-causal bbox-generation window真实自然生成中测试Q→R shape-only transplant是否改善自然bbox IoU并保持Yes/parse，且优于spatial/mismatch/container controls。

## 必要性 / 证据链位置
teacher replay不能证明行为改善；必须让干预进入真实自回归生成并评价自然response。

## 研究依据 / 被审计对象
仅在R000/R001 correctness通过且R002提供可行方向后执行。自然行为是因果主张的必要条件。

## 实现方式（简版）
n20同一model load顺序运行baseline、identity、matched、R180、mismatched、uniform-bbox、knockout；从first generated step启用，到首个合法bbox闭括号关闭。每condition独立从同一prompt greedy generate，不借用baseline tokens/bbox。

## 实现方式（详细版）
shape-only逐row保持当前condition自身alpha；source map仅由该样本prompt-stage G→R预先缓存。若condition自然无bbox，按parse failure记录，绝不借baseline bbox。干预结束后继续自然生成self-query与Yes/No。condition顺序按sample hash轮转以控制缓存/顺序。

## 数据身份与构造
R001冻结20 sequence-unique positives，10 historical error+10 correct；自然输出重新生成。

## 数据规模
20×7 generations；pilot。

## 模型、权重与关键配置
IPLoc-ID LoRA，原prompt，max_side640，greedy及原max_new_tokens。

## 变量、干预与对照
baseline；identity；matched；R180；mismatched cyclic donor；uniform reference bbox；Q→R knockout。

## 指标与计数规则
Primary natural bbox IoU paired matched-baseline；secondary parse、Yes、accepted-positive IoU、Joint correctness、response edit type。Matched相对R180/mismatched/uniform对照；sequence paired bootstrap仅描述，n20不作最终显著性。

## 完整性门槛 / no-silent-zero
identity response/token/logits与baseline一致；各condition自己的stream parser；无未来信息；无borrowed bbox；20×7完整或列失败；matched改善不得伴随大规模parse/Yes崩溃。

## 竞争假设与预期特征
matched改善且优于R180/mismatch支持reference spatial route因果相关；uniform同等改善支持container routing；knockout变差提供necessity方向。

## 验收条件
升级R004条件：matched-baseline mean/median IoU方向为正、>=12/20不差、且matched优于R180与mismatch，parse/Yes下降<=1/20；不满足则停止扩大并报告null/mixed。

## 依赖的 Run / 证据
R000/R001通过；R002满足预设升级条件；用户另行批准执行。

## 观测结果摘要
（待补充）

## 局限与混杂因素
n20；online窗口含格式tokens；positive-only不能评价FP；attention改写可能OOD。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
仅为小样本自然行为pilot；不能形成最终Joint F1或identity结论。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
E003-R-004b outputs; E007-R-002 artifacts

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
- run_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-003-natural-generation-qtor-shape-transplant-pilot-n20
- log_file: /home/featurize/work/mechanism/explog/E-007/E007-R-003-natural-generation-qtor-shape-transplant-pilot-n20/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-003-natural-generation-qtor-shape-transplant-pilot-n20/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-007/E007-R-003-natural-generation-qtor-shape-transplant-pilot-n20/metrics.json
- tmux_session: incontext-E-007-E007-R-003-natural-generation-qtor-shape-transplant-pilot-n20
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T20:44:43
- updated: 2026-08-04T20:44:51

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
