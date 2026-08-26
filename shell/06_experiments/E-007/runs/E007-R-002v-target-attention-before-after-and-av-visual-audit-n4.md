# E007-R-002v-target-attention-before-after-and-av-visual-audit-n4 · target-attention-before-after-and-av-visual-audit-n4

- canonical_run_id: `E007-R-002v-target-attention-before-after-and-av-visual-audit-n4`
- run_type: implementation_visualization_gate
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-04T22:02:47
- approved_at: 2026-08-04T22:03:07
- execution_authorized_at: 2026-08-04T22:03:09
- execution_authorization_consumed_at: 2026-08-04T22:07:53
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
draft

## 本轮目的
直观验证植入确实改变真实decoder target heads的Q→R空间分布及A@V输出，并验证用于后续自然生成的逐token、无未来信息窗口。

## 必要性 / 证据链位置
R-000已用logit变化证明干预进入计算，但未持久化A_before/A_after热图、A@V差异或卸载恢复；R-001仅用归档响应静态审计窗口，未运行真实逐tokenparser。必须先补齐这些工程证据，避免把自然行为变化误归因于错误hook或未来token泄漏。

## 研究依据 / 被审计对象
审计E007-R-000的softmax后/dropout前/A@V前rewrite与E007-R-001的窗口设计；固定source heads L15H13,L16H23,L18H15，target heads L18H15,L19H03,L22H00,L20H08。

## 实现方式（简版）
从R-001冻结集预先固定2个历史定位失败和2个历史正确样本。对每个样本保存原始target attention、matched植入、R180、mismatched和uniform-bbox的真实before/after热图，同时记录A@V变化。另以baseline/identity做真实逐tokengreedy生成，验证parser从首个生成prediction row启用、在第一个合法bbox闭括号后关闭且不读取未来token。

## 实现方式（详细版）
在Qwen3-VL decoder eager_attention_forward内softmax后、dropout前、A@V前截获；vision attention原样走upstream。对每个target head及干预row保存reference-span A_before、A_after、full-row sum、Q→R mass、L1/JS、COM/peak和对应head A@V before/after norm；shape-only使用A_R_prime=alpha*S，alpha取当前row/head自身Q→R mass，非R不变，V保持target自己的V。可视化reference图+GT bbox、source G→R、target Q→R before/after/difference及controls，使用共享绝对色标并另报raw数值，禁止各panel独立归一化制造差异。自然窗口必须在自写逐token循环中仅依据当前已生成prefix更新parser，不得调用完整future response；identity写回每row/head自己的原shape。卸载hook后再forward并核验数值恢复。

## 数据身份与构造
继承E007-R-001冻结20个sequence-unique positives；在看本run结果前按固定ascending index从localization-error取2、localization-correct取2，合计4个sequence-unique样本。复用原图、官方IPLoc-ID消息构造和预先缓存的prompt-stage source maps。

## 数据规模
n=4；每样本完整可视化target main4 × baseline/matched/R180/mismatched/uniform-bbox，并运行baseline与identity自然逐token生成。该run只作实现和可视化gate。

## 模型、权重与关键配置
Qwen3-VL-8B-Instruct + 原IPLoc-ID LoRA；bf16 eager attention；max_side=640；max_memory={0:"22GiB",cpu:"120GiB"}；原prompt；greedy/do_sample=False；沿用归档自然生成的原max_new_tokens和停止设置，若无法核实则GATE_STOP，不猜测。seed=20260804。

## 变量、干预与对照
baseline无hook；identity写回自身shape；matched source aggregate；R180；预冻结cyclic mismatched-sequence donor（不同sequence，按真实矩形grid双线性resize）；uniform reference-bbox fractional occupancy。所有shape-only条件保持各target row/head自身alpha，非reference attention不变，保留target V。

## 指标与计数规则
逐head/row：Q→R mass before/after、full row sum before/after、A空间L1/JS、COM/peak、A@V向量L2/cosine、selected logits变化；生成：baseline-identity token/response完全一致、窗口起止token和每步state、parse/Yes/bbox。必交每样本统一色标多panel图、raw npz和机器可读审计表。

## 完整性门槛 / no-silent-zero
4/4双图span与reference bbox token subsequence连续唯一匹配；所有指定rewrite实际命中且n_rewrites>0；identity attention/logits/自然tokens复现；matched A_after与注册source shape在bf16容差内一致；shape-only mass error<=5e-5、row-sum preservation<=5e-5、finite；非平凡条件A@V或logits确有变化；hook卸载后logits恢复<=5e-4；stream parser不读取未来token并在4/4 parseable bbox覆盖精确p-1 rows。任一失败GATE_STOP，不升级自然pilot。

## 竞争假设与预期特征
若实现正确，before/after图应清楚显示reference内部shape被替换、总Q→R预算不变且A@V变化；identity和卸载恢复应与baseline一致。该结果仅证明干预与在线执行正确，不预设matched改善行为。

## 验收条件
全部完整性gate通过并交付4样本全条件热图、raw A/A@V审计和逐token窗口trace；否则修复必须使用新attempt并保留失败记录。

## 依赖的 Run / 证据
E007-R-000、R-001已工程通过；使用R-001冻结manifest/source maps。与R-002科学方向为null/mixed相容，不把可视化当性能证据。

## 观测结果摘要
（待补充）

## 局限与混杂因素
n4；主要是工程可视化；attention heatmap仍不能单独证明语义或identity；共享色标可能使低mass图视觉较暗但raw值保留。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
最多支持attention probability rewrite进入真实A@V、按预期改变空间shape且future-free逐token窗口可执行；不支持自然IoU/F1改善、identity理解或唯一因果电路。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/_legacy/codespace/e007/runner_000_002.py; shell/06_experiments/E-007/plan.md; E007-R-000/R-001/R-002远端artifacts与attempts

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
- run_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-002v-target-attention-before-after-and-av-visual-audit-n4
- log_file: /home/featurize/work/mechanism/explog/E-007/E007-R-002v-target-attention-before-after-and-av-visual-audit-n4/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-002v-target-attention-before-after-and-av-visual-audit-n4/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-007/E007-R-002v-target-attention-before-after-and-av-visual-audit-n4/metrics.json
- tmux_session: incontext-E-007-E007-R-002v-target-attention-before-after-and-av-visual-audit-n4
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T22:02:47
- updated: 2026-08-04T22:07:53

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
