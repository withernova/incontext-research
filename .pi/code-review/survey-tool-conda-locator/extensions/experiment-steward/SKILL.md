---
name: experiment-steward
description: "Experiment Steward：通过 SSH/tmux 对单个远程实验做结构化观察、动态调度、受控修复和 manifest_reference 归档。"
metadata:
  requires:
    bins: ["ssh"]
  os: ["darwin", "linux", "win32"]
  tags: ["ml", "monitoring", "remote", "ssh", "tmux", "experiment", "steward"]
---

# Experiment Steward（实验管家）

实验管家负责观察和协调，不拥有研究结论、Claim verdict、Run 审核或执行授权。它不会自动执行 shell/SSH；只有计时检查、已由人类确认的精确 remediation playbook，以及显式 archive 动作可以触发相应受限流程。

## 主入口

- `/steward start [minutes] | stop | status | archive`
- `experiment_steward_control`
- `experiment_steward_config`
- `experiment_steward_remediation`
- `experiment_steward_archive`
- `steward_task_queue`
- `survey_run_execution`：单个 Run 的受控执行
- `survey_run_trials`：参数实验专用；`inspect → plan → start → status → complete/fail`，结构化 Trial 数量、ID、参数和结果由 Python 后端校验
- 兼容且名称仍准确：`experiment_status`、`experiment_log`、`experiment_scan_errors`

旧 `/watchdog`、`watchdog_control`、`experiment_watchdog_config`、`watchdog_task_queue` 是 deprecated aliases；仍可用，但返回/展示迁移提示。不得同时安装旧扩展和新扩展。

## 配置与生命周期

Managed Run 配置按 Run 保存在 `.pi/stewards/<run-id>.json` version 2；状态和事件同样使用 `<run-id>.state.json` / `<run-id>.events.jsonl`。因此同一项目可同时运行多个独立 Pi Steward，后启动的 Run 不会重定向旧会话。`.pi/experiment-steward.json` 仅作为最后使用配置的兼容视图；扩展兼容旧 flat/nested Watchdog 配置，但 managed 工具始终优先按精确 Run ID 加载。

没有精确 Run 身份的旧手工配置仍使用 `.pi/steward-state.json` / `.pi/steward-events.jsonl`。Pi 重启后保留磁盘事实，但定时器不会自动恢复；对应 Run 必须显式 reattach/start，不能凭另一个 Run 的最新配置猜测。

若 `status` 发现进程内 lease token 已被后端轮换、撤销或过期，工具会丢弃这份陈旧内存凭证，并对同一个 running dispatch 自动 reattach 后重新读取状态。Pi 重载后内存 lease 为空时，也可直接对精确 Run 调用 `status`；工具会在唯一 running dispatch 上完成同样的安全重绑。不得把“内存中仍有 lease”与“后端已接受该 lease”混为一谈，也不得因此改用 bash/SSH 绕过 managed executor。

观察、错误 cursor/fingerprint 与队列分别写入：

- `.pi/steward-observations.json`
- `.pi/steward-error-events.jsonl`
- `.pi/steward-task-queue.json`
- `.pi/steward-task-events.jsonl`

旧文件只在新文件不存在时读取，绝不删除。

## 完成合同

completion 默认关闭。候选完成必须同时满足：所有 markers；所有 requiredArtifacts 与 metricsFile 存在且非空；可靠 process 检查；没有 open 或 `remediation_applied` incident；不处于修复/人工处理 phase；文件 size/mtime 连续 `stableChecks` 次稳定。严格零退出必须从配置的 `exitCodeFile` 读到整数 0；process 消失不能推定 exit 0。tmux/process 退出或日志单独出现 done 都不算完成。

## 修复边界

remediation 默认关闭。playbook 必须由人类在带 UI 的配置保存中确认；apply 只能引用配置中的 fingerprint、playbook id 和原文命令，不能接收任意 command。无匹配 playbook、预算耗尽或验证失败都转 needs_attention。

`requiresCodeEdit=true` 时插件不执行命令，只要求协调 pi 查询项目有效 `experiment_code_edit` 路由并委派；不得硬编码 Agent/model。`record_code_fix` 只登记外部 changed evidence。重启后至少验证一次 tmux/process 恢复且有新增 clean progress，才能把 fingerprint 标为 resolved。

## 归档边界

archive 默认关闭，第一版只支持 `manifest_reference`。归档位于项目内 `.survey-tool/experiment-archives/<runId>/<archiveId>/`，只生成受限的 `manifest.json` 和 `summary.md`，不是复制大文件，也不是科学结论。

prepare/finalize 都调用同一个严格完成 evaluator。manifest 不得含 playbook 命令、SSH 秘密、lease token、会话消息或 Prompt；日志和 metrics 内容最多各 64 KiB，并保留完整文件 hash 和 truncated 标记。若存在 active Execution Outbox，Run 回写不写 operational completed，只记录 completion pending；必须由持有 lease 的 consumer 用归档证据 complete。Run 回写只能通过当前 survey-tool 的 `surveyctl.py`，不得直接修改 Run JSON，不得修改 Claim verdict 或伪造指标。

## 调度与消息

每次 timer 先直接执行结构化 quick observation。ETA 只从最后匹配行按配置 regex 解析，失败不猜。incident/restart/verifying/completion candidate 和近完成使用最小间隔；有 ETA 使用 clamp 后的 ETA 比例；无 ETA 且持续健康时确定性退避。健康检查直接更新状态并重排，不必唤醒 LLM；只有 NEW/REOPENED、crash、completion candidate、archive failure 或必须人工处理时发送 followUp，streaming 时不得 steer。

Cursor/Fingerprint 与 task queue 的旧安全规则继续生效：只处理增量日志；历史错误不成为新授权；任务必须由用户定义并带验收条件；重试必须有 changed evidence；队列不能绕过 Run 审核、执行授权、Workspace policy 或 Claim verdict。

普通 Run 已批准授权后，优先按精确 `run_id` 调用一次 `survey_run_execution action=continue` 并传入批准上下文中的真实 command。该动作自动解析当前 dispatch 并完成 prepare/claim/ack/start；dispatch ID 只属于内部审计，绝不能要求用户查询、复制或选择。后续 status 也优先传 `run_id`，只有正在恢复同一 running attempt 的工具内部流程才使用 dispatch ID。

参数实验不要用通用 task queue 表示。Pi 必须先用 `survey_run_trials inspect` 读取预算，再用 `plan` 提交完整的 `T-001...T-N` 参数表；`start` 会一次完成 manifest 固化、精确 Run claim/ack、managed start，并自动启动一次快速观察。只有 metrics 中包含全部已计划 Trial，`complete` 才会成功。lease 仍只保存在当前 Pi 进程内。

若用户明确要求在当前 Run 内改变小范围参数，不要机械创建新 Run。调用 `survey_run_trials create`，把用户原话和完整 Trial 列表保存为该 Run 下新的 `C-xxx` Campaign；随后直接 `start`。Campaign 复用 Run 的研究问题、代码与 Workspace，并保存上一轮结果快照。只有研究问题、数据集或主指标发生变化时才建议新 Run。

若观察到新错误或进程/tmux 消失，扩展必须用 follow-up 唤醒当前 Pi。Pi 先读最新日志；需要修改实现或配置时调用 `survey_run_trials repair`（普通 Run 用 `survey_run_execution repair`），把本次 attempt 标记为可重试并解除 managed bash guard。随后只在绑定仓库内修复和聚焦测试，再用同一结构化计划重新 `start`。不得用 SSH/tmux 绕过 managed executor。

如果 Run 已被人类退回修改（`review_status=changes_requested`），旧 attempt、旧 lease 和旧 authorization 已永久失效。此时不得调用 `retry`、`repair`、`claim` 或 `start` 旧 dispatch，也不得把失效当作权限 blocker；应直接按 `review_requirements` 更新 canonical Run 与绑定仓库、完成聚焦检查。旧远端产物的清理由新 attempt 在受管执行中完成。修订完成后等待页面“批准当前修订并交给 Steward 重跑”冻结当前快照；新 Steward 只能使用由该动作创建的新 dispatch。
