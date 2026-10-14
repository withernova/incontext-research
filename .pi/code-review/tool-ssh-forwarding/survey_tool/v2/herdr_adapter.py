"""Narrow Herdr adapter for creating one Survey Tool-owned interactive agent."""

from __future__ import annotations

import json
import os
import re
import selectors
import shlex
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

HERDR_TOPOLOGY_TIMEOUT_SECONDS = 20.0
# Herdr itself defaults to 30 seconds. Pi startup can legitimately take longer,
# so give the CLI a bounded 60 seconds and the outer process a small grace
# period instead of killing Herdr before its own readiness check can finish.
HERDR_AGENT_START_TIMEOUT_MS = 60_000
HERDR_AGENT_START_TIMEOUT_SECONDS = 65.0
HERDR_PROMPT_TIMEOUT_MS = 240_000
HERDR_PROMPT_TIMEOUT_SECONDS = 245.0
HERDR_OUTPUT_LIMIT_BYTES = 8192
HERDR_CONSOLE_OUTPUT_LIMIT_BYTES = 65536
# Launch requests still persist only a short human summary. This larger,
# bounded envelope is rebuilt from current canonical records at start time.
HERDR_ENVELOPE_LIMIT_BYTES = 12000
HERDR_SHELL_READY_ATTEMPTS = 50
HERDR_SHELL_READY_INTERVAL_SECONDS = 0.2
HERDR_REMOTE_AGENT_READY_ATTEMPTS = 120
HERDR_REMOTE_AGENT_READY_INTERVAL_SECONDS = 0.5
REMOTE_PROVISION_TIMEOUT_SECONDS = 20.0


def _clip_utf8(value: Any, limit: int) -> str:
    """Bound display-only envelope data without splitting UTF-8 characters."""
    text = str(value or "")
    raw = text.encode("utf-8")
    if len(raw) <= limit:
        return text
    return raw[: max(0, limit - 3)].decode("utf-8", "ignore") + "…"


def _compact_run_context(context: dict[str, Any], limit: int) -> str:
    """Keep execution identity and high-value hints; canonical remains authority."""
    source = context if isinstance(context, dict) else {}
    experiment = source.get("experiment") if isinstance(source.get("experiment"), dict) else {}
    run = source.get("run") if isinstance(source.get("run"), dict) else {}
    workspace = source.get("workspace") if isinstance(source.get("workspace"), dict) else {}
    compact: dict[str, Any] = {
        "experiment": {"id": _clip_utf8(experiment.get("id"), 48)},
        "run": {"id": _clip_utf8(run.get("id"), 48)},
        "workspace": {
            "id": _clip_utf8(workspace.get("id"), 48),
            "server_id": _clip_utf8(workspace.get("server_id"), 48),
        },
        "context_compacted": True,
        "canonical_reread_required": True,
    }
    implementation = run.get("implementation_ref") if isinstance(run.get("implementation_ref"), dict) else {}
    trial_plan=run.get("trial_plan") if isinstance(run.get("trial_plan"),dict) else {}
    if trial_plan:
        axes=trial_plan.get("axes") if isinstance(trial_plan.get("axes"),list) else []
        compact["run"]["trial_plan"]={
            "contract":"survey-tool.run-trial-plan/v1",
            "planning_mode":str(trial_plan.get("planning_mode") or "matrix"),
            "request":_clip_utf8(trial_plan.get("request"),160),
            "trial_budget":trial_plan.get("trial_budget") or len(trial_plan.get("trials") or []),
            "axis_names":[_clip_utf8(axis.get("name"),32) for axis in axes if isinstance(axis,dict)][:6],
            "concurrency":trial_plan.get("concurrency"),
            "max_retries":trial_plan.get("max_retries"),
            "canonical_plan_required":True,
        }
    optional = [
        (("run", "command"), _clip_utf8(run.get("command"), 240)),
        (("workspace", "remote_repo"), _clip_utf8(workspace.get("remote_repo"), 180)),
        (("run", "purpose"), _clip_utf8(run.get("purpose"), 140)),
        (("run", "metric_plan"), _clip_utf8(run.get("metric_plan"), 140)),
        (("run", "research_question"), _clip_utf8(run.get("research_question"), 140)),
        (("experiment", "title"), _clip_utf8(experiment.get("title"), 100)),
        (("experiment", "objective"), _clip_utf8(experiment.get("objective"), 140)),
    ]
    for key in ("package_root", "entrypoint", "config_path", "launcher_path"):
        optional.append((("run", f"implementation_{key}"), _clip_utf8(implementation.get(key), 120)))
    for (group, key), value in optional:
        if not value:
            continue
        candidate = json.loads(json.dumps(compact, ensure_ascii=False))
        candidate[group][key] = value
        encoded = json.dumps(candidate, ensure_ascii=False, separators=(",", ":"))
        if len(encoded.encode("utf-8")) <= limit:
            compact = candidate
    encoded = json.dumps(compact, ensure_ascii=False, separators=(",", ":"))
    if len(encoded.encode("utf-8")) <= limit:
        return encoded
    # Extremely long or malformed identities must not block Steward creation.
    minimal = {
        "run_id": _clip_utf8(run.get("id"), 36),
        "context_compacted": True,
        "canonical_reread_required": True,
    }
    return json.dumps(minimal, ensure_ascii=False, separators=(",", ":"))


class HerdrStartError(RuntimeError):
    def __init__(self, message: str, *, split_succeeded: bool = False, failure_class: str = ""):
        super().__init__(message)
        self.split_succeeded = split_succeeded
        self.failure_class = failure_class


class HerdrCommandError(RuntimeError):
    def __init__(self, code: str = "command_failed"):
        self.code = code if re.fullmatch(r"[a-z0-9_]{1,80}", code or "") else "command_failed"
        super().__init__("Herdr command failed")


@dataclass(frozen=True)
class OwnershipAttestation:
    agent_name: str
    pane_id: str


@dataclass(frozen=True)
class TaskEnvelope:
    """Opaque, internally-built task input accepted by the prompt adapter."""

    text: str


@dataclass(frozen=True)
class PromptTurnResult:
    agent_status: str


@dataclass(frozen=True)
class AgentConsoleResult:
    text: str
    agent_status: str
    truncated: bool


def build_task_envelope(*, target_type: str, target_id: str, target_title: str,
                        task_type: str, task_summary: str,
                        reasoning_effort: str, max_turns: int,
                        agent_kind: str = "pi",
                        run_state: dict[str, Any] | None = None,
                        run_context: dict[str, Any] | None = None,
                        target_context: dict[str, Any] | None = None,
                        remote_workspace: dict[str, str] | None = None) -> TaskEnvelope:
    raw_summary = str(task_summary or "").strip()
    values = {
        "target_type": str(target_type or "").strip(),
        "target_id": str(target_id or "").strip(),
        "target_title": _clip_utf8(" ".join(str(target_title or "").split()), 160),
        "task_type": str(task_type or "").strip(),
        "task_summary": _clip_utf8(raw_summary, 1500),
        "reasoning_effort": str(reasoning_effort or "").strip(),
    }
    if not values["target_type"] or not values["target_id"] or not values["task_summary"]:
        raise ValueError("task envelope requires target identity and approved summary")
    if not 1 <= int(max_turns) <= 20:
        raise ValueError("task envelope fields are out of bounds")
    context_rules = ""
    if target_context:
        compact_context = _clip_utf8(
            json.dumps(target_context, ensure_ascii=False, separators=(",", ":")), 3200
        )
        context_rules = (
            "\n当前目标上下文（启动时从 canonical authority 重新读取）：\n"
            f"{compact_context}\n"
            "- 以上只属于当前选中目标；缺失字段必须报告，不能从相邻或旧对象推断。\n"
            "- 结果证据默认拒绝：只允许使用 solid_runs 与 explicit_run/object_references；相关 Solid 结果必须优先参考并在最终报告列出 ID。\n"
            "- 不得读取其他 Run、实验产物目录、旧日志、历史聊天或 Agent memory，不得递归展开引用；记忆与 canonical/Solid/显式引用冲突时丢弃记忆。\n"
            "- 显式参考对象仅供证据/定位，不得改写目标、数据、主指标、对照或 Claim 边界。\n"
        )
    run_rules = ""
    if values["task_type"] == "run_implementation":
        if values["target_type"] != "run":
            raise ValueError("run implementation requires a Run target")
        state=dict(run_state or {})
        stage=str(state.get("workflow_stage") or "unknown"); review=str(state.get("review_status") or "unknown")
        authorized=state.get("execution_authorized") is True; dispatch=str(state.get("dispatch_status") or "none")
        resume_dispatch=str(state.get("resume_dispatch_id") or "")
        context=dict(run_context or {})
        run_record=context.get("run") if isinstance(context.get("run"),dict) else {}
        trial_plan=run_record.get("trial_plan") if isinstance(run_record.get("trial_plan"),dict) else {}
        trial_directive=""
        if trial_plan:
            mode=str(trial_plan.get("planning_mode") or "matrix"); budget=int(trial_plan.get("trial_budget") or len(trial_plan.get("trials") or []))
            trial_directive=(
                "\n## 当前任务身份：参数批量实验（不可降级为普通单次 Run）\n"
                f"模式={mode}；Trial 预算/数量={budget}；并发={int(trial_plan.get('concurrency') or 1)}；目标={_clip_utf8(trial_plan.get('request'),300)}。\n"
                "第一步必须重新读取 canonical Run 的 trial_plan，并在回复中明确列出将执行的 Trial 计划。"
                "matrix 必须覆盖声明组合；ai_planned 必须规划恰好 trial_budget 个最有信息量的具体参数。"
                "随后调用 survey_run_execution prepare 时必须同时传 trial_manifest_json：contract=survey-tool.run-trial-manifest/v1，trials 按 T-001 连续编号且每项包含具体 parameters。"
                "后端会校验数量与矩阵覆盖；缺失或不符时无法 claim/start。然后生成批量 launcher、逐 Trial 产物和汇总，不能当作普通单次实验。\n"
            )
        # The ready-to-run governance text itself is intentionally detailed and
        # consumes much of the bounded envelope. Context is a navigation hint:
        # compact it deterministically and require canonical rereads instead of
        # making a long approved record prevent the Steward from starting.
        context_budget = 2200 if stage == "running" and resume_dispatch else 1500
        approved_context=_compact_run_context(context,context_budget)
        execution_first = ""
        if stage == "ready_to_run" and review == "approved" and authorized:
            execution_first = (
                "\n## Mandatory managed-execution action\n"
                "无需再次审核。先在绑定仓库完成实现并解析真实 command，默认不补测试；空 Shell launcher 不是 blocker。"
                "随后只调用一次 `survey_run_execution {action:" + '"continue"' + ",run_id:" + json.dumps(values["target_id"],ensure_ascii=False) + ",runtime_command:" + '"当前批准 Run 中的真实单行 command"' + "}`；工具会按 run_id 自动解析最新授权并原子完成 prepare/claim/ack/start。"
                "不得查询、记忆、展示或要求用户提供 dispatch ID。随后用 `{action:" + '"status"' + ",run_id:" + json.dumps(values["target_id"],ensure_ascii=False) + "}` 观察；只有 status 才能证明运行。\n"
            )
            if trial_plan:
                execution_first=(
                    "\n## Mandatory structured Trial action\n"
                    "不要用通用 Queue 或多次普通 Run 模拟参数实验。调用 survey_run_trials inspect 读取预算；完成代码核验后，用 plan 提交完整结构化 Trial 列表。"
                    "再用 start 传入一个真实批量 runtime_command；工具会固化 manifest，并原子完成精确 Run 的 claim/ack/start。"
                    "随后只用 survey_run_trials status/complete/repair/fail；缺少任一 Trial 指标时 complete 会拒绝。实现代码、launcher、导入或瞬时环境错误必须先 repair，在既定 max_retries 内修复并审阅后按 run_id 原地重启同一 manifest；仅用户明确要求时补测试；预算未耗尽不得把 Run 标记 failed，也不得要求用户重新批准或提供 dispatch ID。\n"
                )
        elif stage=="running" and resume_dispatch:
            if not re.fullmatch(r"dispatch-[a-f0-9]{24}",resume_dispatch): raise ValueError("invalid resume dispatch identity")
            execution_first=(
                "\n## Mandatory interrupted-Steward recovery\n"
                "前一个 Pi 会话已经中断，不能再使用它内存中的 lease。先只读核对下方 approved context 与当前 Run/Experiment/Workspace canonical 记录；不得重新启动第二个远端实验。"
                "随后调用 `survey_run_execution`，参数为 `{action:" + '"reattach"' + ",dispatch_id:" + json.dumps(resume_dispatch) + "}`。"
                "reattach 会在旧 lease 已过期、approved spec 与 Workspace 快照仍一致时原子轮换 lease，并立即执行一次 status heartbeat。"
                "成功后继续调用 status/complete/fail；不得 claim 新 dispatch、不得再次 start、不得把 token 写入消息或文件。\n"
            )
        run_rules = trial_directive + (
            "- 这是实现并调试 Run 的有界闭环；先回读 Run、Experiment、Workspace canonical。\n"
            f"- 当前批准上下文（只读、必须回查 canonical）：{approved_context}\n"
            f"- 状态：stage={stage}；review={review}；authorized={str(authorized).lower()}；dispatch={dispatch}；需回查。\n"
            f"- 最多 {int(max_turns)} 轮实现/审阅/修复；仅用户要求测试时进入实现/聚焦检查/修复循环，不自行补测试，不重复索要已授予的批准。\n"
            "- ready_to_run：空 Shell launcher 不是 blocker；只按 run_id 调用 survey_run_execution continue，再按 run_id status。dispatch ID 是内部审计实现，不得要求用户查询或提供。claim 后不得用 bash/SSH 绕过执行器。\n"
            "- Trial Run：matrix 覆盖矩阵，ai_planned 恰好生成 trial_budget 项；按 concurrency 运行并逐项保存 metrics/artifact。\n"
            "- 实现层故障：代码、launcher、runtime、transient/environment 错误先调用 repair；它保留批准快照和同一 attempt，释放代码修复权限。修复并审阅后按 run_id 继续；仅用户要求时补测试；只有预算耗尽或 invalid_spec/scientific/authorization/external_dependency 才可 fail。\n"
            "- running 恢复只 reattach 同一 dispatch，不启动第二份实验。不得自行批准、授权或改变目标、数据、主指标、对照、Workspace、Claim。\n"
            + execution_first
        )
    from survey_tool.implementation_policy import ALGORITHM_IMPLEMENTATION_GUIDANCE
    engineering_rules = ""
    if values["task_type"] in {"implementation", "code_edit", "run_implementation"}:
        engineering_rules = (
            "\n" + ALGORITHM_IMPLEMENTATION_GUIDANCE + "\n代码交付：\n"
            "- 开始先读 Git HEAD/status，区分已有改动与本任务改动。按任务需要实现，在准备提交、交接或运行时统一审阅；不为缺少测试阻断交付。\n"
            "- 远程代码修改已包含本任务 Git commit 授权：在代码交付检查点，调用 code_change_review，传 ssh_host、repository_path、已获授权且实际执行的 test_evidence（未测试可省略）、精确 commit_paths 与 commit_message，审阅通过后工具提交；不要等实验结束才提交实现或修复。已有用户改动不混入提交，不使用 git add . 或自动 push。\n"
            "- 传任务给出的 allowed/forbidden paths；blocking finding 修复后重审。review_current=false 表示提交钩子等改变了内容，需重新检查；仅暂存或提交不使内容相同的审阅失效。提交失败保留改动并报告具体原因。\n"
            "- 交付报告包含 commit SHA、review_id 和测试状态（未执行写‘未测试’）；当前实现通过 review 后继续已获授权的执行，准备工作不重复索要批准。\n"
        )
    remote_rules=""
    if remote_workspace and remote_workspace.get("local_code_rules"):
        remote_rules=str(remote_workspace["local_code_rules"])
        engineering_rules=engineering_rules.replace("远程代码修改已包含本任务 Git commit 授权", "本地代码修改已包含本任务 Git commit 授权").replace("传 ssh_host、repository_path", "传本地 repository_path（不传 ssh_host）").replace("不使用 git add . 或自动 push", "不使用 git add .；提交后按绑定工作流自动 code publish")
    elif remote_workspace:
        host=str(remote_workspace.get("ssh_host") or ""); repo=str(remote_workspace.get("remote_repo") or ""); tmux=str(remote_workspace.get("tmux_session") or "")
        if (not re.fullmatch(r"[A-Za-z0-9._:@-]{1,255}",host) or not repo.startswith("/")
                or any(char in repo for char in ("\0","\r","\n")) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}",tmux)):
            raise ValueError("invalid remote Workspace envelope")
        remote_intro = "程序已建立远端 tmux；Pi 仍运行在本机" if agent_kind == "pi" else "Codex 运行在本机；按下面的固定 SSH host 与代码根目录操作"
        remote_rules=(
            f"\n远端 Workspace（{remote_intro}）：\n"
            f"- SSH host：{host}；代码根目录：{repo}；tmux：{tmux}。\n"
            "- 代码操作限定于该远端仓库；长命令用上述 tmux，不得改本地 Survey Tool。\n"
            f"- 本地 Code Map：{_clip_utf8(remote_workspace.get('code_map_summary') or '尚无缓存', 600)}。它只用于定位，实际修改前仍核验相关文件。\n"
        )
    text = (
        "Survey Tool Herdr task envelope v1\n"
        f"目标：{values['target_type']} {values['target_id']}"
        + (f" — {values['target_title']}" if values["target_title"] else "") + "\n"
        f"任务类型：{values['task_type']}\n"
        f"推理强度：{values['reasoning_effort']}；最多轮次：{int(max_turns)}\n"
        "\n用户批准的任务：\n"
        f"{values['task_summary']}\n"
        "\n边界：\n"
        "- 当前本地工作目录是治理项目；只处理上面的目标与任务。\n"
        "- 先读取目标对应的当前项目资料，不从相邻对象臆测缺失上下文。\n"
        "- 不修改 Survey Tool 审批、Claim、Run 授权或其它治理状态。\n"
        "- 不读取或输出凭据、环境变量、终端/会话标识。\n"
        "- 若任务要求代码修改，仅做直接需要的改动；默认不测试/构建，仅用户明确要求时执行。\n"
        f"{context_rules}{remote_rules}{run_rules}{engineering_rules}"
        "\n最终请简洁报告：完成内容、审阅/测试状态（未执行写‘未测试’）、剩余风险。\n"
    )
    if len(text.encode("utf-8")) > HERDR_ENVELOPE_LIMIT_BYTES:
        raise ValueError("task envelope exceeds byte limit")
    return TaskEnvelope(text=text)


def _run_json(command: list[str], *, timeout: float, output_limit: int) -> dict[str, Any]:
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
    output = bytearray(); deadline = time.monotonic() + timeout
    selector = selectors.DefaultSelector()
    assert process.stdout is not None
    os.set_blocking(process.stdout.fileno(), False); selector.register(process.stdout, selectors.EVENT_READ)
    try:
        while process.poll() is None:
            remaining = deadline - time.monotonic()
            if remaining <= 0: raise TimeoutError("Herdr adapter deadline exceeded")
            events = selector.select(remaining)
            if not events: raise TimeoutError("Herdr adapter deadline exceeded")
            chunk = os.read(process.stdout.fileno(), min(1024, output_limit + 1 - len(output)))
            if not chunk: continue
            output.extend(chunk)
            if len(output) > output_limit: raise ValueError("Herdr adapter output limit exceeded")
        if len(output) <= output_limit:
            try: output.extend(os.read(process.stdout.fileno(), output_limit + 1 - len(output)))
            except BlockingIOError: pass
        if len(output) > output_limit: raise ValueError("Herdr adapter output limit exceeded")
        if process.returncode != 0:
            code="command_failed"
            try:
                error_payload=json.loads(output.decode("utf-8"))
                candidate=error_payload.get("error",{}).get("code","") if isinstance(error_payload,dict) else ""
                if isinstance(candidate,str) and re.fullmatch(r"[a-z0-9_]{1,80}",candidate): code=candidate
            except (UnicodeDecodeError,json.JSONDecodeError):
                pass
            raise HerdrCommandError(code)
        payload = json.loads(output.decode("utf-8"))
        if not isinstance(payload, dict): raise ValueError("Herdr adapter returned invalid JSON")
        return payload
    finally:
        selector.close()
        if process.poll() is None: process.kill()
        process.wait(); process.stdout.close()


class HerdrAdapter:
    def __init__(self, *, runner: Callable[..., dict[str, Any]] = _run_json, binary: str = "herdr",
                 sleeper: Callable[[float], None] = time.sleep,
                 remote_runner: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run):
        self._runner = runner; self._binary = binary; self._sleeper = sleeper; self._remote_runner=remote_runner

    def _wait_for_shell(self, pane_id: str) -> None:
        stable = 0
        for _attempt in range(HERDR_SHELL_READY_ATTEMPTS):
            try:
                payload = self._runner(
                    [self._binary, "pane", "process-info", "--pane", pane_id],
                    timeout=HERDR_TOPOLOGY_TIMEOUT_SECONDS, output_limit=HERDR_OUTPUT_LIMIT_BYTES,
                )
                info = payload.get("result", {}).get("process_info", {})
                shell_pid = info.get("shell_pid")
                foreground = info.get("foreground_processes")
                ready = (
                    isinstance(shell_pid, int) and shell_pid > 0
                    and isinstance(foreground, list) and len(foreground) == 1
                    and foreground[0].get("pid") == shell_pid
                )
            except (HerdrCommandError, TimeoutError, ValueError):
                ready = False
            stable = stable + 1 if ready else 0
            if stable >= 2:
                return
            self._sleeper(HERDR_SHELL_READY_INTERVAL_SECONDS)
        raise HerdrStartError(
            "created pane shell did not become ready", split_succeeded=True,
            failure_class="pane_shell_not_ready",
        )

    def inspect_remote_workspace(self, *, ssh_host: str, remote_repo: str, known_revision: str = "") -> dict[str,Any]:
        """Read one bounded Git structure snapshot; never read file contents."""
        host=str(ssh_host or "").strip(); repo=str(remote_repo or "").strip(); known=str(known_revision or "")[:96]
        if not re.fullmatch(r"[A-Za-z0-9._:@-]{1,255}",host) or not repo.startswith("/") or any(char in repo for char in ("\0","\r","\n")):
            raise HerdrStartError("invalid remote code Workspace")
        repo_arg=shlex.quote(repo); known_arg=shlex.quote(known)
        script=(
            f"test -d {repo_arg} || exit 72; "
            f"head_rev=$(git -C {repo_arg} rev-parse HEAD 2>/dev/null || printf unknown); "
            f"status_hash=$(git -C {repo_arg} status --porcelain=v1 --untracked-files=all 2>/dev/null | git -C {repo_arg} hash-object --stdin 2>/dev/null || printf unknown); rev=\"$head_rev.$status_hash\"; "
            f"if test \"$rev\" = {known_arg}; then printf '%s\\n' SURVEY_TOOL_CODE_MAP_UNCHANGED; "
            f"else git -C {repo_arg} ls-files --cached --others --exclude-standard 2>/dev/null | head -n 400 | sed 's/^/SURVEY_TOOL_CODE_MAP_FILE:/'; fi; "
            f"git -C {repo_arg} status --porcelain=v1 --untracked-files=all 2>/dev/null | head -n 100 | sed 's/^.../SURVEY_TOOL_CODE_MAP_CHANGE:/'; "
            "printf 'SURVEY_TOOL_CODE_MAP_REV:%s\\n' \"$rev\""
        )
        remote=shlex.join(["bash","-lc",script]); argv=["ssh","-o","BatchMode=yes","-o","ConnectTimeout=10",host,"--",remote]
        try: result=self._remote_runner(argv,input=None,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=REMOTE_PROVISION_TIMEOUT_SECONDS,check=False,shell=False)
        except subprocess.TimeoutExpired as exc: raise HerdrStartError("remote Code Map timed out",failure_class="remote_code_map_timeout") from exc
        output=bytes(result.stdout or b"")[-HERDR_CONSOLE_OUTPUT_LIMIT_BYTES:].decode("utf-8","replace")
        if result.returncode: raise HerdrStartError("remote Code Map unavailable",failure_class="remote_code_map_unavailable")
        revision=next((line.split(":",1)[1].strip() for line in output.splitlines() if line.startswith("SURVEY_TOOL_CODE_MAP_REV:")),"")
        if not revision or len(revision)>96: raise HerdrStartError("remote Code Map response invalid",failure_class="remote_code_map_invalid")
        files=[line.split(":",1)[1] for line in output.splitlines() if line.startswith("SURVEY_TOOL_CODE_MAP_FILE:")]
        changes=[line.split(":",1)[1] for line in output.splitlines() if line.startswith("SURVEY_TOOL_CODE_MAP_CHANGE:")]
        return {"revision":revision,"files":files,"changed_files":changes,"unchanged":"SURVEY_TOOL_CODE_MAP_UNCHANGED" in output}

    def start_owned(
        self, *, project_root: str, agent_name: str, agent_kind: str = "codex",
        topology: str = "new_tab", tab_label: str = "", session_name: str = "",
    ) -> OwnershipAttestation:
        if agent_kind not in {"pi", "codex"}:
            raise HerdrStartError("unsupported agent kind")
        tab_label = str(tab_label or agent_name).strip()
        session_name = str(session_name or tab_label).strip()
        if (not tab_label or len(tab_label) > 80 or any(ord(char) < 32 for char in tab_label)
                or not session_name or len(session_name) > 80 or any(ord(char) < 32 for char in session_name)):
            raise HerdrStartError("invalid owned display name")
        if topology == "new_tab":
            created = self._runner(
                [self._binary, "tab", "create", "--cwd", project_root, "--label", tab_label, "--no-focus"],
                timeout=HERDR_TOPOLOGY_TIMEOUT_SECONDS, output_limit=HERDR_OUTPUT_LIMIT_BYTES,
            )
            pane_id = created.get("result", {}).get("root_pane", {}).get("pane_id")
        elif topology == "split":
            created = self._runner(
                [self._binary, "pane", "split", "--current", "--direction", "right", "--cwd", project_root, "--no-focus"],
                timeout=HERDR_TOPOLOGY_TIMEOUT_SECONDS, output_limit=HERDR_OUTPUT_LIMIT_BYTES,
            )
            pane_id = created.get("result", {}).get("pane", {}).get("pane_id")
        else:
            raise HerdrStartError("unsupported Herdr topology")
        if not isinstance(pane_id, str) or not pane_id or len(pane_id) > 128 or any(char.isspace() for char in pane_id):
            raise HerdrStartError("topology response did not contain a valid pane", split_succeeded=False)
        self._wait_for_shell(pane_id)
        start_command = [self._binary, "agent", "start", agent_name, "--kind", agent_kind, "--pane", pane_id,
                         "--timeout", str(HERDR_AGENT_START_TIMEOUT_MS)]
        if agent_kind == "pi":
            start_command.extend(["--", "--name", session_name])
        try:
            try:
                started = self._runner(start_command, timeout=HERDR_AGENT_START_TIMEOUT_SECONDS,
                                       output_limit=HERDR_OUTPUT_LIMIT_BYTES)
            except HerdrCommandError as exc:
                if exc.code != "agent_pane_busy":
                    raise
                # Creation and shell registration can race even after process
                # visibility. A busy rejection occurs before Herdr launches
                # anything, so one bounded retry is safe and cannot duplicate Pi.
                self._wait_for_shell(pane_id)
                started = self._runner(start_command, timeout=HERDR_AGENT_START_TIMEOUT_SECONDS,
                                       output_limit=HERDR_OUTPUT_LIMIT_BYTES)
        except Exception as exc:
            failure_class = "agent_start_timeout" if isinstance(exc, TimeoutError) else f"agent_start_{exc.code}" if isinstance(exc,HerdrCommandError) else "agent_start_rejected"
            raise HerdrStartError(
                "owned agent start failed", split_succeeded=True, failure_class=failure_class
            ) from exc
        agent = started.get("result", {}).get("agent", {})
        # Herdr versions differ on whether agent start echoes pane_id. The
        # command was addressed to this freshly-created pane, so the exact
        # returned agent name is the ownership attestation; if pane_id is
        # present it must still match and can never redirect us elsewhere.
        returned_name = agent.get("name") or agent.get("agent_name")
        returned_pane = agent.get("pane_id")
        # Some Herdr releases report the runtime kind ("pi") instead of the
        # requested logical label. This is safe here because pane_id came from
        # the split performed immediately above; an existing pane is never
        # adopted. If a pane ID is echoed, it remains an exact requirement.
        if returned_name not in {agent_name, agent_kind} or (returned_pane is not None and returned_pane != pane_id):
            raise HerdrStartError("owned agent response was ambiguous", split_succeeded=True)
        return OwnershipAttestation(agent_name=agent_name, pane_id=pane_id)

    def start_remote_owned(
        self, *, local_project_root: str, ssh_host: str, remote_repo: str,
        agent_name: str, tab_label: str = "", session_name: str = "",
    ) -> OwnershipAttestation:
        """Provision an owned remote tmux, then start the visible Pi locally.

        Host and repository are server-side Workspace authority, never browser
        command input. The remote host needs only SSH and tmux; Pi remains a
        local Herdr agent and receives the remote context in its task envelope.
        """
        host=str(ssh_host or "").strip(); repo=str(remote_repo or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9._:@-]{1,255}",host):
            raise HerdrStartError("invalid remote code host")
        if (not repo.startswith("/") or len(repo)>2048 or any(char in repo for char in ("\0","\r","\n"))):
            raise HerdrStartError("invalid remote code repository")
        if not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}",agent_name):
            raise HerdrStartError("invalid owned agent name")
        tab_label=str(tab_label or agent_name).strip(); session_name=str(session_name or tab_label).strip()
        if (not tab_label or len(tab_label)>80 or any(ord(char)<32 for char in tab_label)
                or not session_name or len(session_name)>80 or any(ord(char)<32 for char in session_name)):
            raise HerdrStartError("invalid owned display name")
        tmux_name=f"st-{agent_name}"
        repo_arg=shlex.quote(repo); tmux_arg=shlex.quote(tmux_name)
        # OpenSSH sends its final argument through the remote login shell.  A
        # fixed `bash -lc` is therefore intentional: it resolves the same Pi
        # installation that an interactive login sees, while every registry
        # value remains individually shell-quoted.  Markers are fixed and safe
        # to show in the terminal; no path/environment value is echoed.
        remote_script=(
            f"if ! test -d {repo_arg}; then printf '%s\\n' SURVEY_TOOL_REMOTE_REPO_MISSING >&2; exit 72; fi; "
            "if ! command -v tmux >/dev/null 2>&1; then printf '%s\\n' SURVEY_TOOL_REMOTE_TMUX_MISSING >&2; exit 73; fi; "
            f"if tmux has-session -t {tmux_arg} 2>/dev/null; then printf '%s\\n' SURVEY_TOOL_REMOTE_TMUX_BUSY >&2; exit 75; fi; "
            f"tmux new-session -d -s {tmux_arg} -c {repo_arg}; "
            f"tmux has-session -t {tmux_arg} || exit 76; printf '%s\\n' SURVEY_TOOL_REMOTE_TMUX_READY"
        )
        remote_command=shlex.join(["bash","-lc",remote_script])
        ssh_argv=["ssh","-o","BatchMode=yes","-o","ConnectTimeout=10",host,"--",remote_command]
        try:
            provisioned=self._remote_runner(ssh_argv,input=None,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=REMOTE_PROVISION_TIMEOUT_SECONDS,check=False,shell=False)
            output=bytes(provisioned.stdout or b"")[-HERDR_OUTPUT_LIMIT_BYTES:]
            if provisioned.returncode!=0 or b"SURVEY_TOOL_REMOTE_TMUX_READY" not in output:
                marker=next((name for name in ("REPO_MISSING","TMUX_MISSING","TMUX_BUSY") if f"SURVEY_TOOL_REMOTE_{name}".encode() in output),"PROVISION_FAILED")
                raise HerdrStartError("remote tmux provisioning failed",failure_class=f"remote_{marker.lower()}")
            try:
                return self.start_owned(project_root=local_project_root,agent_name=agent_name,agent_kind="pi",topology="new_tab",tab_label=tab_label,session_name=session_name)
            except Exception:
                cleanup=shlex.join(["bash","-lc",f"tmux kill-session -t {tmux_arg} 2>/dev/null || true"])
                self._remote_runner(["ssh","-o","BatchMode=yes","-o","ConnectTimeout=10",host,"--",cleanup],input=None,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=REMOTE_PROVISION_TIMEOUT_SECONDS,check=False,shell=False)
                raise
        except HerdrStartError:
            raise
        except Exception as exc:
            failure="remote_ssh_timeout" if isinstance(exc,subprocess.TimeoutExpired) else "remote_tmux_start_failed"
            raise HerdrStartError("remote tmux/local Pi start failed",split_succeeded=True,failure_class=failure) from exc

    def prompt_owned(self, *, agent_name: str, envelope: TaskEnvelope) -> PromptTurnResult:
        if not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}", str(agent_name or "")):
            raise HerdrStartError("invalid owned agent name", split_succeeded=True, failure_class="prompt_rejected")
        if not isinstance(envelope, TaskEnvelope):
            raise HerdrStartError("prompt requires internal task envelope", split_succeeded=True, failure_class="prompt_rejected")
        if not envelope.text or len(envelope.text.encode("utf-8")) > HERDR_ENVELOPE_LIMIT_BYTES:
            raise HerdrStartError("invalid task envelope", split_succeeded=True, failure_class="prompt_rejected")
        try:
            prompted = self._runner(
                [self._binary, "agent", "prompt", agent_name, envelope.text, "--wait",
                 "--timeout", str(HERDR_PROMPT_TIMEOUT_MS)],
                timeout=HERDR_PROMPT_TIMEOUT_SECONDS, output_limit=HERDR_OUTPUT_LIMIT_BYTES,
            )
        except Exception as exc:
            failure_class = "prompt_timeout" if isinstance(exc, TimeoutError) else f"prompt_{exc.code}" if isinstance(exc,HerdrCommandError) else "prompt_rejected"
            raise HerdrStartError(
                "owned agent prompt failed", split_succeeded=True, failure_class=failure_class
            ) from exc
        result = prompted.get("result", {})
        agent = result.get("agent", {})
        returned_name = agent.get("name") or agent.get("agent_name")
        status = agent.get("agent_status") or agent.get("status")
        if result.get("type") != "agent_prompted" or returned_name != agent_name:
            raise HerdrStartError("owned prompt response was ambiguous", split_succeeded=True, failure_class="prompt_ambiguous")
        if status not in {"idle", "done", "blocked"}:
            raise HerdrStartError("owned prompt did not settle", split_succeeded=True, failure_class="prompt_ambiguous")
        return PromptTurnResult(agent_status=status)

    def prompt_owned_async(self, *, agent_name: str, envelope: TaskEnvelope) -> PromptTurnResult:
        """Submit one internally-built turn and return after Herdr accepts it."""
        if not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}", str(agent_name or "")) or not isinstance(envelope,TaskEnvelope):
            raise HerdrStartError("invalid owned prompt",split_succeeded=True,failure_class="prompt_rejected")
        if not envelope.text or len(envelope.text.encode("utf-8"))>HERDR_ENVELOPE_LIMIT_BYTES:
            raise HerdrStartError("invalid task envelope",split_succeeded=True,failure_class="prompt_rejected")
        try:
            payload=self._runner([self._binary,"agent","prompt",agent_name,envelope.text],timeout=HERDR_TOPOLOGY_TIMEOUT_SECONDS,output_limit=HERDR_OUTPUT_LIMIT_BYTES)
        except Exception as exc:
            raise HerdrStartError("owned prompt submission failed",split_succeeded=True,failure_class="prompt_rejected") from exc
        result=payload.get("result",{}); agent=result.get("agent",{}); returned=agent.get("name") or agent.get("agent_name")
        if result.get("type")!="agent_prompted" or returned!=agent_name:
            raise HerdrStartError("owned prompt response was ambiguous",split_succeeded=True,failure_class="prompt_ambiguous")
        return PromptTurnResult(agent_status=str(agent.get("agent_status") or agent.get("status") or "working"))

    def read_owned(self, *, agent_name: str, lines: int = 400) -> AgentConsoleResult:
        """Read bounded terminal output and current lifecycle from an owned name."""
        if not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}",str(agent_name or "")):
            raise HerdrStartError("invalid owned agent name")
        count=max(1,min(int(lines),500))
        info=self._runner([self._binary,"agent","get",agent_name],timeout=HERDR_TOPOLOGY_TIMEOUT_SECONDS,output_limit=HERDR_OUTPUT_LIMIT_BYTES)
        agent=info.get("result",{}).get("agent",{})
        if (agent.get("name") or agent.get("agent_name"))!=agent_name:
            raise HerdrStartError("owned agent is unavailable")
        read=self._runner([self._binary,"agent","read",agent_name,"--source","recent-unwrapped","--lines",str(count),"--format","text"],timeout=HERDR_TOPOLOGY_TIMEOUT_SECONDS,output_limit=HERDR_CONSOLE_OUTPUT_LIMIT_BYTES)
        result=read.get("result",{}); snapshot=result.get("read",{})
        if result.get("type")!="pane_read" or not isinstance(snapshot.get("text"),str):
            raise HerdrStartError("owned agent read response invalid")
        return AgentConsoleResult(text=snapshot["text"],agent_status=str(agent.get("agent_status") or "unknown"),truncated=bool(snapshot.get("truncated")))

    def owned_status(self, *, agent_name: str) -> str:
        """Read only the lifecycle of one attested Agent; never read its pane."""
        if not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}",str(agent_name or "")):
            raise HerdrStartError("invalid owned agent name")
        info=self._runner([self._binary,"agent","get",agent_name],timeout=HERDR_TOPOLOGY_TIMEOUT_SECONDS,output_limit=HERDR_OUTPUT_LIMIT_BYTES)
        agent=info.get("result",{}).get("agent",{})
        if (agent.get("name") or agent.get("agent_name"))!=agent_name:
            raise HerdrStartError("owned agent is unavailable")
        return str(agent.get("agent_status") or agent.get("status") or "unknown")
