# Experiment / Run 治理（第一版）

实验内部文档的阅读入口、记录时间、结果展示与刷新方式见 [Experiment 文档指南](EXPERIMENT_DOCUMENTS.md)。本页说明治理规则，不作为单个实验的当前状态摘要。

Experiment 是执行规则的边界。`run_groups` 可声明多个稳定责任分组，也可以为空。Run 的 `group_id` 可暂时为空，表示历史记录或待整理状态；非空时必须引用已声明分组。分组对象包含 `id`、`name`、可选 `description`，ID 只允许小写字母、数字、点、下划线和连字符。已分组 Run 的规范笔记写入：

```text
shell/06_experiments/<experiment-id>/runs/<group-id>/<run-id>.md
```

历史 Run 没有 `group_id` 时继续读取原来的 `runs/<run-id>.md`；首次归组更新会保留自由笔记并迁移到分组目录。

## 指标

`metric_definitions` 是 Experiment 级可复用定义。每项必须声明 `id`、`name`、`formula`、`meaning`、`direction`、`unit`、`aggregation`、`scope`；`direction` 只能是 `higher`、`lower`、`target` 或 `neutral`。Run 的 `metric_observations` 引用指标 ID，并记录 value、sample_count、uncertainty、provenance/artifact 和 interpretation。生成的 Markdown 会把每项观测写成可读小节，不再倾倒原始 metrics JSON。

## Workspace 环境策略

Workspace 的 `environment_policy` 支持：

- `allowed_write_roots`：允许写入的绝对路径根目录；未声明时仅从 repo、worktree 根和实验产物根推导。
- `read_only_roots`：只读路径；`remote_data_root` 默认进入这里，不会自动获得写权限。
- `forbidden_paths`：禁止路径；默认包含 `/tmp`，因此源码和持久产物不得放入 `/tmp`。
- `forbidden_operations`：执行 Agent 不得进行的操作。
- `temp_policy`：临时文件规则。
- `notes`：补充说明。

Workspace 编辑器提供三种人类可读预设：

- `research-safe`（推荐）：repo、worktree 和实验产物根可写，数据根只读，`/tmp` 禁止承载源码或持久产物，并保留破坏性操作禁令。
- `strict-read-mostly`：只有实验产物根可写，repo、worktree 和数据根只读。
- `custom`：保留并允许逐项编辑现有规则。

预设只负责填充表单，用户仍可修改每条规则。保存前 UI 会展示完整有效策略；移除 `/tmp` 禁令、允许写入 `/tmp`、清空禁止操作或让数据根可写时，需要额外明确确认。后端不会信任客户端提交的风险标记，而会从最终规则独立计算 `dangerous_exceptions`，并把存在危险放宽的策略记录为 `policy_preset: custom`。旧 API 客户端不提交 `environment_policy` 时会保留已有策略。策略只能通过 Workspace 管理端点修改，Experiment 和 Run 更新不能修改它。

激活 Run 前会解析 project、run、log、output、metrics 路径，再检查绝对路径、允许根与禁止路径。任何 violation 都会关闭激活 gate。

### 受控 Conda 激活定位

`environment_activation` 仍只接受声明式的 `conda:<环境名>`（或等价中文格式），不接受任意 shell。Managed preflight 和正式 launcher 使用同一个激活脚本，并验证环境名、`CONDA_PREFIX` 与 Python 实际路径的归属。

对已核验的 `SZY-3090` / `IPLoc` 组合，执行器明确加载 `/songzhengyue/miniconda3/etc/profile.d/conda.sh`，设置对应的 `CONDA_EXE`，并要求 Python 归属同一 `/songzhengyue/miniconda3/envs/IPLoc`。这只修正既有安装的定位，不修改 Workspace 环境声明或 Run 科学快照。安装或 hook 缺失时失败，不退回另一个同名环境或系统 Python。其他 host/env 保留原自动发现逻辑。失败后按带变化证据的 managed retry 恢复，不能裸 tmux 绕过证明。

该修复的回归测试定义在 `tests/test_managed_execution.py`；是否执行须以具体任务证据为准，不能仅凭测试文件存在声称通过。

## 只读查询

```bash
python3 surveyctl.py --project /path/to/project experiment context E-001
python3 surveyctl.py --project /path/to/project experiment constraints E-001
```

两条命令等价且不写状态，返回当前执行逻辑、Run groups、指标定义、Workspace 策略、禁止操作、每个 Run 的解析路径、策略违规和审核/授权 gate。HTTP 客户端可读取 `GET /api/p/<project>/experiment/<id>/constraints`（`context` 也是别名）。

治理注册表和结构化观测必须通过 UI、API 或 CLI 更新，不直接编辑 `.survey-tool`：

```bash
python3 surveyctl.py --project /path/to/project experiment governance E-001 \
  --run-groups-json '[{"id":"baseline","name":"基线"}]' \
  --metric-definitions-json '[{"id":"acc","name":"准确率","formula":"correct/n","meaning":"正确比例","direction":"higher","unit":"ratio","aggregation":"mean","scope":"evaluation"}]'

python3 surveyctl.py --project /path/to/project run update R-001 \
  --metric-observations '[{"metric_id":"acc","value":0.8,"sample_count":100,"uncertainty":"95% CI ±0.04","artifact":"metrics.json","interpretation":"高于基线"}]'
```

## 多 Agent 实现分工

规划、研究勘察、Run 设计、结果解释和 verdict 属于 pi Agent 与人类；Codex 不负责批准 Run 或授予执行权限。进入代码实现阶段时，如果 Herdr 可用，pi 应首先通过 Herdr 将完整、边界明确的实现需求委派给配置指定的 Agent。任何委派或 fallback 都不能绕过 Workspace 环境策略与那一次「交给 Steward」的人类动作。

## Run 记录与门禁（v2）

- 主表只有四栏：**研究问题 / 目的 / 方法 / 详细实现细节**。方法与实现细节会吸收历史字段（metric_plan、variables_controls、metric_definition、integrity_gates、acceptance_criteria、data_definition、data_scale、architecture_plan 等）并保留原文。
- `confirm-design`、`implementation-ready`、`submit-review` 不再有填表前置条件，也不再是必经步骤；`research_design → code_planning → ready_for_review → awaiting_review → ready_to_run` 仍可作为标签使用。
- 推荐路径是「实现 → 交给 Steward」：一次点击同时完成批准、单次执行授权并建立 Outbox dispatch。
- 批准后修改规范不再阻断执行，只在 Run 记 `spec_drift_fields`、在 Outbox 记 `spec_drift_noted`；唯一硬约束是 attempt 处于 running 时不得改写规范与实现证据。

## Agent 路由

顶栏“Agent 管理”维护项目本地 `.survey-tool/agent-routing.json`：

- `local_tool_edit`：本地 survey-tool、Skill、扩展等工具代码；当前 Agent/模型始终以 API 返回的有效路由为准。
- `experiment_code_edit`：实验仓库代码实现与获批 Run 的执行；当前 Agent/模型始终以 API 返回的有效路由为准。

每条路由可配置启用状态、Agent、精确模型 ID、fallback Agent 和 fallback 模型。Luna/Sol 只是兼容预选项，不代表当前有效值。浏览器从 API 填充当前路由，只保存配置和复制给协调 pi 的委派指令，不会声称自动启动 Herdr。实验代码修改与执行使用 `experiment_code_edit`；主模型不可用或额度耗尽时才按配置 fallback，并用 event 记录 requested route/model、actual agent/model 和 fallback reason。

Agent 的 Run 分组 proposal 默认直接走宽容接口，可以只包含建议移动的部分 `assignments`；未列出的 Run 保持当前 `group_id`，值为空表示未分组。每项独立处理：未知 Run、无效目标组、审核锁或目标 note 冲突只跳过该项，不阻塞其他安全移动。现有 group 永不删除；Agent 新组仅在实际应用/未变 assignment 引用时保留，或显式声明 `keep:true`（持久化前会剥离 keep）。严格人工 `run-grouping` 接口仍要求完整映射并保持原子性。

浏览器的“Agent 整理”分支完成后会自动读取最新 JSON 并调用宽容接口；失败时保留“读取并应用”手工重试。终端 Agent 可直接提交：

```bash
python3 surveyctl.py --project /path/to/project experiment agent-grouping E-001 --file shell/06_experiments/E-001/grouping-proposal.json
python3 surveyctl.py --project /path/to/project experiment agent-grouping E-001 --proposal-json '{"groups":[],"assignments":{"R-001":""}}'
```

返回的 `grouping_result` 包含 applied、skipped、unchanged、groups_added 与 totals，并写入 Experiment event。该动作不修改 review status、Claim verdict 或执行状态。

查询：

```bash
python3 surveyctl.py --project /path/to/project agent routing
```

Experiment `context/constraints` 和生成的 Mission 也会包含当前有效路由。路由属于本地工具元数据，不是研究事实；Experiment/Run API 不能修改它。

## Experiment 级自动提交（无评分、无预授权批准）

“自动审核策略”是人类对单个 Experiment 的显式开关，默认关闭。**评分机制已移除**：自动化只能把就绪的 Run 提交给人工审核，它不能批准、不能授权执行，因此不存在“填满字段换自动放行”的路径。

人类可开启“创建 Run 时自动提交审核”。该选项只在策略整体启用时有效，并且只处理服务端认可的 Agent 来源 Run。Run 会先完整持久化，再执行一次结构性检查（占位符、执行路径、Workspace policy、危险命令）；无缺口时只做 submit，保持 `pending_review` 等待人类审批，有缺口时保持 draft 并保存原因。human/manual 创建、普通 update 和读取均不会隐式触发。

自动动作只能由人类或协调流程显式调用：

```bash
python3 surveyctl.py --project /abs/project run auto-review R-001
python3 surveyctl.py --project /abs/project experiment auto-review E-001
```

单 Run 动作仅处理 draft 或 changes_requested；批量动作只遍历这些候选状态，并跳过已批准、完成或锁定项。actor 记为 `automation_policy`，但任何情况下都不会自动批准、自动授权执行或更新 Claim verdict。已批准规范的后续修改仍受既有审核锁和退回机制约束。

## Execution Outbox

人类可在 Experiment 页面独立配置 Outbox：关闭、授权后自动排队、pi 在线后自动派发、claim 租约和最大派发次数。开启自动派发需要二次确认。自动排队不会执行命令；自动派发只向已经实时绑定且不忙的协调 pi 发送 Prompt，状态只变为 delivered。

协调 pi 必须显式 claim 并保存 lease token，再按有效 `experiment_code_edit` 路由委派 Codex，随后 ACK、标记 running，最终以非空 log/artifact/result evidence complete，或以明确 failure class/reason/retryable fail。fallback 必须说明原因。规范重开会取消旧 dispatch，claim 时还会重新验证审核、授权、approved spec 和 Workspace gate。

```bash
surveyctl --project /path outbox list
surveyctl --project /path outbox status <dispatch>
surveyctl --project /path outbox enqueue R-001
surveyctl --project /path outbox claim-next --experiment-id E-001 --consumer pi:<session>
surveyctl --project /path outbox ack <dispatch> --lease-token <token> --consumer pi:<session> --actual-agent codex --actual-model sol
surveyctl --project /path outbox running <dispatch> --lease-token <token> --consumer pi:<session>
surveyctl --project /path outbox complete <dispatch> --lease-token <token> --consumer pi:<session> --artifact metrics.json --result-message 已核验
surveyctl --project /path outbox fail <dispatch> --lease-token <token> --consumer pi:<session> --failure-class infra --reason GPU不可用 --retryable
surveyctl --project /path outbox retry <dispatch> --reason GPU恢复 --evidence scheduler记录
surveyctl --project /path outbox reconcile --dry-run
surveyctl --project /path agent route-event --route experiment_code_edit --requested-agent codex --requested-model sol --result unsupported --message "400 not supported"
surveyctl --project /path governance-task list
surveyctl --project /path governance-task claim-next --consumer pi:<session>
surveyctl --project /path governance-task complete <task> --lease-token <token> --consumer pi:<session> --group-id baseline --reason "唯一匹配"
```

命令统一使用 `outbox` 对象和稳定 `dispatch_id`。ACK 的 actual agent/model 与 requested route 完全相同时不需要 `--fallback-reason`；任一不同都必须给出原因。delivered 可在新 pi session 立即重派，同 session 默认等待 5 分钟；页面“强制重派”会明确绕过冷却，但不会绕过最大派发次数，也不会派发 claimed/running 项。

同一 `execution_authorized_at` 在 queued、blocked、failed、cancelled、superseded、completed 等全生命周期只对应一个 dispatch。blocked 可在 gate 修复后通过显式 enqueue/reconcile 原地解除；failed 必须使用 retry 并给出变化依据。running 会消费 Run 执行授权并写入 dispatch linkage；claimed/acknowledged 租约可过期回队，running 不自动过期，避免两个 Agent 同时执行。complete/fail 只保存执行证据和治理关联，不改 Claim verdict。
## Experiment Steward（实验管家）

新扩展目录是 `extensions/experiment-steward/`，只能安装这一份。主入口是 `/steward start [minutes]|stop|status|archive`、`experiment_steward_control/config/remediation/archive` 和 `steward_task_queue`。旧 `/watchdog`、`watchdog_control`、`experiment_watchdog_config`、`watchdog_task_queue` 暂时兼容并标记 deprecated；状态、配置和事件写入新的 `steward-*` 文件，只有新文件不存在时才读取旧文件。

授权是“可靠入队”的承诺，不是执行：人工或 automation policy 授权后都创建 queued/blocked dispatch；只有 claim→ACK→running 消费授权。Pipeline Board 展示这一生命周期，Folder Board 继续只表达责任分类。历史 consumed 且没有 Outbox linkage 的 Run 固定进入 `legacy_untracked`，不能伪装 queued。

`run_organization_policy` 是人类专用策略。创建后只做唯一可证明的 group 匹配；含糊时建立 `classify_run` governance microtask。microtask 不改变 review/authorization、不能执行 Run，也不能绕过 Folder Board 的锁。

轻量待办使用 `lightweight_governance` 路由，旧路由配置会明确继承 `local_tool_edit`，人类可在 Agent 管理中独立设置。领取返回不超过 4 KiB 的单 Run prompt；状态进入 claimed，租约过期后才允许其他 consumer 重领。可先运行 `surveyctl --project /path governance-task prompt <task-id>` 查看指令，浏览器不会自动启动 Agent。

Pipeline 中“修复待入队”来自只读 reconciliation actions；页面 GET 不写状态，只有按钮 POST 或 claim 才补队列。claim 在过滤后的项目/Experiment 范围按授权时间从新到旧领取。

实验管家先直接做结构化 quick observation，再按 phase、ETA 和持续健康次数确定下一间隔。健康轮次只更新状态，不唤醒 LLM；NEW/REOPENED、crash、completion candidate、归档失败和人工处理才发送 followUp。process 匹配优先限定 tmux pane 子进程和 projectDir，避免把同机其他训练误判为本 Run。

remediation 必须由人类在带 UI 的 v2 config 保存中启用并确认精确 playbook。apply 不接受任意命令；无匹配 fingerprint、预算耗尽或恢复验证失败均停止并进入 needs_attention。`requiresCodeEdit` 不由插件执行，协调 pi 必须读取有效 `experiment_code_edit` 路由后委派，并以 changed evidence 回录。

completion 默认关闭，且是严格 AND 合同：markers、必需 artifacts/metrics、可靠 process/exit 条件、无 open 或 `remediation_applied` incident、非修复/人工处理 phase、连续 size/mtime 稳定缺一不可。严格零退出必须配置 `exitCodeFile` 且读到整数 0；process 消失不能推定成功。`agent_end` 不参与单实验 timer 调度或健康判断，结构化 observation 异常会转 needs_attention、通知一次并按安全间隔继续。

archive 第一版只做 `manifest_reference`，prepare/finalize 共用严格 evaluator。manifest 保存受限 inventory、错误/修复摘要及最多 64 KiB 的日志/metrics 内容与 hash；不保存 playbook 命令、Prompt 或秘密。稳定 hash 可在落盘后移除 `manifest_sha256` 复验。finalize 后 Run 只通过 `surveyctl.py` 写回“自动归档，待科研解释”和审计路径；若存在 active Outbox dispatch，不写 operational completed，必须由 lease holder 使用 manifest 证据 complete。

## 简化后的 Run 端到端流程

v2 Run 先用自然科研语言写清问题、目的、假设或比较关系，并说明复用哪些已登记指标及其公式。随后规划公共实验包：稳定 Pipeline、必要的 Hook/Adapter/Metric、Run 配置和薄 Shell launcher。代码实现完成并通过测试后再提交审核、单独授权并进入 Execution Outbox。进入 running 后生成 Experiment Steward 配置，但浏览器不会声称已经启动扩展；terminal pi 仍需实际加载并运行 `/steward start`。

Experiment Steward 监控本次实验并执行人类预授权的工程修复；它不能改变研究目的、指标或科研解释。程序结束后 Run 进入“待分析”，保存关键具体数值、比较对象、差值、不确定性、结果文件和解释后才完成。复杂的历史边界字段不再影响运行，明显局限只需简短记录；执行安全策略仍保持不变。
