# Survey Tool Phase 6 只读审计

审计范围：当前 `rebuild/survey-tool-2.0` 工作树中的 `server.py::route_post`、`route_put`、`surveyctl.py`、v2 API 与 `web/src/api.ts`。本报告只描述现状；未修改仓库文件。工作树审计开始时已有用户改动 `start.sh`，本审计未触碰。

## 结论摘要

Phase 6 目前**不具备安全全量切换条件**。v2 的 native 写能力集中在 Paper Candidate/采集 Job、Automation、Herdr Launch Request/Execution、Agent Session 索引与有限软归档；Question、Comparison、Finding、Claim、Idea、paper note/七问、Experiment/Run 仍没有等价的 v2 canonical 写 API。当前 Phase 5 配置也只识别 `questions`、`compares` 两组：仅把更多字符串加入 `freeze_legacy_writes` 并不会冻结其它入口。

## 1. 当前 1.x POST/PUT 入口清单

“v2 对应”分为：

- **native**：v2 有实际创建/变更能力；
- **索引-only**：v2 只索引 legacy identity/relation，不拥有正文或治理写入；
- **无**：没有等价 v2 API/UI；
- **不适用**：操作不是研究对象持久化写入，或是运维/外部进程控制。

### 1.1 项目内容与研究对象

| 方法与端点 | 写入对象/副作用 | 实际持久化位置 | v2 对应 |
|---|---|---|---|
| POST `/api/p/<p>/sync` | Zotero collection 导入 | `papers/*.pdf`、通常也更新 `papers/INDEX.md`（外部同步脚本） | 部分 native：Paper Candidate acquisition/ingest，但没有 collection sync 等价 UI/API |
| POST `/api/p/<p>/zotero/sync` | Zotero collection 或 item PDF 导入 | `papers/*.pdf`；collection 脚本可更新 `papers/INDEX.md` | 部分 native，语义不等价 |
| POST `/api/p/<p>/papers/web-import` | 下载开放 PDF 并 canonical ingest | `papers/*.pdf`、ingest 脚本写 `kernel/citations.md` 及相关 canonical 产物 | native staged candidate + acquisition + confirmed ingest；最接近可迁移项 |
| POST `/api/p/<p>/mineru/parse` | 启动 MinerU 解析进程 | `papers/<stem>/hybrid_auto/**`；进程状态仅内存 | native acquisition Job 覆盖受控 pipeline，但没有任意既有 PDF 的同语义入口 |
| POST `/api/p/<p>/scan-github` | 扫描论文/笔记中的仓库链接 | 无持久化，仅返回计算结果 | 不适用（读/计算型 POST） |
| POST `/api/p/<p>/intake` | 保存 intake；可选 materialize 项目 | `INTAKE.md`；materialize 脚本还会生成/更新 `state.md`、kernel/shell 项目骨架 | 无 |
| POST `/api/p/<p>/claims` | 新建 Claim | `kernel/claims.md` | 索引-only：content migration 可索引 Claim identity，不能写 canonical Claim/门禁 |
| POST `/api/p/<p>/ideas` | 新建 Idea | `shell/00_idea/idea.md` | 无 |
| POST `/api/p/<p>/compares` | 新建 Comparison，并生成 comparison/finding Markdown 和索引页 | `.survey-tool/compares.json`、`shell/04_comparisons/<id>.md`、`shell/04_comparisons/findings/*.md`、`index/**` | 索引-only；无 native create/edit API，当前 v2 UI 仍从 legacy GET 读取 |
| POST `/api/p/<p>/questions` | 新建 Question 并刷新索引 | `shell/01_questions/Q-*.md`、`index/**` | 索引-only；无 native create/edit API，当前 v2 UI 仍从 legacy GET 读取 |
| POST `/api/p/<p>/explorations/request` | 生成一条人工复制的探索命令/Prompt | 无持久化，明确 `started:false` | 无需冻结；不是写入口 |
| POST `/api/p/<p>/obsidian/index` | 重建 Obsidian 派生索引 | `index/*.md`、`index/objects/*.md`、实验 alias 页面；还可能规范化部分 legacy JSON ID | 无 |
| POST `/api/p/<p>/obsidian` | 保存 vault 配置并重建索引 | `.survey-tool/obsidian.json`、上述 `index/**` | 无 |
| PUT `/api/p/<p>/paper/<citekey>` | 编辑七问、图片标注、paper UI state | canonical paper note（`shell/03_evidence/papers/<citekey>.md`）；`.survey-tool/papers/<citekey>.json` | 无；v2 Paper 只是 reference identity/Paper Candidate，不支持 note、七问或 annotation 写入 |
| PUT `/api/p/<p>/claim/<Cnn>` | 更新 Claim 字段/审核状态 | `kernel/claims.md` | 索引-only；无 native Claim mutation/双门禁 API |
| PUT `/api/p/<p>/idea/<I-nn>` | 更新 Idea | `shell/00_idea/idea.md` | 无 |
| PUT `/api/p/<p>/compares` | 全量保存 Comparison/Finding 结构 | 与 POST compares 相同 | 索引-only；无 native mutation |
| PUT `/api/p/<p>/question/<Q-nnn>` | 更新 Question 正文、关系与状态 | `shell/01_questions/Q-*.md`、`index/**` | 索引-only；无 native mutation |

### 1.2 Experiment / Run / execution governance

| 方法与端点 | 写入对象 | 实际持久化位置 | v2 对应 |
|---|---|---|---|
| POST `/experiments` | 创建 Experiment | `.survey-tool/experiments.json`；`shell/06_experiments/<E>/{<E>,brief,plan,review,mission,events}.md` | 索引-only；Automation 不是等价 Experiment 治理 |
| POST `/experiments/<E>/runs` | 创建 Run | `.survey-tool/runs.json`；Experiment 下 Run spec/result Markdown；事件文件 | 无等价 native Run |
| POST `/experiments/<E>/run-grouping` | 人工 Run 分组 | `experiments.json`、`runs.json`、Experiment plan/mission、Run specs | 无 |
| POST `/experiments/<E>/agent-run-grouping` | Agent proposal 的受控分组 | 同上，另可能写 governance task/snapshot | 无 |
| POST `/experiments/<E>/review-automation-policy` | Run 审核自动化策略 | `experiments.json`、Experiment plan/mission | 无；v2 Automation 生命周期不等价 |
| POST `/experiments/<E>/execution-dispatch-policy` | 执行派发策略 | `experiments.json`、Experiment plan/mission | 无 |
| POST `/experiments/<E>/run-organization-policy` | Run 组织策略 | `experiments.json`、Experiment plan | 无 |
| POST `/execution-outbox/reconcile` | 修复/记录 dispatch 一致性 | `.survey-tool/execution-outbox.json`、`.survey-tool/execution-reconciliation-events.jsonl`，并可能更新 Run | 无；v2 Herdr Execution 不等价旧 Run Outbox |
| POST `/agent/route-event` | Agent 路由审计事件 | `.survey-tool/agent-route-events.jsonl` | 无 |
| POST `/governance-tasks/claim-next` | 原子领取治理任务 | `.survey-tool/governance-tasks.json`（lease hash/owner/deadline） | 无 |
| POST `/governance-tasks/<id>/complete` | 完成治理任务并应用结果 | `governance-tasks.json`，并可能更新 `runs.json`/Run spec | 无 |
| POST `/governance-tasks/<id>/fail` | 标记治理任务失败 | `governance-tasks.json` | 无 |
| POST `/runs/<R>/execution-outbox/enqueue` | 将已授权 Run 入队 | `execution-outbox.json`；Run registry/spec 的 dispatch 状态 | 无 |
| POST `/execution-outbox/claim-next` | 原子领取 dispatch | `execution-outbox.json` | 无 |
| POST `/execution-outbox/<D>/ack` | 确认实际路由 | `execution-outbox.json`，可能同步 `runs.json`/Run spec | 无 |
| POST `/execution-outbox/<D>/running` | 真正开始并消费 Run 授权 | 同上 | 无 |
| POST `/execution-outbox/<D>/complete` | 以证据完成 dispatch/Run | 同上 | 无 |
| POST `/execution-outbox/<D>/fail` | 分类失败 | 同上 | 无 |
| POST `/execution-outbox/<D>/retry` | 有依据重试 | `execution-outbox.json` | 无 |
| POST `/execution-outbox/<D>/release` | 开始前释放 lease | `execution-outbox.json` | 无 |
| POST `/pi/dispatch-pending` | 向 live pi 投递 pending dispatch | `execution-outbox.json` delivery 状态；外部 pi session transcript | 无 |
| POST `/experiments/<E>/auto-review` | 按策略审核 eligible Runs | `runs.json`、Run spec、`experiment-events.jsonl`、`events.md` | 无 |
| POST `/runs/<R>/auto-review` | 自动审核单 Run | 同上 | 无 |
| POST `/agent-routing` | 保存 agent/model routing | `.survey-tool/agent-routing.json`；重写 Experiment mission Markdown | 无 |
| POST `/(machines|servers)` | 新增/更新服务器配置 | `.survey-tool/servers.json` | 无 |
| POST `/workspaces` | 新增/更新 Workspace 与环境策略 | `.survey-tool/workspaces.json` | v2 只有 workspace object type 基础结构，无等价写 API/UI |
| POST `/runs/<R>/workflow` | 推进 Run 设计/实现/分析/终态 | `runs.json`、Run spec/result、events；部分阶段更新 Experiment | 无 |
| POST `/runs/<R>/review` | submit/changes/approve/authorize | `runs.json`、Run spec/review、events；可 enqueue outbox | 无，且是不可绕过治理 |
| POST `/runs/<R>/activate` | deprecated compatibility activation/enqueue | `active-run.json`、`.pi/experiment-steward.json`，或 outbox/Run 状态 | 无 |
| PUT `/experiment/<E-nnn>` | 更新 Experiment 字段 | `experiments.json` 及 Experiment canonical Markdown | 索引-only；无 native mutation |
| PUT `/run/<id>` | 更新 Run 字段 | `runs.json` 及 Run canonical Markdown | 无 |

### 1.3 工具、发布与会话控制

| 方法与端点 | 写入/副作用 | 位置 | v2 对应 |
|---|---|---|---|
| POST `/gpt/assistant` | 生成给 GPT 的指令 | 无持久化 | 不适用（计算型 POST） |
| POST `/gpt/parse` | 解析 GPT 返回文本 | 无持久化 | 不适用 |
| POST `/branches` | 记录 deep-dive/session branch | `.survey-tool/branches.json` | 无 |
| POST `/export` | 构建/同步发布仓库 | `.publish/**` 或请求的 destination、`.survey-tool/publish.json`；可 git init/commit/push | 无 |
| POST `/clone` | clone 代码仓库 | `codespace/<repo>/**` | 无 |
| POST `/pi/restore` | 恢复 live pi bridge | `.survey-tool/pi-binding.json`；启动外部 pi 进程/session | v2 只有 bind-current-pi 的隐私安全索引，不等价控制 |
| POST `/pi/bind` | 绑定/启动 pi session | `pi-binding.json`，外部 pi session | 不等价 |
| POST `/pi/prompt` | 向 live pi 发送 Prompt | 外部 pi session transcript；可能触发后续项目写回 | 无；v2 agent session 仅索引 |
| POST `/pi/steer` | steer live pi | 外部 session | 无 |
| POST `/pi/abort` | 中止当前 pi turn | 进程控制 | 无 |
| POST `/pi/switch` | 切换 session | `pi-binding.json`、外部 session | 无 |
| POST `/pi/new` | 新 session | `pi-binding.json`、外部 session | 无 |
| POST `/pi/clone` | clone session | `pi-binding.json`、外部 session | 无 |
| POST `/pi/set_name` | 改 session 名并持久 binding | `pi-binding.json`、外部 session | 无 |
| POST `/pi/set_model` | 改 live model | 外部进程/session | 无 |
| POST `/pi/messages` | 读取 live messages | 无项目写入 | 不适用（读型 POST） |
| POST `/pi/last_text` | 读取最后回复 | 无项目写入 | 不适用 |
| POST `/pi/models` | 读取模型列表 | 无项目写入 | 不适用 |

此外，`POST /api/projects/init|register|unregister` 写 server `config.json`，init 还创建整个项目骨架。这些是全局 operator/project-registry API，不属于 ADR-0004 定义的 `/api/p/<proj>/...` 研究对象写入口，不应被 project-level Phase 6 freeze 混入。

## 2. 当前仍为 1.x-only 的对象类型

1. **Paper note / Seven-Q / annotations / per-paper UI state**：只有 `PUT /paper/<ck>`。v2 candidate ingest 能纳入论文，但不能编辑已纳入论文的 canonical note、七问或图片标注。
2. **Claim**：v2 Content Index 只存 identity/relation；`POST /claims`、`PUT /claim/<C>` 仍直接维护 `kernel/claims.md`。缺少 R2 verdict、human verdict、content hash、revision 与批准门禁的 v2 等价写模型。
3. **Idea**：只有 `POST /ideas`、`PUT /idea/<I>`；v2 store/UI 没有 native Idea 写路径。
4. **Question**：虽有 identity 双写与 v2 核对显示，但 canonical 创建/编辑仍只有 POST/PUT 1.x；所以当前冻结 `questions` 实际会使 v2 Question UI 变成只读。
5. **Comparison / Finding**：同样只有索引双写，native v2 create/update 缺失；当前冻结 `compares` 会使 Analysis UI 无法保存结构和 Findings。
6. **Experiment / Run**：legacy JSON + canonical Markdown + review/outbox 是唯一 authority。v2 Automation、Herdr Execution 均不等价，也没有 Experiment/Run native mutation API。
7. **Workspace / Server / routing / governance task / execution outbox**：都是 Experiment/Run 执行治理依赖的 1.x-only tool-state。
8. **Intake / Obsidian index/config / branches / publish / codespace clone**：均无 v2 写替代。
9. **GPT/assistant、GPT/parse、explorations/request、scan-github、pi messages/last_text/models**：它们是 POST 形态的生成或读取，不应被误判为对象写入；冻结它们不会提升数据 authority 安全，反而会损失工具能力。
10. **Live pi 控制**：v2 Agent Session 只做隐私安全 binding/index，不提供 prompt/steer/session lifecycle 控制；不能视为等价迁移。

## 3. “全量开启 freeze”会中断什么

先说明现实限制：当前 `_legacy_write_frozen()` 只被四个分支调用，key 只有 `questions`、`compares`。因此把配置写成所有可能名称，**现实中仍只会冻结这四个端点**：

- POST `/questions`、PUT `/question/<Q>`：不能创建或编辑 Question；GET `/questions` 仍可读。
- POST/PUT `/compares`：不能创建或保存 Comparison/Finding；GET `/compares` 仍可读。

若 Phase 6 将同一门控真正扩展到所有“有写副作用”的 1.x POST/PUT，则以下能力会完全失去 Web 写入口：

- 论文：Zotero sync、Web import、MinerU、paper note/七问/annotation/state。
- 研究知识：Intake/materialize、Claim、Idea、Question、Comparison、Finding、Obsidian config/index。
- 实验：Experiment/Run 创建更新、分组、policy、workflow、review、authorization、auto-review。
- 执行：Outbox enqueue/claim/ack/running/complete/fail/retry/release/reconcile、governance tasks、route events、dispatch-to-pi。
- 运行环境：Workspace/Server/routing 配置。
- 工具：branches、publish/export、clone、live pi restore/bind/prompt/steer/session changes。

其中绝大多数没有 v2 替代；“全量冻结”会把应用从“v2 工作区”降级成大面积只读，而不是完成写入切换。若同时冻结 `surveyctl.py` 的直接写回，Experiment/Run、Outbox、治理任务及 Research Explorer 的 Agent/CLI 工作流也会停止。

## 4. Phase 6 安全前置条件

### 必须先补齐

1. **Question native write API/UI**：create/update、expected revision、canonical Markdown authority adapter、关系校验、双写/回读一致性、冲突与回滚。仅 identity index 不够。
2. **Comparison + Finding native write API/UI**：不能继续以全量 `compares.json` 覆盖作为唯一操作；需对象级 revision、canonical Markdown 更新、关系与 Finding identity 原子性。
3. **Paper note/Seven-Q/annotation API/UI**：与 canonical note 分区合并、避免 state-only 更新抹除正文、revision/content-hash 冲突检测。
4. **Claim 治理 API/UI**：必须保持 `kernel/claims.md` authority 或设计经过验证的新 authority adapter，并原样保留 R2 + human approval + content hash 门禁；不得用通用 v2 object update 替代。
5. **Idea native write API/UI**。
6. **Experiment/Run 完整治理域**：Experiment、Run、review transitions、execution authorization consumption、Outbox lease/reconciliation、governance tasks、Workspace/Server/policy、events/canonical specs 的等价模型和端到端测试。
7. **非对象工具的迁移决策**：Intake、Obsidian、publish、clone、Zotero/MinerU、pi bridge 应明确归为 operator/tool APIs，而不是机械改名成 `/api/v2`。它们需要各自权限和副作用策略。
8. **可观测与回退**：每个 key 独立开关、409 计数、写入一致性告警、回退 runbook、冻结前 dry-run、旧/新结果 diff、至少一个发布周期的 shadow/dual-write 验证。
9. **客户端 readiness**：v2 UI 当前 `loadWorkspace()` 仍从 1.x GET 读 Paper/Question/Comparison/Experiment；必须先切 native reads/writes，并对未初始化 store 和 legacy project 提供明确只读模式。

### 建议暂时保留 1.x 的范围

- **Experiment/Run + surveyctl.py + Outbox/Claim/authority gates**：直到等价状态机、review、execution authorization、lease/reconciliation 和 canonical artifacts 全部迁移且回放测试通过。
- **Claim**：直到双重审核/content hash 门禁有等价实现。
- **paper note/Seven-Q/annotations**：直到 canonical merge 与并发冲突测试完成。
- **operator/tool endpoints**（project init/register、Zotero/MinerU、Obsidian、publish、clone、pi control）：可保留独立 legacy/tool namespace；它们未必应成为 v2 object writes。

## 5. 建议的 Phase 6 分步方案

### Step 0：修正 freeze 模型，不做“一个全局全开”

- 建立端点级 key，而非模糊对象 key：如 `question.create`、`question.update`、`comparison.create`、`comparison.replace`、`paper.note.update`。
- 每个写 API 返回统一 409 payload，但配置保持默认关闭；记录匿名计数，不记录正文。
- 明确排除计算/读型 POST：`gpt/assistant`、`gpt/parse`、`scan-github`、`explorations/request`、`pi/messages|last_text|models`。

### Step 1：先完成低风险 canonical adapter，再冻结 Question

1. 新增 v2 Question create/update API 与 UI，内部仍通过单一 canonical Markdown adapter 写 `shell/01_questions/Q-*.md`，随后刷新 v2 index。
2. 加 expected revision/content hash、冲突 409、幂等和回读测试。
3. shadow 运行并核对至少一个周期。
4. 先冻结 POST `/questions`，观察；再冻结 PUT `/question/<Q>`。GET `/questions` 一直保留。

### Step 2：Comparison/Finding 对象化

1. 新增对象级 Comparison create/update 和 Finding create/update，避免全量数组覆盖。
2. 事务性维护 `.survey-tool/compares.json` + canonical Markdown + v2 index；失败不得留下半写状态。
3. v2 Analysis UI 切换后，依次冻结 POST、PUT `/compares`；保留 GET。

### Step 3：Paper 与采集路径

1. 将 Web import/Zotero 导入 UI 引导到 Candidate → staged acquisition → confirmed ingest。
2. 为既有 paper note/Seven-Q/annotation 补 native update，再冻结 PUT `/paper/<ck>`。
3. 任意 MinerU 与 operator Zotero sync 可继续作为受限 tool API，或迁移到 v2 Job；不要在没有 Job/rollback 时直接冻结。

### Step 4：Idea、Intake 与 Claim

1. Idea native CRUD 完成后冻结 POST/PUT Idea。
2. Intake/materialize 单独设计项目初始化工作流；它不是普通对象 CRUD。
3. Claim 最后迁移：先实现和验证 R2/human/hash 全部门禁，再按 POST `/claims`、PUT `/claim/<C>` 分开冻结；任何门禁差异都应阻止切换。

### Step 5：保留并迁移 Experiment/Run 治理岛

1. 在此之前明确把所有 Experiment/Run、policy、grouping、workflow/review、Outbox、governance-task、Workspace/Server/routing 端点列入 exemption。
2. 新 v2 域必须能回放旧 `experiments.json`、`runs.json`、outbox/events，并证明 revision、review 与 authorization 不可绕过。
3. Web 新旧写路径先双写/影子校验；执行类操作不得双执行，只能单 authority + mirror event。
4. 验证后按依赖逆序切换：配置元数据 → Experiment/Run draft → review → Outbox claim/transition → execution integration；每组独立可回退。

### Step 6：surveyctl.py 写回桥

- 在 Experiment/Run 迁移前保持原样；它当前直接调用 `server.py` 的 authority 函数，并不经过 HTTP freeze。
- 迁移时把 `surveyctl.py` 改成调用一个共享 application service（或稳定的 localhost v2 API），而不是继续直接改 JSON/Markdown。
- CLI 与 Web 必须共享 revision/confirmation/lease 门禁；Outbox raw lease 不能经日志或普通 stdout 泄漏。
- 提供显式 legacy fallback 开关仅用于回退，且新旧 authority 不能同时消费 execution authorization。

### Step 7：1.x UI 下线顺序

1. 先让 1.x UI 对已迁移对象显示只读迁移提示，GET 保留。
2. v2 UI 完成端点级验收且 freeze 观察无必要回退后，移除对应 1.x UI 编辑控件，但不删除服务端 GET。
3. Experiment/Run/Claim UI 最后下线。
4. 至少一个稳定发布周期后，依据访问 telemetry 决定是否移除 1.x UI bundle；legacy GET 应继续保留到所有已知项目完成 store 初始化和读路径迁移。

## 风险排序

- **极高**：Experiment/Run review、execution authorization、Outbox/lease；Claim 审核门禁。
- **高**：paper canonical note 合并；全量 Comparison 覆盖；surveyctl 与 Web 双 authority。
- **中**：Question、Idea、Workspace/Server 配置；Obsidian 派生索引。
- **低但非 v2 对象问题**：GPT 生成/解析、scan、exploration request 等无持久化 POST；不应纳入写冻结。
