# Survey Tool 2.0 领域模型与数据权限草案

> 状态：Phase 0 / 初始合同
> 日期：2026-08-15
> 相关决策：ADR-0001、ADR-0002

## 1. 通用对象信封

所有 2.0 核心对象共享稳定 identity：

```json
{
  "schema": "survey-tool.object/v2",
  "id": "P-01J...",
  "type": "paper",
  "project_id": "PROJECT-...",
  "title": "人类可读标题",
  "lifecycle_status": "active",
  "canonical_path": "shell/.../object.md",
  "revision": 1,
  "created_at": "ISO-8601",
  "created_by": {"kind":"human|agent|import|automation", "id":"..."},
  "updated_at": "ISO-8601",
  "updated_by": {"kind":"human|agent|import|automation", "id":"..."}
}
```

### 1.1 ID

- ID 一经建立不可修改；
- 展示短 ID 与内部全局唯一 ID 可以分离；
- 对既有 `citekey`、`Q-xxx`、`E-xxx` 和 descriptive Run ID，保留其领域 identity；
- 新增关系引用内部 object ID，同时保存适合 Markdown 的稳定 reference；
- 文件名不是唯一身份，移动文件不能创造新对象。

### 1.2 Revision

- SQLite 状态更新必须递增 revision；
- API 写请求可提交 `expected_revision`；
- revision 冲突返回 409，不做 last-write-wins；
- Markdown 正文使用内容 hash / mtime 检测外部修改，并在覆盖前生成冲突。

## 2. Authority Map

| 数据 | Authority | 说明 |
|---|---|---|
| 研究正文、证据解释、引用 | Markdown | 人、pi、Obsidian 可读 |
| 对象 ID、type、lifecycle | SQLite v2 | 事务和关系查询 |
| 对象关系 | SQLite v2 | Markdown 可渲染链接摘要 |
| Job、lease、progress | SQLite v2 | 不写入研究正文 |
| Agent 草稿正文 | Markdown draft 或独立 artifact | 未确认不得覆盖正式正文 |
| Experiment / Run 旧治理状态 | 现有 JSON | 垂直迁移前保持 authority |
| Claim 证据门禁 | 现有 kernel + skill gate | 2.0 不降低规则 |
| UI 筛选和布局 | browser / tool state | 不属于研究事实 |

## 3. 对象类型

## 3.1 Paper

```text
identity: citekey + object_id
acquisition: zotero | local_pdf | doi | arxiv | web
file_status: missing | available | download_failed
parse_status: not_requested | queued | running | parsed | failed
trust_status: normal | needs_verification | low_trust | quarantined
visibility: visible | hidden | archived | trashed
```

约束：

- `parsed` 必须有解析 artifact；
- 正式证据引用必须指向已摄取来源；
- trust 状态变化产生事件并记录理由；
- trashed 是可恢复软删除。

## 3.2 Paper Candidate

```text
status: proposed | accepted | dismissed | hidden | expired
verification: unverified | metadata_verified | source_accessible
acquisition_job_id: optional
```

Candidate 不是 Paper。accepted 后创建或关联 Paper；转换必须保留检索 query、来源和 Agent 推荐理由。

## 3.3 Seven-Q Note

Seven-Q 仍是 Paper canonical note 的受管章节，不必复制完整正文到 SQLite。v2 登记：

- paper relation；
- canonical path；
- 七问各节 completion index；
- draft revision；
- confirmed revision；
- Finding links。

## 3.4 Comparison

```text
status: draft | active | archived
participants: Paper relations
axes: ordered comparison questions
canonical_path: shell/04_comparisons/<id>.md
```

矩阵 cell 可以结构化索引，但正式分析正文和引用在 Markdown 中。

## 3.5 Finding

```text
verification_status: draft | supported | contradicted | superseded
source_relations: seven_q | comparison | question | run
claim_id: optional
```

Finding 不等于 validated Claim。晋升时创建明确 event 和 Claim relation。

## 3.6 Claim

继续使用 research-survey 的状态与双门禁：

```text
draft | supported | validated | contradicted | partial | inference_only
```

2.0 SQLite 只索引 identity、状态摘要和关系，不绕过 `kernel/claims.md`、R2、人工批准及 source hash。

## 3.7 Question

```text
status: open | investigating | answered | blocked | archived
canonical_path: shell/01_questions/<id>.md
relations: Paper / Seven-Q / Comparison / Finding / Experiment / Run / Automation
```

answered 表示用户认可当前回答，不自动表示对应 Claim 已 validated。

## 3.8 Workspace / Server

```text
status: unknown | online | degraded | offline
policy_version: integer
policy_path: canonical Chinese policy document
structured_policy: governed runtime state
```

敏感认证信息只允许保存在系统认证环境，不进入 SQLite、Markdown、event 或前端 payload。

## 3.9 Experiment

```text
status: draft | active | paused | completed | archived
workspace_relation: exactly one active Workspace binding
canonical_overview_path: shell/06_experiments/<id>/README.md
```

现有 Experiment governance registry 在迁移前仍是执行状态 authority。

## 3.10 Run

主要阶段：

```text
design
→ implementation
→ review
→ authorized
→ queued
→ running
→ analysis_pending
→ completed
```

操作状态与科研状态分离。`program exited`、`dispatch completed`、`scientific completed` 不得合并为一个布尔值。

现有 Run lifecycle v2、review gate、execution authorization 和 Outbox 是 2.0 必须兼容的最低合同。

## 3.11 Automation

```text
type: research | experiment | hybrid
status: draft | awaiting_approval | active | paused | checkpoint | completed | completed_with_warnings | failed | cancelled
phase: intake | research | research_review | experiment_planning | experiment_execution | synthesis
```

预算：

- deadline；
- max rounds；
- max papers；
- max runs；
- compute / concurrency limit；
- retry limit。

Automation 只能通过正式关系创建 Candidate、Finding、Question、Experiment 或 Run，不能直接写 validated Claim。

## 3.12 Agent Session

```text
provider: pi | herdr | codex | other
status: requested | live | paused | stale | completed | failed
object_relation: required
task_type: discussion | research | implementation | monitoring | analysis
```

只保存 session identity、位置、Agent/model 和健康状态；不复制消息、secret 或完整 Prompt。

## 3.13 Job

```text
kind: download | mineru | import | export | migration | agent_task | automation_step
status: queued | running | succeeded | failed | cancelled
progress: 0..1 or null
idempotency_key: required where retry may duplicate side effects
```

Job 必须有：

- request summary；
- actor；
- target object；
- attempt；
- timeout；
- error class / safe error message；
- result artifact relation；
- created / started / finished timestamps。

## 3.14 Inbox Item

Inbox 不是业务对象的第二份状态，只是待处理投影：

```text
kind: candidate_review | draft_review | run_review | execution_attention | automation_checkpoint | migration_conflict
status: open | snoozed | resolved | dismissed
target_object_id: required
```

业务状态变化后，Inbox item 由规则创建或关闭。

## 4. 关系合同

关系是有类型的有向边：

```json
{
  "from_object_id": "...",
  "relation_type": "supports|contradicts|derived_from|discusses|compares|tests|produced_by|belongs_to|uses_workspace",
  "to_object_id": "...",
  "metadata": {},
  "created_at": "...",
  "created_by": {"kind":"...", "id":"..."}
}
```

初始 relation types：

- `belongs_to`
- `derived_from`
- `discusses`
- `compares`
- `supports`
- `contradicts`
- `tests`
- `produced_by`
- `uses_workspace`
- `implemented_by`
- `monitored_by`
- `supersedes`

关系类型采用 allowlist；不接受任意字符串。关系 metadata 必须有大小和字段限制。

## 5. Agent 草稿与人工确认

所有七问、Comparison、Question 和正式结果解释采用统一流程：

```text
Agent generates Draft Artifact
→ server validates references and target revision
→ UI shows diff / citations / warnings
→ human accepts selected blocks or rejects
→ canonical Markdown write
→ event records actor and source session
```

约束：

- Agent 不直接覆盖用户在其运行期间修改的新 revision；
- 接受部分 block 时保留 provenance；
- 被拒草稿可归档但不进入 canonical 正文；
- 预授权也必须限定对象、章节、截止时间和最大修改次数。

## 6. 事件合同

每个重要变化写入 append-only event：

```json
{
  "event_id": "EV-...",
  "project_id": "...",
  "object_id": "...",
  "kind": "paper.candidate.accepted",
  "actor": {"kind":"human|agent|system|automation", "id":"..."},
  "occurred_at": "ISO-8601",
  "from_revision": 1,
  "to_revision": 2,
  "summary": "安全、简短、可展示的说明",
  "details": {}
}
```

事件禁止包含：

- token、密码、private key；
- 未裁剪的完整 Prompt；
- PDF 正文或大型日志；
- lease token；
- 不必要的绝对敏感路径。

## 7. 跨存储写入恢复

当一个操作同时更新 SQLite 和 Markdown 时：

1. 在 SQLite 创建 operation，状态 `prepared`；
2. 以临时文件写 Markdown，`fsync + os.replace`；
3. 计算并记录 content hash；
4. SQLite transaction 更新对象 revision、event 和 operation=`committed`；
5. 若进程中断，启动恢复器根据临时文件 / hash / operation 状态重试或标记人工处理；
6. 不静默回滚为“空内容”。

第一阶段不需要通用分布式事务，只需覆盖工具管理的 Markdown 小节和新 v2 文档。

## 8. Migration 合同

每次 migration 支持：

- `inventory`：只盘点；
- `dry-run`：生成拟变更与冲突；
- `apply`：在确认备份后执行；
- `verify`：计数、路径、hash 和抽样验证；
- `rollback`：恢复 migration 前快照或逆向记录。

不确定映射写入 `migration_records` 并创建 Inbox conflict，不猜测对象关系。

## 9. 下一步实现边界

Phase 1 首个垂直切片只实现：

1. SQLite schema migration runner；
2. `objects`、`relations`、`events`、`jobs`、`inbox` 基础 repository；
3. `/api/v2/health` 和项目 capability；
4. `/v2` React 应用壳；
5. 一个只读 Inbox / object index 示例；
6. 不迁移现有 Experiment / Run authority；
7. 不启动 Automation 执行。
