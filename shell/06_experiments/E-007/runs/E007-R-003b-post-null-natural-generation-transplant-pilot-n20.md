# E007-R-003b-post-null-natural-generation-transplant-pilot-n20 · post-null-natural-generation-transplant-pilot-n20

- canonical_run_id: `E007-R-003b-post-null-natural-generation-transplant-pilot-n20`
- run_type: exploratory_causal_behavior_pilot
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-04T22:02:47
- approved_at: 2026-08-04T22:03:16
- execution_authorized_at: 2026-08-04T22:03:18
- execution_authorization_consumed_at: 2026-08-04T22:07:53
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
draft

## 本轮目的
在R-002 teacher-replay方向为null/mixed后，探索真实逐token自然生成中matched Q→R shape transplant是否改变bbox IoU，并完整展示历史baseline失败的rescue、无变化与新增损害。

## 必要性 / 证据链位置
teacher replay NLL不能回答自然bbox是否变化；用户关心不植入与植入后的mIoU/F1及失败样本是否恢复。由于R-002未满足原R-003升级条件，本run明确作为post-null探索，不冒充确认实验。

## 研究依据 / 被审计对象
继承E007-R-000真实A@V correctness、R-001冻结n20与source maps、R-002 matched未优于R180/mismatched的null/mixed结果；仅在R-002v在线实现与可视化gate通过后运行。

## 实现方式（简版）
对同一冻结n20 positives，在同一模型加载中分别从原prompt独立greedy生成baseline、identity、matched、R180、mismatched、uniform-bbox、uniform-reference和Q→R knockout。每个条件从第一生成prediction row开始干预，parser检测首个合法bbox闭括号后停止；不借用baseline或GT token。比较每条件自然bbox IoU，并对全部历史baseline失败逐例展示是否rescue，同时报告植入导致原正确样本变差的案例。

## 实现方式（详细版）
每condition重置KV cache和parser并从完全相同prompt独立生成；source map仅由该样本prompt-stage reference bbox rows在生成前缓存。shape-only逐步保留该condition当前row/head的alpha，非R不变且保留target V；knockout将alpha按原非R分布比例返还。条件顺序按sample hash确定的Latin/cyclic rotation控制顺序效应。baseline完全不经过rewrite；identity逐row写回自身原shape。保存每步token、parser state、rewrite audit、raw response、bbox、Yes/No、IoU和attention before/after。禁止用归档response决定在线关闭位置。

## 数据身份与构造
严格继承R-001冻结20个sequence-unique positive样本：10个历史natural IoU<0.1 localization-error与10个历史IoU>=0.7 localization-correct；分层仅用于描述，不按本次结果换样本。GT仅用于生成完成后的IoU评价。

## 数据规模
20×8=160次独立自然生成。positive-only pilot可计算bbox mIoU、parse、Yes与positive joint-success，但不能计算包含TN/FP的完整Identification F1或标准Joint F1。

## 模型、权重与关键配置
Qwen3-VL-8B-Instruct + 同一原IPLoc-ID LoRA；bf16 eager；max_side=640；max_memory={0:"22GiB",cpu:"120GiB"}；原官方消息构造；greedy/do_sample=False；与E003-R-004b归档自然生成完全相同的max_new_tokens、EOS和processor设置，配置无法核实时停止。seed=20260804。

## 变量、干预与对照
baseline；identity；matched；R180；fixed within-grid permutation不在本pilot主集（R-002已有）；mismatched cyclic donor；uniform reference-bbox；uniform full-reference；Q→R knockout。matched必须同时优于spatial、mismatch和container controls才允许空间特异解释。

## 指标与计数规则
Primary：sequence-paired delta IoU(matched-baseline)、matched改善/不差/变差计数。Secondary：各condition parse、Yes、mIoU、median IoU、IoU>=.3/.5/.7、positive joint-success=Yes且IoU达阈值；matched相对R180/mismatched/uniform-bbox/uniform-reference。失败rescue定义预冻结baseline IoU<.1且matched达到>=.3/.5/.7；newly-broken定义baseline>=.7且matched<.3。报告rescue与newly-broken全量，不挑案例；sequence bootstrap CI仅描述。完整F1明确NA。

## 完整性门槛 / no-silent-zero
R-002v GATE_PASS；20×8均有独立generation记录或显式失败原因；baseline/identity 20/20 token和response完全一致，否则GATE_STOP；每condition parser仅看当前prefix、无未来信息、无borrowed bbox/GT/rewrite response；每个rewrite命中、finite且shape-only mass/row-sum误差<=5e-5；同一prompt/图像/LoRA/config；所有parse failure按失败计而非替代bbox。

## 竞争假设与预期特征
不预设正向结果。matched若改善baseline且优于R180/mismatched/uniform-bbox，同时没有parse/Yes损失，才提示reference-conditioned spatial routing可能影响自然定位；若各control相近或newly-broken抵消rescue，则维持null/container/OOD解释并停止扩大。

## 验收条件
探索性升级到fresh确认run的必要条件：matched相对baseline mean和median IoU均为正、至少12/20不差；matched配对方向同时优于R180和mismatched且优于或可区分uniform-bbox；parse与Yes各下降不超过1/20；rescue数必须超过newly-broken数。未满足即停止，不事后改heads/window/samples。

## 依赖的 Run / 证据
E007-R-002v必须通过；R-000/R-001已通过；明确豁免原R-003要求R-002正向的前提，仅因用户要求作post-null探索。该豁免本身需本run人工批准和单独执行授权。

## 观测结果摘要
（待补充）

## 局限与混杂因素
n20、positive-only、历史极端分层、attention rewrite可能OOD；无法给出完整Identification F1或Joint F1。任何大样本mIoU/F1确认须另建fresh sequence-disjoint正负run。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
最多支持或反驳在该冻结n20上，future-free query-stage Q→R shape rewrite对自然bbox行为有无探索性因果影响；不形成最终Joint F1结论，不证明identity内容被读取、共享语义电路或可泛化训练收益。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
E007-R-002v artifacts; E007-R-001 frozen manifest/source maps; E007-R-002 summary/records; E003-R-004b archived natural outputs; official vlm_build_messages.py

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
- run_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-003b-post-null-natural-generation-transplant-pilot-n20
- log_file: /home/featurize/work/mechanism/explog/E-007/E007-R-003b-post-null-natural-generation-transplant-pilot-n20/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-003b-post-null-natural-generation-transplant-pilot-n20/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-007/E007-R-003b-post-null-natural-generation-transplant-pilot-n20/metrics.json
- tmux_session: incontext-E-007-E007-R-003b-post-null-natural-generation-transplant-pilot-n20
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T22:02:47
- updated: 2026-08-04T22:07:53

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
