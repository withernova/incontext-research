# Architecture

```text
Research project (canonical Markdown)
  kernel/ + shell/ + state.md
          ↕ narrow managed sections / revision checks
server.py ── survey_tool/v2/http.py ── web/src → static/v2
    ↕
.survey-tool/*.json (runtime compatibility state)
    ↕
surveyctl.py (terminal agent writeback)
    ↕
Experiment → Run → resolved execution config → tmux/log/artifacts

skills/research-survey/             evidence and Claim gates
extensions/experiment-steward/    monitoring and bounded task scheduling
.publish/                           generated GitHub-readable snapshot
```

Experiment Steward 使用项目级 v2 配置和独立 `steward-state/events` 持久状态；重启后不自动恢复 timer。旧 Watchdog 文件和 session entry 仅在新数据不存在时兼容读取，首次写入使用新名称。`/watchdog` 与旧工具名是带迁移提示的 deprecated aliases，安装时只能保留 `experiment-steward` 一份扩展。

Research Explorer 使用独立 extension/skill 和 `.pi/research-explorer-state.json` scheduler，不复用 Steward timer/queue。canonical 成果位于 `shell/07_explorations/`，公开 registry 只存摘要/hash；所有正文写入通过 `surveyctl exploration` 桥接。pi 重启后 active round 转 paused，必须显式 resume。

## 执行治理域的渐进拆分

`server.py` 保留 HTTP/storage wrapper，v2 路由集中在 `survey_tool/v2/http.py`，纯契约位于领域模块。唯一 Web UI 由 `web/src` 构建到 `static/v2`；旧单文件 UI 与 Codespace clone 入口已经下线。

## Trust boundaries

1. Browser input, GPT responses, Markdown and imported metadata are untrusted.
2. Research projects may be outside this repository and are discovered recursively with exclusions.
3. SSH aliases and remote paths are configuration; secrets must never be stored in project metadata.
4. A Run registry entry is not proof that execution occurred. Logs, artifacts, metrics and integrity gates provide evidence.
5. Human approval is required for formal execution and Claim verdict changes.

## Current implementation shape

The backend intentionally keeps a small standard-library HTTP shell, while canonical, Experiment, integration, Pi bridge and v2 routing behavior live in dedicated `survey_tool` modules. The React/TypeScript v2 application is the only served UI.

## pi 对话绑定：实时状态与持久快照

每个项目在 `.survey-tool/pi-binding.json` 保存最近一次已验证绑定的最小快照。快照仅包含 schema/version、项目规范路径、session 文件、session id、名称、话题和时间戳，不保存消息、prompt、模型凭据或其他秘密。写入复用工具状态的原子 JSON 写入机制。

绑定有两种不能混淆的状态：

- `live_bound=true`：本服务进程内存在可响应 RPC 的 pi 子进程，允许读取消息和发送 prompt。
- `persisted_bound=true`：磁盘上有项目专属快照。服务重启后通常只有此状态，前端显示“已保存 · 名称（待恢复）”，但不得把它当成实时 RPC，也不得自动启动进程。

用户点击“恢复已保存对话”后，服务按以下顺序解析：验证快照绝对路径；按 session header 的 id 或 basename 在 `~/.pi/agent/sessions/**` 中查找唯一匹配；最后按 header `cwd` 与项目 canonical path 匹配。路径必须位于 pi sessions 根目录且扩展名为 `.jsonl`。多个候选会返回 `ambiguous` 和候选列表，不随机选择；不存在、过期和非法路径分别返回 `missing`、`stale`、`invalid_path`。

`GET .../pi/state` 同时返回 live/persisted/recoverable 语义；`POST .../pi/restore` 是唯一的显式快照恢复动作。项目切换使用各自 canonical path 对应的 bridge 和快照，不能串用绑定。

## Execution Outbox 与 pi 派发

Outbox 是项目级、可重启恢复的持久状态机。授权事务可幂等创建 dispatch；claim 在 `tool_state_transaction` 内完成，确保并发消费者只有一个取得 lease。所有后续执行状态都验证 token、consumer 和前置状态。公开 dashboard/list 不包含 token。

pi bind/restore 成功后，服务在锁外检查人类策略和 bridge busy 状态；只有 `auto_deliver_on_pi_live=true` 的 queued/delivered 项会收到协调 Prompt。发送成功仅记 delivered，发送失败保留原待消费状态并留痕。新 live session 可立即重派；同一 session 默认 5 分钟冷却，显式派发也防抖，只有用户明确 `force=true` 才绕过冷却，且都不超过最大尝试次数。claim 后不再派发；`GET /pi/state` 无副作用。整个过程不启动 shell/SSH、不自动 claim。

claim/acknowledged 的租约到期会恢复 queued；running 表示 Run 授权已经由该 dispatch 消费，因此不自动过期回队。服务重启后 running 仍保持 running，必须由持有者 complete/fail 或由人类处理，防止重复执行。

Outbox reconciliation 的 GET/dashboard 仅做纯计划，不写项目；显式 POST、授权和 claim 才会补建 dispatch。claim 在候选范围内按 `authorization_timestamp` 从新到旧选择，避免先消费更旧的遗漏授权。任何正常授权即使 route/gate 内部读取异常，也会由 `ensure_authorization_dispatch` 留下同授权的确定性 blocked item，而不是只有内存错误。

路由健康把 `subject=requested|actual` 分开聚合。fallback ACK 只降低 requested route 健康；fallback 真正进入 running/complete 后，只增加 actual Agent 的健康记录，不会把原 requested Codex/model 洗白。`lightweight_governance` 是独立有效路由；旧 v1 两路由文件读取时从 `local_tool_edit` 继承，并在 API 标明 `inherited_from`。

## Run lifecycle 与实验代码架构

纯领域契约位于 `survey_tool/run_lifecycle/`：`contracts.py` 定义科研阶段，`architecture.py` 校验公共包、配置和 Shell launcher 的实现引用。Run 不再等同于 Python runner；Run 是研究设计、实现版本、执行记录和结构化结果的可复现实例。程序完成与科研完成分离：Outbox completed 进入 `analysis_pending`，研究者或协调 pi 保存关键数值与解释后才完成。
