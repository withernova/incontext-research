# Survey Tool 2.0 实施进度

> 更新时间：2026-08-15
> 分支：`rebuild/survey-tool-2.0`

## 已完成

### Phase 0：基线与决策

- 完整代码备份与 SHA-256；
- 建立独立 2.0 分支；
- 基线盘点；
- ADR-0001：React + TypeScript + Vite；
- ADR-0002：Markdown 研究正文 + SQLite 运行状态；
- v2 领域模型和 authority map。

### Phase 1：基础设施与应用壳

- SQLite schema migration runner；
- objects / relations / events / jobs / inbox 基础仓储；
- revision conflict、typed relation、Job 状态机与幂等键；
- `/api/v2/health` 与项目 capability；
- React/TypeScript 2.0 应用壳；
- 自带 Noto Sans SC 中文字体；
- 桌面与移动响应式布局；
- 全局对象搜索；
- 旧版 `/` 与新版 `/v2/` 并行运行。

### Phase 2：论文闭环的只读与候选检索切片

- 论文目录返回稳定 `citekey`；
- 修复 OpenAlex 大 JSON 被 4 KiB stdout 截断的问题；
- 原生论文库；
- 论文状态筛选和详情；
- PDF、MinerU、图片、七问与 Claim 数量摘要；
- 证据边界提示；
- 联网候选论文检索；
- 候选使用醒目的“未核验”状态，不自动进入正式证据库。

已加入受控写入基础：

- v2 schema version 5；
- 显式初始化 API，必须提交固定确认语句；
- GET / 浏览页面不会隐式建库；
- Paper Candidate 持久 registry、状态 revision、来源去重和 Job linkage；
- 论文检索可由用户确认启用候选登记；
- 登记候选不会下载 PDF、不会 ingest，也不会成为正式证据。

已完成持久 acquisition 基础：

- Candidate 可在二次人工确认后创建 PDF 下载 → MinerU 两段式 Job；
- Job 支持依赖、原子领取、lease heartbeat、过期回收与重启恢复；
- 下载限制为公网 HTTP(S)，检查重定向目标、PDF 文件头和 100 MiB 上限；
- 下载与 MinerU 产物只写 `.survey-tool/staging/`；
- Worker 不调用 `ingest.py`，不会写 `papers/`、`kernel/citations.md` 或研究正文；
- 服务请求只排队，不在 Web 线程执行长任务。

最终 canonical 门禁也已完成：

- 下载与 MinerU Job 都成功后才开放“核验并纳入”；
- 必须手工输入 `INGEST <citekey>`；
- 已存在 PDF、MinerU 目录、笔记或 citekey 时拒绝自动覆盖；
- canonical 写入调用既有 `ingest.py`，保留 PDF SHA-256 与 citations 记录；
- ingest 失败会恢复原 `citations.md` 并删除本次半成品；
- 成功后记录 canonical path、content hash、时间与审计事件；
- Candidate 和 Job 状态可在页面刷新后恢复。

### Question 工作区

- 原生 Question 队列；
- 状态和正文搜索；
- 原始疑问、当前判断与深究记录分区；
- Paper / Comparison / Finding / Experiment 关联；
- 明确 Question 阶段性判断不等于 validated Claim。

### Experiment / Run 工作区

- Experiment 独立对象导航；
- Run Pipeline 泳道；
- 研究设计、审核、批准、授权、执行、分析、完成、失败和历史异常分离；
- reconciliation action 和 legacy untracked 可见；
- Run 研究设计与审计字段；
- 程序完成不等于科研完成；
- 不改变现有审核、授权、Outbox 和 Workspace gate。

### Research Analysis 工作区

- 原生 Comparison 列表和详情；
- 参与论文与分析轴；
- canonical 综合分析；
- Finding 空状态与列表；
- Finding / Comparison 不自动等于 validated Claim。

### Migration inventory / dry-run

- 只读扫描 12 类 legacy / canonical 来源；
- 每个来源文件记录 SHA-256、大小、解析状态、记录数与 authority；
- 明确排除 `.publish/`、`.git/`、`.pi/`、codespace 和实验产物；
- 损坏 JSON 显式报告，不静默记为零；
- GET dry-run 不创建 v2 SQLite、不复制或修改 canonical 文件；
- Automation 页以默认收起区展示摘要和冲突；
- 真实 `incontext` dry-run：17 个来源文件、6 个 PDF、1 个排除镜像提示、0 个数据冲突。

### Agent session binding 基础

- v2 只索引 session identity、provider、目标对象、任务类型、Agent/model 摘要和健康状态；
- 不复制消息、Prompt、上下文文件或凭据；
- pi 绑定只接受旧系统已经验证过的稳定 session ID 快照；
- 前端/API 不能任意提交 session 文件路径；
- provider + external reference 唯一，禁止同一 session 静默跨对象重绑；
- 状态更新使用 revision；
- 遵循 pi runtime replacement 语义，不缓存或复用 `/new`、`/resume`、`/fork` 前的 session 对象。

### Automation 工作区

- 调研、实验与混合三种模式；
- v2 持久 Automation 对象、固化预算和 revision；
- 保存治理草稿、提交审批、人工批准激活与复制命令相互独立；
- draft / awaiting_approval / active / paused / checkpoint / terminal 状态机；
- hybrid 从调研进入实验阶段必须第二次独立人工批准；
- 页面刷新后恢复 Automation 历史，支持选择对象和继续治理；
- Herdr Execution Record Slice 1：v7 持久短时单次授权与人工 revoke；绑定 approved Launch Request revision/snapshot，capability/target/active-record 门禁齐全，HTTP 只写记录且从不启动或调用 Herdr；
- Herdr Executor Slice 2：显式 one-shot、preflight-only CLI；原子 claim、私有 hash lease、heartbeat/安全 finish、并发 1 和显式过期 ownership reconciliation；只运行 capability discovery，不创建或控制 Herdr 资源；
- Herdr Executor Slice 3：新增显式 `--start-owned` 与窄 Herdr adapter；只允许 sibling split + `codex` start，双响应精确 ownership attestation 后进入 `running`，不 prompt；失败保留资源并转人工 attention，测试全部 mock；
- 展示固化预算、revision、deadline 与对象级事件时间线；
- UI 覆盖暂停/恢复、检查点、完成/预警完成、失败与取消；
- 首次激活按固化 duration 计算并持久化 deadline；
- 保存或批准状态不会自动发送命令、启动 Agent 或创建/执行 Run；
- Question / Experiment 目标选择；
- deadline、轮次和间隔预算；
- 生成 terminal pi Research Explorer 协调命令；
- 明确“复制命令不等于启动”；
- 调研证据、阶段转换、Run 治理和停止条件；
- Research Explorer proposal 不等于 validated synthesis。

### Herdr Launch Request 治理

- 后端只读探测当前服务是否由 Herdr 管理、CLI 是否可用和是否支持 Codex；
- 探测有 750 ms 超时和 4 KiB 输出上限，不公开终端拓扑、session、路径或相邻 Agent；
- v2 schema version 6 持久化 Herdr Launch Request；
- Launch Request 只允许 Codex、受限任务类型、短摘要和白名单预算；
- draft / awaiting_approval / approved / cancelled 状态机使用 revision、固定确认语句和 append-only event；
- Automation 页面提供可折叠治理控制台和事件时间线；
- 批准明确返回 `execution_started: false`，不调用 Herdr；
- ADR-0003 已提出后续独立 Execution Authorization、one-shot Executor、ownership attestation、lease 和恢复合同，当前尚未实现执行层。

### Agent Session Binding UI

- Automation 页面展示当前项目已验证 pi 快照的安全摘要；
- 只显示名称、live/stale、最后核验时间和不可逆 identity fingerprint；
- 不返回完整稳定 session ID，不暴露 `.jsonl` 路径、消息、Prompt 或上下文；
- 可显式绑定到 Automation、Question 或 Experiment，并选择任务类型；
- legacy Question/Experiment 仅创建最小 v2 reference identity，不复制正文、不切换 authority；
- Question / Experiment authority 继续分别是 Markdown / legacy JSON；
- 创建和刷新绑定均记录对象审计事件，并标明 messages/prompt 未复制。

### 持久 Job 运维控制台

- Automation 页面集中展示 PDF 下载、MinerU 和其他 v2 Job；
- 展示 queued/running/failed/succeeded 汇总、依赖状态、attempt、revision、progress；
- running Job 展示 Worker、heartbeat 和 lease 到期时间；
- failed Job 可在理由必填、revision 校验后回到 queued；
- queued Job 可人工取消，并原子取消仍 queued 的依赖后继 Job；
- running Job 不允许网页强制取消，避免数据库状态与仍在写 staging 的进程分裂；
- 重试和取消均写入对象审计事件，且明确不会启动或终止 Worker。

### 归档与 Legacy MinerU 收口

- Automation 页面提供 v2 原生 Candidate / Automation 软归档与恢复 UI；
- 当前 / 已归档筛选、批量选择、影响计数和 blocker 可视化；
- 理由必填、revision 预检、批次全有或全无；
- 记录归档前状态，恢复时回到真实原状态而非统一 active；
- active/paused/checkpoint/awaiting_approval Automation 禁止归档；
- 有 queued/running Job 的对象禁止归档；
- legacy reference、Question、Experiment 和 Run 不在通用归档范围；
- v2 仅开放软归档 / 恢复，不提供硬删除 API；
- canonical 文件、staging、event、Job、relation、session index 和 content hash 不删除；
- Experiment / Run 继续服从 legacy governance；
- 1.x 进程内 MinerU 入口仅保留兼容，2.0 不再调用；
- v2 Worker 支持 one-shot 和有界 polling loop，并可优雅停止；
- 操作边界记录于 `docs/2.0/OPERATIONS.md`。

### Content Index migration（Phase 2）

- 在 Identity Index（Question/Experiment）之上新增第二阶段内容索引；
- 只读索引 6 个 paper PDF（stable citekey）、4 个 comparison、4 个 finding、2 个 claim identity；
- 关系：comparison → paper（compares）、finding → comparison（derived_from）、claim → paper（derived_from）；
- authority 不变：paper=canonical files、comparison/finding=Markdown、claim=kernel gate；
- 不复制正文、不修改 canonical 文件、不切换 authority；SQLite 只存 identity + relation 索引；
- 迁移检查器新增 Content Index 计划、独立确认语句与持久检查点历史；
- 修复 claims 解析中 `\s*` 跨越换行导致空字段误吞下一行的问题（改用 `[ \t]*`）；
- 已对真实项目 incontext 显式初始化 v2 store（schema v7）并应用 Identity + Content Index；
- 幂等重跑：11 + 16 个 identity 复用、0 新增、25 条关系稳定。

### v2 对象索引接入

- 新增只读 `GET /api/v2/p/<proj>/objects`，返回 native objects、relations 与按 type 汇总；
- store 未初始化时返回 `initialized: false`，不会隐式建库；
- 2.0 首页“系统状态”面板显示已索引对象/关系计数，并新增“v2 对象索引”区展示各 type 数量；
- 正文仍以 Markdown / kernel 为 authority，SQLite 只承担 identity + relation 索引。

### Phase 3：工作区 native 对象核对（ADR-0004）

- Paper / Question / Comparison 三个工作区新增 `V2IndexNote` 核对条：显示 native 计数、legacy 读穿计数、该类型关系数，并声明“正文 authority 不变”；
- store 未初始化时不显示核对条，页面刷新后从 `/objects` 重新拉取；
- 扩展 paper 索引：把 `papers/INDEX.md` 中无本地 PDF 的目录条目（如 PromptHub）也作为 reference identity 索引（canonical_path 为空），使 paper 计数与 legacy 读穿一致（7/7）；
- 真实项目 native 索引：paper 7 · comparison 4 · question 4，均与 legacy 读穿一致。

### Phase 4：低风险对象双写（ADR-0004）

- 新增 `refresh_v2_index`：best-effort、幂等、永不抛异常、store 未初始化即跳过、plan blocked 只记 warnings；
- `save_question` 写后同步 identity 索引（`content=False`），`save_compares` 写后同步 content 索引（`identity=False`）；
- 1.x 写入口 authority 不变，双写只是索引同步；
- 由 Herdr 委托 codex agent（`w1:p4`）实现，人工审查通过；端到端验证 question/compare 写后自动进入 v2 索引。

### Phase 5：1.x 写入口冻结（ADR-0004）

- 原可逆写入口冻结已经由 v2 硬切换取代：有 v2 等价能力的 legacy 写入口固定返回 410，旧单文件 UI 与 Codespace clone 已删除；
- 门控 4 个写入口，端点级 key：`question.create`、`question.update`、`comparison.create`、`comparison.replace`；冻结时返回 409 `legacy_write_frozen`；
- GET 读路径、Experiment/Run 治理与 `surveyctl.py` 不受影响；默认不冻结，删除 key 即可恢复；
- 由 Herdr 委托 codex agent（`w1:p4`）实现，人工审查通过。

### Phase 6 · Step 0 + Step 1（进行中）

- Step 0：freeze 升级为端点级 key，计算/读型 POST 不纳入冻结；
- Step 1 后端：新增 v2 Question native 写 API（POST/PUT `/api/v2/p/<proj>/questions`），复用 canonical Markdown 写入器 + content-hash 乐观并发（409 `content_hash_conflict`）+ 写后刷新 identity index；
- 由 Herdr 委托 codex agent（`w1:p4`）实现，人工审查通过；
- Question v2 写闭环已通过隔离 shadow 验证；真实运行配置已冻结 `question.create` / `question.update`，legacy GET 保留，删除配置 key 即可回滚。

### Phase 6 · Step 1 前端（已完成）

- Question 工作区具备创建/编辑闭环：内联新建表单 + 详情编辑态（标题/原始疑问/当前判断/深究记录），保存用 `_canonical_rev` 乐观并发，冲突提示「内容已被其它地方修改」；
- `read_questions` 新增 `_canonical_rev`（canonical Markdown 的 sha256）；`loadQuestions`/`createV2Question`/`updateV2Question` 接入；
- 由 Herdr 委托 codex agent（`w1:p4`）实现，人工审查通过。

### Phase 6 · Step 2 后端 + 分层重构

- Step 2 后端：新增对象级 Comparison/Finding v2 写 API（create/update，content-hash 乐观并发 + 写后刷新 content index）；
- v2 路由独立：新建 `survey_tool/v2/http.py`，`dispatch(method,path,body,deps)` 承载全部 `/api/v2/*` 路由，依赖注入避免循环导入；
- server.py 单体拆分：`survey_tool/canonical.py`（论文/引用/claim/idea/question/comparison/finding/state）、`experiments.py`（实验/运行/outbox/governance）、`integrations.py`（zotero/mineru/gpt/github/obsidian/exploration）、`pibridge.py`（pi 桥 + v2 投影）；
- 导入接线：显式 `from server import ...` 取函数/常量，可变全局（CFG/SKILL/SKILL_SCRIPTS/HERE/BRIDGES）用 `server.X` 实时访问，不使用 `globals().update` 反模式；
- `server.py` 从 4816 行降到 1217 行；新增 v2 端点只改 `http.py`、领域逻辑只改对应模块；
- 由 Herdr 委托 codex agent（`w1:p4`）实现，人工审查通过；全套 144 测试通过。

### Phase 6 · Step 2 前端 + 第一批 1.x 写退役

- `ResearchAnalysisWorkspace` 已提供 Comparison/Finding 创建、编辑、取消和防重复提交；写入只调用 v2 API，不再跳转 1.x 工作台；
- Comparison/Finding 更新提交各自 `_canonical_rev`，409 `content_hash_conflict` 会提示并刷新当前项目；写成功后同时刷新 WorkspaceData 和 v2 object index；
- 在真实 `incontext` 的 6.2MB 隔离文本 shadow 副本上完成 migration + Question/Comparison/Finding create/update + 三类 stale-hash 409 + canonical Markdown 落盘 + v2 index refresh 验证；源项目 Git 状态与 canonical 文件未改变；
- 本地运行配置已冻结 `question.create`、`question.update`、`comparison.create`、`comparison.replace`；live `:7421` 验证四个 legacy 写入口返回 409、Question/Comparison/v2 object GET 继续可用；
- 修复模块化后的直接启动问题：`python3 server.py` 将 `__main__` 实例注册为 `server`，避免领域模块二次加载造成循环导入；`import server`、direct-start smoke、v2 API 24 tests 均通过。

### Phase 6 · Paper 写闭环 + 第二批 1.x 写退役

- 新增共享 `update_paper_canonical` service，legacy/v2 共用 seven、annotation、state merge 语义；state-only 更新不重写 canonical Markdown；
- `PUT /api/v2/p/<proj>/papers/<citekey>` 使用固定确认语句和 `_canonical_rev` content-hash 门禁，写后刷新 content index；citekey 仅接受安全文件名字符；
- v2 Paper Library 已提供七问内联编辑，以及图片标注新增、编辑、删除；编辑保留 annotation boxes，冲突时刷新 bundle；
- 在真实 `incontext` 文本 shadow 上验证七问写入、annotation boxes、stale-hash 409、state-only Markdown 不变、legacy freeze 与 GET 可用；
- 本地运行配置新增冻结 `paper.update`；删除该 key 并重启即可回滚。

### Phase 6 · Idea 写闭环 + 第三批 1.x 写退役

- `read_ideas` 返回共享 `idea.md` 全文件 `_canonical_rev`；新增 v2 Idea create/update API，字段白名单覆盖全部现有 canonical Idea 用户字段但禁止覆盖 created/updated；
- 新增 v2 Idea Workspace：导航、搜索、创建、详情、完整字段编辑、Claim 引用规范化和冲突刷新；明确 Idea 仍是 proposal；
- 真实项目文本 shadow 已验证完整字段、共享 revision、create/update、stale-hash 409、legacy create/update freeze 与 GET 可用；
- 本地运行配置新增冻结 `idea.create` / `idea.update`，删除 key 并重启即可回滚；Claim 状态不受影响。

### Phase 6 · Intake operator workflow + 第四批 1.x 写退役

- Intake 保持 `INTAKE.md` authority；v2 将保存与 materialize 拆成独立确认动作，保存使用全文 hash，materialize 只读取已保存且 revision 匹配的输入；
- 新增 v2 Intake Workspace，覆盖全部现有字段，提供 dirty 检测、仅保存、人工确认 materialize 及 stdout/stderr/returncode 展示；
- 真实项目文本 shadow 通过保存、partial-safe merge、stale-hash 409、mock materialize、动作分离和 legacy freeze 验证；
- 本地运行配置新增冻结 `intake.update`；legacy GET 保留，删除 key 并重启即可回滚。

### Phase 6 · Experiment/Run v2 facade 与交互模型修正

- v2 Experiment Workspace 不再以只读 Kanban 作为唯一主界面；默认恢复 Experiment 方案、Run 职责文件夹、Run 独立详情与完整研究记录编辑，Pipeline 改为辅助视图；
- 新增 Experiment/Run create/update、Run grouping、review/authorization 和 research workflow v2 facade，全部委托现有 `experiments.py` service 与 JSON/Markdown authority；
- 普通表单禁止修改 status/review/authorization/dispatch/lease/history；审核、退回、批准和单独授权继续通过现有状态机与 Outbox gate；
- workflow v2 UI 与状态机对齐：研究设计确认 → 代码方案就绪 → 提交审核 → 批准/退回 → 单独授权；不提供直接运行或 claim 按钮；
- Experiment 可编辑指标定义；Run 阅读态按研究设计、数据指标、实现执行、结果边界分组直接展示，编辑态恢复核心字段和 JSON 校验；
- 当前未冻结 Experiment/Run legacy 写入口，等待真实项目观察；完整 Python 回归 150 passed，Vitest 5 passed，production build 通过。

### Phase 6 · Experiment/Run AI discussion 与 GitHub snapshot prompt

- Experiment 与 Run 详情恢复 1.x 的“与 AI 讨论”入口，并明确分为当前终端 pi 与 GitHub 外部 AI 两种上下文来源；
- terminal pi prompt 由后端根据当前 workflow/review/authorization、Mission、实时项目路径和有效 agent route 生成；预览可编辑，可复制，仅在 bridge live 时显式发送；
- 外部 AI prompt 复用 canonical `gpt_assistant_instruction`，生成前可同步完整 `.publish` snapshot，并固定 GitHub repository 与 commit SHA；
- 首次 GitHub 绑定使用本机 `gh` 登录，v2 不接收或保存 PAT；repo name、visibility 和 include options 均有严格输入校验；
- AI prompt preview 不写 canonical、不审核、不授权、不启动 Agent 或 Run；GitHub 同步只更新 `.publish` mirror，不 push canonical project repository；
- 聚焦 API 与完整回归通过：151 Python tests、5 Vitest tests、production build 和 diff check。

### Phase 6 · Readiness：Markdown、环境绑定与论文来源

- 新增不使用 HTML 注入的安全 Markdown reader，覆盖 Question、Comparison、Finding 与 Run 阅读态的标题、列表、引用、代码、链接和表格；
- v2 Experiment 恢复 Server/Workspace 执行环境可见性和编辑入口，完整展示 `W-01`、SSH alias、远程仓库及执行路径；写入继续以 `.survey-tool/servers.json` / `workspaces.json` 为 authority，并使用 registry hash CAS；
- 环境面板明确区分 Intake `repo_path`、Workspace `remote_repo` 和 GitHub Publish snapshot，三者不自动互相覆盖；
- Paper Finder 统一提供 OpenAlex、arXiv 与 Zotero 本地库三种来源；所有结果先登记 Candidate，再进入 staged acquisition、MinerU 和显式 ingest；
- Zotero attachment 只由服务端 item ID 解析并复制到 `.survey-tool/staging`，浏览器不接收本地路径；arXiv ID 严格校验并只生成 `arxiv.org` PDF URL；
- 完整回归通过：156 Python tests、7 Vitest tests、production build、Python compile 和 diff check。

### Phase 6 · Paper acquisition 可操作性修复

- arXiv 检索改用 HTTPS；上游失败时仅用带严格 arXiv identity 的 OpenAlex 结果降级，完全失败返回明确 502，不再以 HTTP 200 空列表掩盖错误；
- Paper Candidate acquisition 新增确认式本地 Worker 入口；每项目只允许一个受控 daemon，限定目标 Candidate 和最多处理任务数，不接收命令或路径；
- Paper Finder 每 2 秒刷新 Candidate/Job，分别显示 PDF acquisition 与 MinerU 的 queued/running/succeeded/failed、attempt 和错误详情；
- queued Candidate 可显式“在本机开始准备”，失败 Job 可说明理由后重试并启动 Worker；两步成功后才出现 canonical ingest；
- 公开 Job API 移除 lease token，本地 MinerU 使用最长 3600 秒的有界 lease，避免两分钟误回收；
- 回归通过：158 Python tests、7 Vitest tests、production build、compile 和 diff check。

### Phase 6 · Question 工作区完整操作闭环

- Question 新建与编辑覆盖 title、status、原始疑问、当前判断和深究计划；错误、冲突与部分关联失败改为页面内反馈；
- 新增六类关系管理：Paper、Comparison、Finding、Experiment 写回 Question canonical frontmatter 并建立 typed index；Idea、Claim 只建立 v2 导航关系，不修改目标内容或 Claim 治理状态；
- 关系添加按目标真实类型映射固定语义，支持搜索、初始多选、幂等同步、精确移除和 stale-hash 409；不允许浏览器提交任意 relation type；
- Question 本地 Pi 与外部固定 commit AI discussion 使用真实 Markdown 和完整 canonical/navigation 关系，只读且不允许晋升 Finding 或批准 Claim；
- “打开讨论”假跳转已移除，关联卡片和管理入口均有真实操作；Question 写后同时刷新 WorkspaceData 与 v2 object/relation index；
- 回归通过：161 Python tests、12 Vitest tests、production build、compile 和 diff check。

### Phase 6 · Paper/Candidate AI discussion 与 UI 收敛

- 正式 Paper 和持久 Paper Candidate 均可打开“与 AI 讨论”；支持问题、审阅、反方质疑、比较、改写与验证实验，以及整篇、七问、方法、证据、局限和研究相关性焦点；
- 本地 Pi prompt 读取真实 canonical/MinerU 或受限 staging 上下文，明确只读、非执行、非审批，并将论文正文与元数据视为不可信输入；
- 正式 Paper 的外部 AI prompt 固定 GitHub repository 与 commit；Candidate 在未 canonical ingest 前禁止外部 AI，避免虚构仓库对象；
- 七问输出继续走 preview-first import，不自动写 canonical；AI 发送不再弹二次确认，后端固定 confirmation gate 保留；
- Candidate 初始化、登记、准备、重试和 ingest 均移除浏览器确认；明确动作按钮直接执行，后端安全边界不变；
- Candidate 任务区改为复用 Paper Library 的筛选、卡片、按钮、字号、颜色与状态样式，不再使用独立深蓝 queue UI；
- 回归通过：159 Python tests、10 Vitest tests、production build、compile 和 diff check。

### Phase 6 · Candidate discovery 与持久任务分离

- Paper Finder 将瞬时“检索发现”与持久“候选与本地任务”拆成独立视图；更换检索词、来源或关闭弹窗不会隐藏 Candidate/Job；
- 候选目录直接读取 v2 registry，支持按 title/citekey/DOI/source 模糊过滤，并按处理中、失败、可纳入、已纳入筛选；
- 论文库固定入口显示未纳入 Candidate 数量；登记搜索结果后自动进入候选目录，后续准备、Worker、重试和 ingest 均以 stored Candidate 为 authority；
- 回归通过：158 Python tests、9 Vitest tests、production build 和 diff check。

### staged Worker + MinerU 接入

- 安装 MinerU 3.4.5：conda python 3.12 环境 + `mineru[pipeline]`（纯 CPU），补装缺失的 `six`，`mineru` 符号链接到 `~/.local/bin`；
- Worker 默认 `-b pipeline`（`MINERU_BACKEND` 可覆盖 GPU 后端），并回退查找 conda env 下的 `mineru`；
- Phase 2 端到端验收通过：临时项目上真实 arxiv PDF → download → mineru(pipeline) → canonical ingest（PDF + `hybrid_auto/` + SHA-256 citations），重复 ingest 幂等；
- 真实 incontext 项目仍未执行 canonical ingest，等待正式研究节奏。

## 测试基线

- Python：144 tests；
- 旧版 JavaScript：5 个测试文件；
- 2.0 Vitest：5 tests；
- Playwright：18 tests，桌面与移动双项目；
- E2E 覆盖真实数据加载、搜索、论文库、候选隔离、Question、Comparison、Experiment Pipeline 和横向溢出；
- `git diff --check` 通过。

## 当前运行地址

- 1.x：`http://127.0.0.1:7421/`
- 2.0：`http://127.0.0.1:7421/v2/`

## 数据安全状态

- 真实项目 v2 store 已初始化并应用 Identity/Content Index；SQLite 仍只承担对象身份、关系和运行状态，研究正文 authority 不变；
- Question、Comparison、Finding 已由 v2 UI/API 写 canonical Markdown；对应 1.x 写入口已冻结，legacy GET 暂时保留；
- Claim 审批与 Experiment/Run execution governance 仍沿用现有权威实现，不因本轮 cutover 放宽门禁；
- 冻结可通过删除 `config.json` 的对应 `freeze_legacy_writes` key 立即回滚。

## 下一步

Identity Index Phase 1 与 Content Index Phase 2 均已实现并应用到真实项目 incontext：单事务写入 reference identity 与明确关系，幂等可重跑，正文与 authority 不变。

已完成（原计划 1–4）：

1. Herdr Execution Record 与单次授权；
2. one-shot Executor 只读 preflight（mock 验证 ownership/lease/恢复）；
3. `--start-owned` 一次性隔离 Codex Agent smoke（mock 覆盖）；
4. 审核 migration dry-run 与 authority map，显式初始化真实项目 v2 store，应用 Identity Index + Content Index。

剩余：

Phase 2（staged Worker + canonical ingest）已验收：MinerU 3.4.5（conda python 3.12 + `mineru[pipeline]`）安装完成，临时项目 `v2-smoke` 上以真实 arxiv PDF 跑通 download → mineru → canonical ingest；worker 默认 `-b pipeline`（`MINERU_BACKEND` 可覆盖）。

后续按 ADR-0004 推进：

- Phase 3：✅ 已完成（工作区 native 对象核对条 + 无 PDF 目录条目索引）；
- Phase 4：✅ 已完成（低风险对象双写：question/compare 写后 best-effort 同步 v2 索引）；
- Phase 5：✅ 已完成（1.x 写入口冻结机制，默认关闭、可逆、配置门控）；
- Phase 6：进行中（Question/Comparison/Finding v2 前后端闭环、shadow 验证和第一批 legacy 写冻结已完成；下一批为 Paper/Idea/Intake/Claim v2 facade）。
