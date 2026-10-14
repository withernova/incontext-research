# Survey Tool 2.0 操作说明

## 1. 服务边界

- 1.x：`7421`，继续承载尚未迁移的 legacy 写入入口。
- 2.0：`7422`，承载原生对象工作区和 v2 状态 API。
- 2.0 页面 GET 不会隐式初始化项目 SQLite。

## 2. 项目 v2 Store

`/api/v2/health` 与项目 capabilities 会进行一次只读 Herdr 能力探测。探测只公开当前服务进程是否由 Herdr 管理、CLI 是否可用、是否支持 `codex` agent kind，以及 available/unavailable 状态；不会返回 workspace/tab/pane/terminal/session 标识、路径、环境、终端输出、Prompt、消息或相邻 Agent。探测命令仅为 `herdr agent`，具有 750 ms 超时和 4 KiB 输出上限；失败按 unavailable 处理，不执行任何 Herdr 控制动作。

必须由用户在 UI 中确认，或向初始化 API 提交固定确认语句：

```text
INITIALIZE SURVEY TOOL 2.0
```

数据库位置：

```text
<project>/.survey-tool/survey-tool-v2.sqlite3
```

数据库不复制研究正文；Markdown、PDF、kernel Claim 门禁继续各自作为 canonical authority。

## 3. 持久 Paper Acquisition Worker

2.0 的 PDF 下载和 MinerU 任务不会在 Web 请求线程执行。先由用户登记候选并明确排队，再单独运行 Worker：

```bash
python3 -m survey_tool.v2.worker --project /absolute/project/path --worker-id local-paper-worker
```

只处理一个任务后退出：

```bash
python3 -m survey_tool.v2.worker --project /absolute/project/path --worker-id manual-once --once
```

安全边界：

- 下载与 MinerU 产物只进入 `.survey-tool/staging/`；
- URL 必须解析到公网地址；
- 重定向目标会再次检查；
- PDF 上限 100 MiB，并验证 `%PDF` 文件头；
- Worker 不调用 `ingest.py`；
- 服务重启后，过期 lease 任务可重新排队；
- staging → canonical 必须在 UI 输入 `INGEST <citekey>`；
- 已存在 canonical 文件或 citekey 时拒绝覆盖。

### Job 控制台

Automation 页面提供持久 Job 控制台：

- `failed` Job 可填写理由后重试；重试只返回 `queued`，不会启动 Worker；
- `queued` Job 可填写理由后取消；取消下载父 Job时会同时取消仍为 `queued` 的依赖任务；
- `running` Job 只展示 lease owner、heartbeat 和 lease deadline，不提供网页强制取消；
- running 任务必须由 Worker 正常结束，或在 lease 到期后由恢复机制重新排队；
- 所有人工重试和取消保留 revision 检查与对象审计事件。

### MinerU 安装与后端（2026-08-16 验证）

MinerU 3.4.5 要求 Python 3.10–3.13（系统 Python 3.14 不兼容），本机用 conda 建独立环境并装纯 CPU 的 `pipeline` 后端：

```bash
conda create -n mineru python=3.12 pip -y
/home/zhengyuesong/miniforge3/envs/mineru/bin/pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
/home/zhengyuesong/miniforge3/envs/mineru/bin/pip install "mineru[pipeline]" six
ln -sf /home/zhengyuesong/miniforge3/envs/mineru/bin/mineru ~/.local/bin/mineru
```

说明：

- `mineru[pipeline]` 依赖声明缺少 `six`，需手动补装；
- Worker 默认使用 `-b pipeline`（纯 CPU 兼容），可用环境变量 `MINERU_BACKEND` 覆盖为 `hybrid-engine`/`vlm-engine` 等 GPU 后端；
- Worker 先 `shutil.which("mineru")` 查找，再回退到 `~/miniforge3|miniconda3|anaconda3/envs/mineru/bin/mineru` 与 `~/.local/bin/mineru`；
- 首次运行会从 ModelScope/HuggingFace 下载 pipeline 模型（约 15 MB，缓存复用）。

### staged Worker + canonical ingest 验收 runbook（Phase 2）

在具备 `mineru` 二进制与公网访问的环境中，对**测试候选**（使用临时测试项目，不要用真实 incontext）执行一次端到端验收：

1. 显式初始化测试项目 v2 store；
2. `POST /paper-candidates` 登记一个测试候选（真实公网 OA PDF URL）；
3. `POST /paper-candidates/<id>/acquisition`（确认语句 `STAGE PAPER ACQUISITION`）排队两段式 Job；
4. 运行两次 `python3 -m survey_tool.v2.worker --project <测试项目> --worker-id manual-once --once`（一次 download、一次 mineru），或用有界 polling loop；
5. 确认两个 Job 均 `succeeded`、产物只在 `.survey-tool/staging/`；
6. `POST /paper-candidates/<id>/ingest`（确认语句 `INGEST <citekey>`）执行 canonical ingest；
7. 验收：`papers/<stem>.pdf` 与 `kernel/citations.md` 新增且带 `content_hash`，`shell/03_evidence/papers/<citekey>.md` 生成；
8. 重复 ingest 应返回已纳管的幂等 no-op（`verification_status=ingested`），不重复写文件；失败回滚由 `tests/test_v2_ingest.py` mock 覆盖。

**已验收（2026-08-16）**：临时项目 `v2-smoke` 上以 arxiv 2503.06287（7.8 MB）跑通 download → mineru(pipeline) → canonical ingest，产出 PDF + `hybrid_auto/` + 带 SHA-256 的 citations 条目，重复 ingest 幂等。真实 incontext 项目仍未执行 canonical ingest，等待正式研究节奏。

## 4. Legacy MinerU

1.x 的 `/api/p/<project>/mineru/parse` 仍使用进程内任务，仅为兼容旧工作台。其状态在服务重启后不可恢复。

2.0 不调用该入口。新候选必须使用 v2 持久 Job 和上述 Worker。旧入口在 1.x 写入功能迁移完成前保留，不进行破坏性删除。

## 5. Migration Dry-run

Automation 页面中的 Migration Dry-run 是只读操作：

- 不初始化数据库；
- 不复制文件；
- 不修改 Markdown/JSON/PDF；
- 记录来源 SHA-256、authority、记录数和解析错误；
- 排除 `.publish/`、`.git/`、`.pi/`、codespace 与实验产物。

Dry-run 通过不等于批准正式迁移。当前 Experiment/Run authority 仍是 legacy JSON。

### Identity Index Phase 1

这一阶段只把 legacy Question / Experiment 的最小 identity 和 Question frontmatter 中已明确的 Experiment 关系写入 v2 SQLite。它不复制正文、不修改 canonical 文件，也不切换 Markdown / legacy JSON authority。

操作顺序：

1. 先在 Automation 页展开“迁移 Dry-run”，核对 Question、Experiment、明确关系数量和所有预警。
2. 如页面显示 v2 Store 未初始化，先使用项目 v2 Store 的独立显式初始化操作。迁移接口不会代为初始化。
3. `question_parse_error`、`experiment_parse_error`、`duplicate_identity` 或 `existing_identity_conflict` 会阻止应用；先停止并人工核对来源，不在迁移器中猜测修复。
4. 只在预检无阻塞后点击“显式应用索引”，并确认人工提示。
5. 应用后重新运行 Dry-run，核对持久检查点的 hash、新建 / 复用 identity 数和关系数。同一来源可幂等重跑；已存在的匹配 identity 会记为复用。

应用使用单个 SQLite 事务；任何 identity 冲突都会使整批回滚。当前不提供网页回滚动作；如检查点数量或 hash 与审核预期不符，不要继续后续迁移，保留数据库和来源现状供人工调查。

### Content Index Phase 2

第二阶段在 Question/Experiment 之外，只索引 canonical paper PDF、Comparison、Finding 和 Claim 的最小 identity 与明确关系：

- paper 对象 ID 使用与 `citekey_for` 一致的 stable citekey（标题前 8 字符 + 年份），canonical_path 指向 `papers/<file>.pdf`；
- comparison 对象 ID 来自 `.survey-tool/compares.json` 的稳定 `id`，canonical_path 指向 `shell/04_comparisons/<id>.md`；
- finding 对象 ID 与标题来自 `shell/04_comparisons/findings/F-*.md` frontmatter，canonical_path 指向该 Markdown；
- claim 对象 ID 来自 `kernel/claims.md` 的 `## Cxx` 段，只索引身份与状态摘要，canonical_path 固定为 `kernel/claims.md`；
- 关系：comparison `compares` paper、finding `derived_from` comparison、claim `derived_from` paper（citekey/sources/source_ref 推导）。

authority 不变：paper=canonical files、comparison/finding=Markdown、claim=kernel gate；不复制正文、不修改任何 canonical 文件、不切换 authority。

操作顺序与阻塞条件与 Identity Index 相同：先 dry-run 核对，独立初始化 v2 store；解析错误、`duplicate_identity`、`existing_identity_conflict` 会阻止应用；缺失的 paper/comparison 关系目标只跳过关系并产生预警，不阻塞整批。应用使用单个事务，幂等可重跑。应用确认语句为：

```text
APPLY CONTENT INDEX MIGRATION
```

## 6. Automation

### Experiment 勘察方案确认

Agent 用 `surveyctl experiment handoff E-xxx --file ...` 登记 `survey-tool.experiment-handoff/v1` 后，Experiment 详情顶部显示“待确认方案”，包含事实证据、可编辑的目标/实现范围/评估方式、风险和待答问题。没有问题时仍可直接核对方案并确认。仅保存 handoff.json 而未登记到 Experiment 的文件不会自动成为待确认方案。

点击“确认方案，继续准备 Run”会调用独立的 `/experiments/E-xxx/handoff/confirm` 接口。服务端在项目锁内核对 updated 与完整 handoff 快照，保存用户方案和回答、记录确认事件，并转为 confirmed。该动作不会创建、审核、授权或执行 Run。过期页面需刷新重新核对；归档或非待确认 Experiment 不能重复确认。

Automation 的三个动作相互独立：

1. 保存治理草稿和固化预算；
2. 提交审批 / 人工批准激活；
3. 复制 terminal pi 命令并由用户发送。

批准 `active` 不会自动启动 Agent，也不会创建、授权、入队或执行 Run。Hybrid 进入实验阶段还需要第二次独立批准。

## 7. Agent Session Binding

### Herdr Agent Launch Requests

v2 可持久保存受人工治理的 Herdr Agent 启动请求。请求必须指向已存在的 v2 identity；agent kind 仅允许 `pi` / `codex`，任务类型使用固定 allowlist。存储内容仅包括不超过 500 字符的任务摘要，以及白名单配置 `reasoning_effort` / `max_turns` / topology。

生命周期为 `draft -> awaiting_approval -> approved`，也可在批准前取消。提交、批准和短期执行授权均只记录治理状态，响应仍为 `execution_started: false`。只有用户在 Herdr 终端显式运行 one-shot Executor 才会创建 Agent。

### Herdr Execution Authorization · Slice 1

已批准的 Launch Request 可通过 `AUTHORIZE HERDR EXECUTION <request-id>` 创建短时、单次、revision-bound 的持久授权记录。授权要求目标未归档且 capability 同时报告 managed、CLI available、codex supported；同一请求只允许一个非终态 execution。授权只记录 approved snapshot hash、deadline、attempt 和安全 runtime 摘要，响应始终为 `execution_started: false`、`herdr_invoked: false`。原始 lease token 只在后续 one-shot Executor 原子 claim 时生成并保存在该进程内，数据库仅保存 hash；Web API 永不接触 token。

尚未 claim/start 的记录可用 `REVOKE HERDR EXECUTION <execution-id>` 和 execution revision 撤销。GET 不初始化 SQLite；公共响应不包含 nonce/hash、lease/owner、内部 Agent 名或任何 Herdr 标识。本阶段没有 executor，也不调用 Herdr。

### Read-only Executor Preflight · Slice 2

在 Herdr 管理的 pane 内，可显式运行一次只读预检：

```text
python3 -m survey_tool.v2.herdr_executor --project <path> --execution <id> --once --preflight-only
```

Executor 以项目级本地锁防止重叠运行，原子 claim 指定的 authorized execution，并重新核验授权期限、Launch Request revision/snapshot、目标状态、capability 和项目并发上限 1。lease 为 15–300 秒；原始 token 只存在于该进程，SQLite 仅保存 SHA-256。

本阶段只运行既有隐私安全 capability probe，完成后记录 `completed` dry-run checklist，且始终保持 `execution_started: false`、`herdr_invoked: false`。不会创建 pane/Agent，不会 prompt、发送按键或进入轮询。过期 claimed lease 仅能通过显式 ownership observation (`absent` / `live` / `ambiguous`) 协调，不做后台自动恢复。

### Owned Agent Start

`--preflight-only`（以及未指定模式）继续只做只读预检。只有显式 `--start-owned` 才进入 owned-start，复用原子 claim 和全部 preflight gate，创建一个新 tab/分栏和一个 ownership 可验证的 Agent，并提交固定任务 envelope。

Agent 名由 execution ID 与私有 lease hash 生成，限制为小写 32 字符，并只存于 execution 私有字段。pane ID 只在 adapter 内验证后丢弃，不进入数据库、事件、HTTP 或 stdout。启动失败或 ownership 歧义转为 `attention_required`，不会关闭或收养其他资源。

`implementation`（修改代码）和 `run_implementation`（实现 Run）使用绑定的 Server/Workspace：Executor 先以固定、完整 quoting 的 SSH 命令连接 Server，只创建一个以 `remote_repo` 为 cwd 的 detached tmux shell；随后 Herdr 在本机创建可见 tab 并启动本地 Pi。远端不需要安装 Pi。host/path/tmux 名只能由 registry 与 execution identity 生成，浏览器和任务摘要不能覆盖；短任务 envelope 告诉本地 Pi 只能经该 SSH Workspace 处理代码。仓库、tmux 缺失或 tmux 名冲突返回固定 `SURVEY_TOOL_REMOTE_*` 标记，不回显环境。正式运行仍由本地 Steward 通过 Managed Execution/Outbox 控制实验 tmux，避免把本地 lease 和审批状态复制到代码服务器。

每个 Workspace 在本地 `.survey-tool/workspace-code-maps.json` 保存一个可丢弃的 Code Map：Git HEAD + worktree-status fingerprint、最多 400 个 tracked/untracked 非忽略相对路径、顶层模块、关键 manifest 和当前变更文件。启动代码任务时先比较 fingerprint；未变化直接复用。Pi turn 完成后 Executor 自动重新读取 fingerprint/`git ls-files`/有界 changed-file 列表并以 0600 原子更新缓存，因此未提交的新模块也会进入下一次上下文。缓存不保存源码、数据内容、SSH 输出、环境或凭据，也不是 canonical authority；实际修改前 Pi 仍需核验相关文件。

远程代码交付按可验证的小步提交：Agent 开始先读取 Git HEAD/status，保留已有改动；实现或修复完成并通过聚焦检查后，用 `code_change_review` 的 `commit_paths` 与 `commit_message` 提交本任务文件，同时传远端 host/repository 和检查证据。工具先暂存明确文件，审阅通过才提交，保留其他暂存项，不 push；失败保留现场。报告包含 commit SHA、review ID 与检查结果。固定基线使已审阅内容的提交不触发重复审核；后续内容变更或提交钩子改动仍需重审。此流程属于已授权代码任务的交付步骤，不新增人工批准节点。

Experiment 通过 `code_repository_workspace_id` 关联一个代码仓库 Workspace；旧记录未设置时回退到 `workspace_id`。Workspace 可另登记 `external_code_url`（GitHub HTTPS）与 `external_code_ref`，供用户在“GitHub 外部 AI”中显式选择“真实代码仓库”。该模式不要求发布研究 snapshot，生成的只读 Prompt 只含仓库 URL、revision、目标 ID 和本轮问题，不包含 SSH host/path、Experiment/Run 正文、Solid 结果、结论或历史上下文；外部 GPT 必须通过用户已有的 repository connector 实际读取代码，并用 `path:line` 给出依据。

批准后的执行层采用 ADR-0003 的三段式门禁：Launch Request 审批、单次 Execution Authorization、Herdr 内 one-shot Executor 领取。Web API 只管理授权记录，不能调用 Herdr；Executor 只能管理由 Survey Tool 创建且 ownership 可验证的 Agent，不能复用或关闭现有用户 pane。

Run Steward 使用显式终端 handoff。Run 完成审核与单独授权后，Web 的“复制 Steward 启动命令”只生成并复制固定 `HERDR_ENV=1 python -m survey_tool.steward_runtime ... --start-agent` 命令，响应保持 `execution_started:false`、`herdr_invoked:false`。用户在独立 Herdr 本地终端运行后，才创建本地 Pi Steward；该 Pi 再通过既有 `survey_run_execution` 工具持有内存 lease、启动远端 managed tmux 并监控。项目路径、Run ID 与 CAS revision 由服务端生成并 shell quoting；浏览器不能提供 command、lease 或远端路径。

Pi Steward 是同一 Pi 进程中的 `experiment-steward` 扩展，不是第二个隐藏模型。新会话先只读核对选中 Experiment、Run、Workspace 及批准的代码入口，再以精确 Run ID 调用 `survey_run_execution claim/start/status`；扩展从 authority 重新解析 command 和 policy，不接受 Prompt 覆盖。若 Pi 会话中断，raw lease 随进程消失；旧 lease 到期后，Web 可生成新的 handoff，新 Pi 对同一 running dispatch 调用 `reattach/status` 并轮换内存 lease，禁止再次 `start` 第二个远端实验。lease 未到期时恢复会明确拒绝，避免两个 Pi 同时拥有执行权。

若旧 Pi 明显卡死且不能等待 lease 自然到期，Run 详情的“强制更换 Steward”要求人工确认，并调用固定确认短语 `FORCE RESTART V2 RUN STEWARD`。该动作只撤销旧 Pi token hash、立即使 lease 可 reattach，并生成新的本地 Herdr Pi handoff；running dispatch、远端 tmux、批准规范和执行授权均不重建。新 Pi 首个执行动作必须是同一 dispatch 的 `reattach/status`，旧 Pi 的后续工具调用会因 token 不匹配而失败。

若上一次失败仅发生在本地 Steward/Herdr 启动阶段，再次生成 handoff 会在确认同一授权 dispatch 仍为 queued 后，把旧 `attention_required` 清为 `handoff_ready`，并清除旧错误展示。若 execution attempt 已把 workflow-v2 Run 记为 `failed`，Run 详情会提供“重新启动 Steward（复制命令）”：它要求 `approved_spec` 未变化，保留旧 failed dispatch/失败证据，建立新的显式授权与新 dispatch，再生成新的 handoff；不会解锁研究字段，也不要求重新走设计审核。若 approved spec、Workspace policy 或绑定已变化，重启会 fail closed，必须重新审核/授权。

v2 只保存：session ID 派生索引、provider、目标对象、任务类型、Agent/model 摘要和状态。

Web API/UI 只显示不可逆 identity fingerprint，不返回完整稳定 session ID，也不暴露 `.jsonl` 文件路径。不会保存或读取消息、Prompt、上下文正文或凭据。

只有旧控制面已经验证并持久保存的当前 pi session 可以绑定。绑定到尚未迁移的 Question/Experiment 时，v2 只建立最小 reference identity；Markdown / legacy JSON authority 不变，正文不会复制进 SQLite。

pi 在 `/new`、`/resume`、`/fork` 后会替换 runtime；旧 session 对象不可复用，必须基于新 session identity 重新绑定。

## 10. v2 Question 写 API（Phase 6 Step 1 后端）

v2 提供 Question 的 native 写 API，复用既有 canonical Markdown 写入器：

- `POST /api/v2/p/<proj>/questions`：确认语句 `CREATE V2 QUESTION`；写 `shell/01_questions/Q-*.md` 后刷新 v2 identity index；返回 `{question, authority:"markdown", indexed:true}`；
- `PUT /api/v2/p/<proj>/questions/<Q-ID>`：确认语句 `UPDATE V2 QUESTION`；`expected_hash` 必须是当前 canonical Markdown 的 sha256（`sha256:` 前缀），不一致返回 409 `content_hash_conflict`；通过后合并字段写回并刷新 index；
- authority 仍是 canonical Markdown；SQLite 只同步 identity/relation 索引。

## 9. 1.x 写入口硬切换

对已有 v2 等价能力的 1.x 写入口执行不可逆的接口切换：

- 对应 POST/PUT 写入口永久返回 410（`reason=legacy_write_removed`），并返回精确的 v2 `migrated_to` 模板；不再读取 `freeze_legacy_writes` 配置；
- 支持的 key（端点级）：`question.create`（POST `/questions`）、`question.update`（PUT `/question/<Q-ID>`）、`comparison.create`（POST `/compares`）、`comparison.replace`（PUT `/compares`）、`paper.update`（PUT `/paper/<citekey>`）、`idea.create`（POST `/ideas`）、`idea.update`（PUT `/idea/<I-ID>`）、`intake.update`（POST `/intake`，含 save/materialize）；
- 计算/读型 POST（gpt/assistant、gpt/parse、scan-github、explorations/request、pi messages/last_text/models）不纳入写冻结；
- GET 读路径、Experiment/Run 治理与 `surveyctl.py` 不受影响；
- 根入口只服务 v2；旧 `static/app.js` UI 和 legacy Codespace clone 已删除；
- legacy GET 暂时仅作为 v2 canonical bundle 的内部读取适配器保留，迁到 v2 GET 后逐项删除；
- Claim、Experiment/Run 等没有被本次切换误删，其 authority 与治理服务继续由 v2 facade 调用。

## 8. 归档与删除

v2 只为原生 Paper Candidate 和 Automation 提供软归档和恢复：

- 必须提供理由；
- 必须匹配 revision；
- 批量预检任一失败则整批拒绝；
- 归档前状态写入审计事件，恢复时回到原状态；
- `awaiting_approval`、`active`、`paused`、`checkpoint` Automation 必须先完成或取消；
- 有 `queued` / `running` Job 的对象必须先安全结束 Job；
- 页面展示 Job、relation 和 session index 影响，但不删除它们；
- canonical 文件、staging、事件和 content hash 不删除；
- 不提供硬删除 API；
- legacy reference、Question、Experiment 和 Run 不由通用归档 API处理，Experiment/Run 继续服从 legacy governance。
