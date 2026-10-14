# 数据层契约（DATA_CONTRACT）— 前端 ↔ 文件 ↔ pi agent

本文件定义 survey-tool 与 research-survey skill / pi agent 之间的数据流通规则。
**目的：pi agent 讨论时只看到规范的研究工件，看不到任何前端/UI 冗余信息。**

## 1. 两类数据，严格分离

| 类别 | 存储位置 | 谁读写 | pi 是否可见 |
|------|---------|--------|------------|
| **规范研究工件**（canonical） | `kernel/`、`shell/`、`state.md`、`INTAKE.md`、`AGENTS.md` | 前端写 + pi 写 | ✅ pi 直接读 |
| **工具/UI 元数据**（tool-state） | `.survey-tool/`（项目根下） | 仅前端读写 | ❌ pi 永不读 |

> 一条铁律：**凡是 pi 需要讨论的内容，必须落在规范文件里；凡是只服务于前端展示/进度的状态，落在 `.survey-tool/`。**
> 前端**绝不**把 UI 语法、勾选状态、组件 ID、样式等信息写进 `kernel/` 或 `shell/`。

## 2. 规范工件落点（前端写入 ↔ pi 读取）

| 前端动作 | 落到的规范文件 | 格式 |
|---------|--------------|------|
| 七问①–⑦ 的**文本** | `shell/03_evidence/papers/<citekey>.md` 的 `## 七问细读` 小节 | markdown，每问一个 `### ① …` |
| 图片标注（框/箭头/文字 + 说明） | 同上笔记的 `## 图片标注` 小节 | `- [[citekey]] Fig.x \| src:images/xx.png \| boxes:[[x,y,w,h],...] \| note: …` |
| 抽取/编辑 claim | `kernel/claims.md` | skill 原生格式：`## Cxx` + `- key: value` |
| 新 idea / 编辑 idea | `shell/00_idea/idea.md` | `## I-xx` + `- key: value`（见下） |
| 研究疑问 | `shell/01_questions/Q-xxx.md` | frontmatter + 可自由编辑 Markdown |
| 对比正文 | `shell/04_comparisons/<comparison-id>.md` | frontmatter + 关联分析 + Obsidian 自由笔记 |
| Finding | `shell/04_comparisons/findings/F-xxx.md` | 独立 Markdown；未核验时不得视为 Claim |
| 对比项目 findings 归档 | → 转写为 idea 进 `shell/00_idea/idea.md` | 同上 |
| Obsidian 导航索引 | `index/*.md` | 自动生成 MOC；不作为第二份研究正文 |
| 同步/搜索日志 | `shell/02_search/search_log.md` | skill 脚本自动追加 |
| 引用元数据 | `kernel/citations.md` | skill 原生格式（ingest.py 写） |
| 状态机 | `state.md` | skill 原生格式 |

## 3. 工具元数据落点（pi 不可见，仅前端用）

`.survey-tool/` 目录结构：
```
.survey-tool/
  papers/<citekey>.json     # triage(deep/skim/counter)、github_repo、github_status、
                           # seven_q 勾选完成度、claim 引用列表
  compares.json             # legacy 结构兼容索引（参与论文/轴/cells/讨论线程）；正文由 Markdown 回读
  obsidian.json             # Vault 名称与路径（仅非敏感编辑器配置）
  ui_state.json             # 最后打开的 tab、排序、筛选等纯 UI 状态
  agent-routing.json        # 人类配置的职责→Agent/模型/Fallback 路由；本机工具策略
```

> 对比的结构化表格仍以 `compares.json` 兼容旧 UI，但对比分析与 Findings 已物化为 canonical Markdown，pi 与 Obsidian 均可见。Markdown 中的 `关联分析` / `Finding` 在刷新时回读；`自由笔记（Obsidian）` 永不由工作台覆盖。

## 4. idea.md 结构化格式（前端与 pi 共识）

```
## I-01
- title: <一句话标题>
- hypothesis: <假设>
- mechanism: <为何会 work>
- falsification: <证伪条件>
- status: draft|active|negated
- novelty: novel|partial|already_done|unknown
- novelty_note: <已查的 query 类 + 最相似 prior>
- support_claims: C01, C05
- contra_claims: C03
- sources: [[focus26]]⑦扩展, [[detpo26]]⑦扩展, 对比:FOCUS vs Teach vs DetPO finding①
- created: <iso>
- updated: <iso>
```

pi 读取 `idea.md` 时按 `## I-xx` 分块解析；前端同构。字段键保持英文（与 skill C1 约定一致：机器读取键为英文）。

## 5. 论文笔记的 tool-managed 小节（安全追加）

前端在 `shell/03_evidence/papers/<citekey>.md` 末尾维护**两个明确标记的小节**，绝不改动 ingest.py 生成的骨架内容：

```
## 七问细读（survey-tool 管理）
### ① 解决了什么问题？
<你的回答>
### ② 默认了哪些前提？
...
### ⑦ 扩展方向 → Idea
...

## 图片标注（survey-tool 管理）
- [[focus26]] Fig.2 | src: images/fig2_pipeline.png | boxes: [[0.30,0.38,0.28,0.34]] | note: 软约束注入点
```

pi 读笔记时这两节就是普通 markdown，可正常引用。标记 `(survey-tool 管理)` 仅说明"这块由前端结构化编辑"，不引入任何 pi 无法解析的语法。

## 6. 与 pi 讨论的流程规则

1. **pi 永不读 `.survey-tool/`。** 若 pi 误读，agent 应据本契约忽略。
2. **前端不向 pi 发送 UI 状态。** 前端只在规范文件里读写；pi 通过读文件获取上下文，与前端解耦。
3. **claim/idea 的晋升仍走 skill 两闸门**：`supported→validated` 需 R2 PASS + 人 approve + 有 hash 来源。前端只改 `status`/`r2_verdict`/`human_verdict` 字段，晋升由 `promote_claim.py` 校验。
4. **反幻觉硬规则不变**：未抓取的论文不进 citations；标注/claim 的 `[[citekey]]` 必须是已 ingest 的；搜索必进 search_log。
5. **前端触发的脚本调用**（sync/scan-github/ingest）走 skill 的 scripts，产物落规范文件，与 agent 手动跑结果一致。

## 7. Obsidian 共编辑边界

1. 推荐直接把项目根目录作为 Vault，不创建导出副本。
2. 可安全自由编辑 Question 正文、Comparison 的 `关联分析` 与 `自由笔记（Obsidian）`、Finding 的 `Finding`/证据/自由笔记。
3. 工作台保存 Comparison 时会更新 frontmatter、参与论文、关联分析和 Findings 链接；自由笔记保留。
4. Experiment Plan 与 Run 的 `自由笔记（Obsidian）` 在工具重新生成文件时保留；其他受管章节仍以工作台结构化数据为准。
5. 新 Run 的 `id` 必须是 canonical/descriptive Run ID，并与 registry 主键、`runs/<id>.md` 文件名和默认真实产物目录末级名称一致。不得用自动 `R-xxx` 再通过 `variant`、`notes` 或 event 建立旁路映射；历史记录通过受校验的 `surveyctl run rekey` 迁移。
6. 每条科学 Run 必须区分并持久化：`necessity`（为何需要）、`evidence_basis`（审计哪项定义/先验）、`data_definition`（数据身份与构造）、`model_config`、`variables_controls`、`metric_definition`、`integrity_gates`、`result_summary`、`limitations`、`conclusion_scope`、`claim_boundary` 和 `audit_paths`。不得只保存命令、路径和一个 metrics JSON。
7. 任何完整性门槛失败、traceback、processor skip、parser ambiguity 或缺失 summary 均不得静默汇总为零性能或 completed；必须登记为 `failed|incomplete|aborted`，并保留失败产物。观测事实、直接解释和机制/论文级推断必须分开。
8. 评测审计必须记录被审计论文/benchmark 的任务定义与原指标覆盖范围；“未报告 joint metric”不得改写成“没有评测任一 component”，本地重建不得冒充官方 split。
9. `index/*.md` 和 `index/objects/*.md` 是生成索引，可随时覆盖，不应在其中保存唯一研究内容。
10. Claims 的审核门禁不变；Obsidian 编辑 Finding、Experiment 或 Question 不能自动验证 Claim。
11. `.survey-tool/*.json` 采用项目级锁与临时文件 `fsync + os.replace` 原子写入；JSON 损坏必须显式报错并保留 `*.corrupt-*` 副本，禁止退化为空 registry。Experiment/Run 更新只接受声明字段，`id`、`experiment_id`、创建时间等身份字段不可通过普通 PUT 修改。
12. AI Run 导入 schema 与 Run registry 对齐；schema 外字段必须拒绝，旧别名仅做明确映射（`changes → implementation_summary`、`expected → expected_outcome`、`acceptance → acceptance_criteria`），不得静默丢字段。Experiment Proposal 的结构化对象在 JSON 中原样保存，Markdown 只是确定性渲染。
13. 新 Run 的主表只有四栏：**研究问题 / 目的 / 方法 / 详细实现细节**（`research_question`、`purpose`、`method_plan`、`implementation_details`）。方法一栏承担干预、对照、指标与判定规则；实现细节一栏承担数据身份与规模、代码结构、环境与命令。历史字段（hypothesis、metric_plan、data_definition、data_scale、variables_controls、metric_definition、integrity_gates、acceptance_criteria、architecture_plan 等）仍可写入，会按语义归入方法/实现细节小节并保留原文，但不再出现在主表单。`submit-review → approve → authorize_execution` 链仍保留，但**不再是必经门禁**：`confirm-design`、`implementation-ready`、`submit-review` 都不再有填表前置条件，且审核中/批准后修改规范只记录 `spec_drift_fields` 与 `spec_edited_after_*` 历史，不再要求先退回。
14. 执行仍需一次人类动作：`review_status=approved` 且存在 `execution_authorized_at`（推荐直接用「交给 Steward」一步完成批准+授权+建 dispatch）。批准后规范变化**不再阻断执行**，只在 Run 记 `spec_drift_fields`、在 Outbox 记 `spec_drift_noted` 事件；唯一保留的硬约束是「attempt 正在 running 时不得改写规范与实现证据」。历史已执行 Run 标为兼容 `legacy`，不被静默迁移。
15. Agent 路由由 `.survey-tool/agent-routing.json` 和“Agent 管理”界面维护。默认本地工具编辑走 Codex/Luna、实验仓库代码编辑走 Codex/Sol；实际有效值以项目配置为准。Agent 只能查询，不能通过 Experiment/Run 更新改写。主模型不可用或额度耗尽时才按配置 fallback，并记录 requested route/model、actual agent/model 与原因。生成的 Mission 可引用当前有效路由，但 `.survey-tool/` 本身仍不是研究事实。
16. Schema 完整不等于文字可审核。Run 的 `variant`、`purpose`、`necessity`、`implementation_summary` 是面向人的摘要层，必须用普通中文说明“比较什么、已有证据缺什么、怎样比较”；精确术语、tensor 位置、head 列表和公式放技术字段。不得使用未解释的术语拼接，不得用“冻结”代替“在看结果前固定 X 且运行中不改”，不得用“在线自然生成/可在线实现”代替“模型逐 token 生成答案时（不是联网服务）”。安全、完整性、可复现和审核字段不得因此删减。

## 8. 一致性

- `.survey-tool/papers/<citekey>.json` 的 `seven_q` 完成度 = 笔记 `## 七问细读` 各小节是否有非空内容（前端以此驱动圆点颜色，不重复存文本）。
- claims 的 `citekey` 字段 = 该 claim 来源论文，前端据此把 claim 挂到论文卡上。

## Experiment 自动提交策略（无评分）

Experiment 可由人类显式保存 `review_automation_policy`：

```json
{
  "enabled": false,
  "auto_review_on_create": false,
  "policy_version": "run-review-automation/v1",
  "notes": ""
}
```

**评分机制已移除。** 自动化只能把已经就绪的 Run 提交给人工审核，它不会批准、不会授权执行，也不能通过“把字段填满”换取任何自动放行。审批与执行授权始终由人类完成。旧存档里的 `auto_approve_threshold` / `auto_authorize_execution` / `auto_authorize_threshold` 与 `policy_version=run-review-score/v1` 仍可读入，但会被归一化为上面的形态并丢弃阈值字段。

`auto_review_on_create` 默认关闭，且仅在 `enabled=true` 时生效。开启后，只有 `created_by` 属于服务端集中定义的 Agent 来源（`terminal_pi`、`agent`、`ai_import`、`ai_proposal`、`codex`、`automation`）才在 Run 完整持久化后触发一次提交；`human`/`manual` 不触发。

提交前只做**结构性**检查（`run_review_blockers`），不做打分：待确认占位符、执行路径或 Workspace 配置不完整、Workspace 安全规则未满足、运行命令含危险操作。命中任一项就保持原状态并记录原因。

自动处理成功后，Run 保存 `automation_review_snapshot` 和 `automation_reviewed_at`（含当时的策略、动作、时间与 `automation_policy` actor）；Experiment event 同步留痕。普通 Run update 不触发自动提交。

创建时被阻断也会保存 `create_time_review_evaluation`，其中 `applied=false`、`needs_human_review=true`，同时保留 `review_status=draft`；这只是留痕，不伪装成已审核。自动化异常同样在 Run/event 留痕并回到 draft，不回滚已经成功创建的 Run。

## Execution Outbox

`.survey-tool/execution-outbox.json` 使用 `survey-tool.execution-outbox/v1` schema 和原子工具状态写入。每个 dispatch 绑定 Experiment、Run、单次 `execution_authorized_at`、approved spec hash 与请求的 `experiment_code_edit` Agent/model。稳定 `dispatch_id` 由 Experiment、Run 和授权时间派生，因此同一次授权幂等；重新授权会 supersede 旧的未完成 dispatch。

状态机为 `queued → delivered → claimed → acknowledged → running → completed|failed`。`delivered` 仅表示协调 Prompt 已送达实时 pi，绝不表示领取或执行；新 live session 可立即重派，同一 session 默认冷却 5 分钟，且始终受 `max_delivery_attempts` 限制。同一次授权会在所有历史状态中复用同一个 dispatch：blocked 在 gate 修复后可原地恢复 queued，failed 只能经带依据的 retry，completed/cancelled/superseded 不复活。claim 返回的 lease token 只在领取响应中出现，list/dashboard/UI 会递归剥离 token/hash。

`running` 是执行授权的唯一消费点：Run 原子记录 `execution_authorization_consumed_at`、`execution_dispatch_id` 和最新 dispatch 状态；claim/ACK 不消费。claimed/acknowledged 租约到期可回 queued，但 running 永不因租约到期自动回队，避免双执行。complete/fail 只回写治理 linkage 与证据，不伪造研究状态或 Claim verdict。

Experiment 的人类专用 `execution_dispatch_policy` 默认如下：

```json
{"enabled":false,"auto_queue_on_authorize":false,"auto_deliver_on_pi_live":false,"claim_lease_minutes":30,"max_delivery_attempts":5,"notes":""}
```

该策略不属于通用 Experiment/Run mutable fields。只有 approved、授权未消费、approved spec 未漂移且 Workspace gate 完整无违规的 Run 才能入队或领取。request_changes 会取消尚未完成 dispatch；Outbox 不执行 shell/SSH、不自动 claim，也不修改 Claim verdict。
## Experiment Steward v2

`activate_run` 只生成 `.pi/experiment-steward.json`，不会启动监控。配置 `version=2`，包含 `identity/remote/experiment/monitoring/scheduling/completion/remediation/archive`；completion、remediation、archive 默认关闭。加载兼容旧 flat activate_run、旧 nested WatchdogConfig 和旧文件名，但首次写入只生成新文件且不删除旧数据。

## Research Explorer

`.survey-tool/research-explorations.json` 是 version 1 public registry，仅保存 exploration 身份、预算、状态、canonical path 与 round/final/proposal hash，不保存正文、Prompt、消息或秘密。正文唯一写入 `shell/07_explorations/<id>/`；`surveyctl exploration inspect-target|init|context|record-round|finalize` 是 terminal Extension 的受控桥接。round payload 上限 256KB，证据状态枚举固定。Idea/Question/Comparison 仅得到探索链接；Experiment 仅得到 `exploration-candidates` draft Runs，不自动审核、授权、入队或执行。

执行授权成功必须为同一 authorization timestamp 建立一个持久 Outbox dispatch，即使旧 `auto_queue_on_authorize` 为 false。唯一授权消费点是持有 lease 的 dispatch 从 acknowledged 进入 running；deprecated `activate_run` 对 reviewed Run 只 enqueue。`outbox reconcile` 幂等补齐未消费授权，已消费但无可追溯 dispatch 的旧数据只报告 `legacy_consumed_untracked/consumed_dispatch_missing`，绝不伪造任务或清除消费时间。

`.survey-tool/governance-tasks.json` v1 只保存 `classify_run` 轻量整理待办，不具备执行或审核授权。`.survey-tool/agent-route-events.jsonl` 使用对象 `{schema,version,events}`，记录路由结果观测，不修改 routing policy。

`run_organization_policy` 默认只启用确定性规则：明确 group、唯一 group、唯一 token 匹配或 Research Explorer 候审组。含糊 Run 保持未分组，并以 Experiment/Run/groups hash 生成稳定 `classify_run` task id。该策略只能由人类专用端点修改。

governance task 的租约状态是 `claimed`，不是 delivered。过期 claim 原子恢复 queued；complete/fail 必须同时匹配 claimed、consumer、未过期 token，终态清除全部租约字段。任务使用独立 `lightweight_governance` requested route，prompt 只包含单 Run 与 group 摘要并限制在 4 KiB。

`.survey-tool/agent-route-events.jsonl` 的新事件带 `subject=requested|actual`；旧事件缺省视为 requested。公开 health 按 subject、route、Agent/model 分组。message/fallback_reason 拒绝 credential、token 和 private-key 样式内容，并限制长度。

项目生命周期状态写入 `.pi/steward-state.json`，迁移事件追加到 `.pi/steward-events.jsonl`。phase 为 `idle|monitoring|incident_open|remediation_pending|restarting|verifying_recovery|completion_candidate|archiving|archived|needs_attention|stopped`。pi 重启不恢复 timer；磁盘事实保留但明确 stopped/pausedAfterRestart。

完成合同是 AND：所有 marker、required artifact/metrics 非空、可靠的 process 检查、没有 open 或尚待恢复验证的 remediation incident、并且 size/mtime 连续 `stableChecks` 次稳定。若 `requireProcessExit=true` 且 `allowNonzeroExit=false`，必须配置 `completion.exitCodeFile`，远程文件必须存在且内容是整数 `0`；插件绝不根据 process 消失伪造 exit code。若允许 nonzero，也仍须可靠确认 process 已退出。修复相关 phase 和 `needs_attention` 均阻断完成/归档。

归档 schema 为 `survey-tool.experiment-steward-archive/v1`，只保存受限 manifest/summary、稳定排序的远程 inventory、错误/修复生命周期摘要，以及最多 64 KiB 的日志和 metrics 摘要及 SHA-256。文件数和总大小均有上限，目录扫描请求 `maxFiles+1` 以可靠标记 `truncated`。配置快照不含 playbook 命令、restart command 或秘密。`manifest_sha256` 是移除该字段后对递归 key 排序稳定序列化的 SHA-256。

归档不是科研解释或 Claim verdict。Run 回写只能调用当前仓库 `surveyctl.py`；若同 Run 有 queued/delivered/claimed/acknowledged/running Outbox dispatch，只写证据字段，不把 operational status 写成 completed，并明确等待持有 lease 的 consumer complete。

## Run 科研生命周期 v2

新 Run 的主流程是：**四栏研究记录 → 实现 → 交给 Steward（一次点击即批准+授权）→ 运行及 Experiment Steward 监控 → 结果分析 → 完成归档**。`research_design`、`code_planning`、`ready_for_review`、`awaiting_review`、`ready_to_run` 仍是可用的阶段标签，但不再要求逐段点按；新对象显式保存 `workflow_version=2`，没有版本的历史 Run 保持 legacy，不做静默迁移。

方法一栏建议写清「干预什么、和什么比、什么算通过」，指标的计算与判定规则可以直接写在里面；Experiment 级 `metric_definitions` 注册表仍可选用，用于跨 Run 复用同一指标的公式与量纲。运行结束只进入 `analysis_pending`；只有保存 `result_analysis`，以及带具体数值和结果文件的 `key_results` 或 `metric_observations` 后，才进入科研意义上的 completed。`limitations` 只需简短记录明显局限，可为空。

`implementation_ref` 使用 `survey-tool.run-implementation/v1`，登记公共 Python 包、稳定 CLI、Run 配置、可读 Shell launcher、复用/新增模块和测试。`codespace/` 建议只保存薄 Shell；Hook、Metric、Adapter 和 Pipeline 属于公共实验包。架构检查以可读警告为主；Workspace 安全、人工授权和 Outbox 防重复执行仍是后台硬约束。
