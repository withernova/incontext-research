"""Durable, prompt-free supervisor for one authorized managed Run.

The browser may start this local supervisor, but never receives an Outbox lease.
The supervisor owns the lease in memory, launches the already-approved command via
``managed_execution``, and stops at ``analysis_pending`` for human interpretation.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import os
import pathlib
import re
import shlex
import json
import subprocess
import sys
import threading
import time
import uuid

_ACTIVE={"preparing","agent_starting","agent_running","launching","claiming","starting","running","collecting"}
_RUN_ID=re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_STATE_FILE="steward-runtimes.json"
_START_LOCK=threading.Lock()
_ANSI_ESCAPE=re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\))")


def _safe_run_id(value):
    value=str(value or "").strip()
    if not _RUN_ID.fullmatch(value): raise ValueError("Run ID 不合法")
    return value


def _trial_plan_fingerprint(value):
    if not isinstance(value,dict): return ""
    encoded=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
    return "sha256:"+hashlib.sha256(encoded).hexdigest()


def _new_steward_agent_name(run_id, authorization, dispatch_id):
    """Return a private live-agent name unique to this handoff attempt."""
    import hashlib
    stem=re.sub(r"[^a-z0-9]+","-",str(run_id or "").lower()).strip("-")[:10] or "run"
    nonce=uuid.uuid4().hex
    digest=hashlib.sha256(f"{run_id}\0{authorization}\0{dispatch_id}\0{nonce}".encode()).hexdigest()[:10]
    return f"steward-{stem}-{digest}"[:32]


def _bounded_display(value, limit):
    """Keep a human label recognizable while respecting Herdr's 80-char cap."""
    value=" ".join(str(value or "").split())
    if len(value)<=limit: return value
    digest=hashlib.sha256(value.encode("utf-8")).hexdigest()[:6]
    return value[:max(1,limit-8)].rstrip(" ._-")+"…"+digest


def _steward_display(run,agent_name,trial_plan=None):
    run_id=_bounded_display(run.get("id") or "Run",38); variant=_bounded_display(run.get("variant") or "",24)
    kind="Trials" if trial_plan else "Steward"; suffix=f" · {variant}" if variant else ""
    tab_label=_bounded_display(f"{kind} · {run_id}{suffix}",80)
    session_name=_bounded_display(f"{run_id} · {'Parameter Trial Steward' if trial_plan else 'Experiment Steward'}",80)
    return {"agent_name":agent_name,"tab_label":tab_label,"session_name":session_name}


def _runtime_rows(root):
    import server
    value=server.read_tool_json(root,_STATE_FILE,{"version":1,"runs":{}})
    return value if isinstance(value,dict) and isinstance(value.get("runs"),dict) else {"version":1,"runs":{}}


def _update_runtime(root,run_id,**fields):
    import server
    run_id=_safe_run_id(run_id)
    with server.tool_state_transaction(root):
        data=_runtime_rows(root); prior=data["runs"].get(run_id,{})
        data["runs"][run_id]={**prior,"run_id":run_id,**fields,"updated_at":server.now_iso()}
        server.write_tool_json(root,_STATE_FILE,data)
        return dict(data["runs"][run_id])


def _pid_alive(value):
    try: os.kill(int(value),0); return True
    except (OSError,TypeError,ValueError): return False


def _public_runtime(value):
    allowed={"run_id","phase","runtime_kind","agent_status","started_at","updated_at","finished_at","error_class","message","dispatch_id"}
    return {key:value[key] for key in allowed if key in value}


def _status_for_run(run,runtime,dispatch,experiments,agent_active=None):
    revision_open=experiments.run_review_status(run)=="changes_requested"
    if revision_open:
        # Runtime rows and failed dispatches remain audit evidence, but they no
        # longer describe the current controller after a human reopens a Run.
        runtime={**runtime,"phase":"revision_open","dispatch_id":"","agent_status":"superseded","error_class":"","message":"Run 已退回修改；旧 Steward/dispatch 不再控制当前 Run。现在可直接登记 canonical 与代码修订。"}
    herdr_pi=runtime.get("runtime_kind")=="herdr_pi"
    dispatch_status=str((dispatch or {}).get("status") or "")
    terminal_dispatch=dispatch_status in {"failed","completed","cancelled","superseded"}
    runtime_dispatch_id=str(runtime.get("dispatch_id") or "")
    current_dispatch_id=str((dispatch or {}).get("dispatch_id") or "")
    controller_matches_attempt=not (herdr_pi and runtime_dispatch_id and current_dispatch_id and runtime_dispatch_id!=current_dispatch_id)
    # A live/working Pi process is no longer an active execution controller
    # once its dispatch is terminal.  Keeping it "active" hid the only valid
    # recovery action and left the UI saying LOCAL STEWARD STARTING forever.
    active=bool(controller_matches_attempt and not terminal_dispatch and runtime.get("phase") in _ACTIVE and ((agent_active if agent_active is not None else True) if herdr_pi else _pid_alive(runtime.get("pid"))))
    linked=bool(dispatch and run.get("execution_dispatch_id")==dispatch.get("dispatch_id") and run.get("execution_authorized_at")==dispatch.get("authorization_timestamp"))
    managed=(dispatch or {}).get("managed_execution") or {}
    observation=managed.get("status_observation") if isinstance(managed.get("status_observation"),dict) else {}
    running_evidence=bool(dispatch and dispatch.get("status")=="running" and managed.get("started_evidence")=="tmux_new_session_ok")
    remote_active=bool(active and linked and running_evidence)
    tmux_observed=bool(remote_active and observation.get("tmux_alive") is True and observation.get("observed_at"))
    canonical_stage_stale=bool(remote_active and str(run.get("workflow_stage") or run.get("status") or "")!="running")
    state_conflict=bool(running_evidence and not linked)
    ready=run.get("workflow_version")==2 and run.get("workflow_stage")=="ready_to_run" and experiments.run_review_status(run)=="approved" and bool(run.get("execution_authorized_at")) and bool(dispatch and dispatch.get("status") in {"queued","delivered"})
    expiry=experiments._parse_iso((dispatch or {}).get("lease_expires_at")); resumable=bool(dispatch and dispatch.get("status")=="running" and expiry and expiry<=dt.datetime.now() and not active)
    resume_waiting=bool(dispatch and dispatch.get("status")=="running" and expiry and expiry>dt.datetime.now() and not active)
    attention=bool(not revision_open and (state_conflict or runtime.get("phase")=="attention_required" or (dispatch or {}).get("status") in {"failed","blocked"} or (runtime.get("phase") in _ACTIVE and not active) or ((dispatch or {}).get("status")=="running" and not active)))
    recoverable=bool(herdr_pi and agent_active is False and dispatch and dispatch.get("status") in {"queued","delivered"})
    restartable=bool(dispatch_status=="failed" and run.get("workflow_version")==2 and run.get("workflow_stage")=="failed" and experiments.run_review_status(run)=="approved")
    effective_stage="running" if remote_active else str(run.get("workflow_stage") or run.get("status") or "")
    return {"run_id":run["id"],"experiment_id":str(run.get("experiment_id") or ""),"run_label":str(run.get("variant") or run["id"]),"workflow_stage":effective_stage,"revision_open":revision_open,"state_conflict":state_conflict,"canonical_stage_stale":canonical_stage_stale,"supervisor":_public_runtime(runtime),"supervisor_active":active,"remote_execution_active":remote_active,"remote_tmux_observed":tmux_observed,"remote_observed_at":str(observation.get("observed_at") or ""),"needs_attention":attention,"dispatch":dispatch,"can_start":ready,"can_resume":resumable,"can_restart":restartable,"resume_waiting":resume_waiting,"resume_available_at":str((dispatch or {}).get("lease_expires_at") or ""),"can_recover":recoverable,"execution_started":bool(dispatch and dispatch.get("status") in {"running","completed","failed"}),"lease_exposed":False,"prompt_used":False}


def _owned_agent_active(runtime,adapter=None):
    if runtime.get("runtime_kind")!="herdr_pi" or runtime.get("phase") not in _ACTIVE: return None,runtime
    name=str(runtime.get("internal_agent_name") or "")
    if not name: return False,runtime
    try:
        from survey_tool.v2.herdr_adapter import HerdrAdapter
        status=(adapter or HerdrAdapter()).owned_status(agent_name=name)
    except Exception:
        return None,runtime
    observed={**runtime,"agent_status":status}
    return status in {"working","starting","prompting"},observed


def _public_dispatches_readonly(root,experiments):
    """Read and scrub Outbox rows without expiring leases or writing state."""
    box=experiments._outbox_read(root)
    rows=[]
    for item in box["items"]:
        public=experiments._dispatch_public(item); managed=public.get("managed_execution")
        if isinstance(managed,dict):
            public["managed_execution"]={key:value for key,value in managed.items() if key not in {"launcher_path","ssh_host","tmux_session"}}
        rows.append(public)
    return rows


def steward_status(root,run_id,adapter=None):
    """Read local supervisor/Outbox state without SSH, token access, or writes."""
    from survey_tool import experiments
    root=pathlib.Path(root).resolve(); run_id=_safe_run_id(run_id)
    data=experiments.experiment_data(root); run=next((row for row in data["runs"] if row.get("id")==run_id),None)
    if not run: raise KeyError("Run not found")
    rows=_runtime_rows(root); runtime=rows["runs"].get(run_id,{}); agent_active,runtime=_owned_agent_active(runtime,adapter)
    items=_public_dispatches_readonly(root,experiments)
    dispatch=next((row for row in reversed(items) if row.get("run_id")==run_id),None)
    return _status_for_run(run,runtime,dispatch,experiments,agent_active)


def list_steward_statuses(root,adapter=None):
    """Only active or actionable supervisors; never list historical noise."""
    from survey_tool import experiments
    root=pathlib.Path(root).resolve(); data=experiments.experiment_data(root); runtimes=_runtime_rows(root)["runs"]
    dispatches=_public_dispatches_readonly(root,experiments); latest={}
    for item in dispatches: latest[str(item.get("run_id") or "")]=item
    rows=[]
    for run in data["runs"]:
        rid=str(run.get("id") or "")
        if rid not in runtimes: continue
        runtime=runtimes.get(rid,{}); agent_active,runtime=_owned_agent_active(runtime,adapter)
        status=_status_for_run(run,runtime,latest.get(rid),experiments,agent_active)
        if status["supervisor_active"] or status["needs_attention"]: rows.append(status)
    rows.sort(key=lambda item:str(item["supervisor"].get("updated_at") or item.get("run_id") or ""),reverse=True)
    phases={}
    for item in rows:
        phase=str(item["supervisor"].get("phase") or (item.get("dispatch") or {}).get("status") or item.get("workflow_stage") or "unknown"); phases[phase]=phases.get(phase,0)+1
    return {"items":rows,"summary":{"total":len(rows),"active":sum(bool(item["supervisor_active"]) for item in rows),"attention":sum(bool(item["needs_attention"]) for item in rows),"phases":phases},"remote_probe_performed":False,"lease_exposed":False}


def steward_console(root,run_id,runner=None,adapter=None):
    """Capture bounded output from the owned Herdr Pi (legacy tmux fallback)."""
    from survey_tool import experiments, managed_execution
    from survey_tool.v2.herdr_adapter import HerdrAdapter
    root=pathlib.Path(root).resolve(); run_id=_safe_run_id(run_id)
    run=next((row for row in experiments.experiment_data(root)["runs"] if row.get("id")==run_id),None)
    if not run: raise KeyError("Run not found")
    runtime=_runtime_rows(root)["runs"].get(run_id,{})
    if runtime.get("runtime_kind")=="herdr_pi":
        agent_name=str(runtime.get("internal_agent_name") or "")
        if not agent_name:
            return {"run_id":run_id,"available":False,"connected":False,"output":"","reason":"agent_not_attested","captured_at":"","truncated":False,"source":"herdr_pi"}
        try: observed=(adapter or HerdrAdapter()).read_owned(agent_name=agent_name,lines=400)
        except Exception:
            return {"run_id":run_id,"available":False,"connected":False,"output":"","reason":"herdr_agent_unavailable","captured_at":dt.datetime.now().isoformat(timespec="seconds"),"truncated":False,"source":"herdr_pi"}
        return {"run_id":run_id,"available":True,"connected":True,"output":observed.text,"reason":"","captured_at":dt.datetime.now().isoformat(timespec="seconds"),"truncated":observed.truncated,"source":"herdr_pi","agent_status":observed.agent_status}
    if not (runtime.get("phase") in _ACTIVE and _pid_alive(runtime.get("pid"))):
        return {"run_id":run_id,"available":False,"connected":False,"output":"","reason":"steward_not_active","captured_at":"","truncated":False}
    dispatch=next((row for row in reversed(experiments._outbox_read(root)["items"]) if row.get("run_id")==run_id and row.get("status")=="running"),None)
    managed=(dispatch or {}).get("managed_execution") or {}; host=str(managed.get("ssh_host") or ""); session=str(managed.get("tmux_session") or "")
    if not host or not session:
        return {"run_id":run_id,"available":False,"connected":False,"output":"","reason":"console_not_attested","captured_at":"","truncated":False}
    observed=managed_execution._ssh(runner or managed_execution._default_runner,host,["tmux","capture-pane","-p","-J","-S","-400","-t",session],timeout=10)
    if observed["returncode"]:
        return {"run_id":run_id,"available":False,"connected":False,"output":"","reason":"tmux_capture_failed","captured_at":dt.datetime.now().isoformat(timespec="seconds"),"truncated":False}
    raw=str(observed.get("stdout") or ""); truncated=len(raw.encode("utf-8"))>65536
    if truncated: raw=raw.encode("utf-8")[-65536:].decode("utf-8","replace")
    output=_ANSI_ESCAPE.sub("",raw); output="".join(ch for ch in output if ch in "\n\r\t" or ord(ch)>=32)
    return {"run_id":run_id,"available":True,"connected":True,"output":output,"reason":"","captured_at":dt.datetime.now().isoformat(timespec="seconds"),"truncated":truncated,"source":"owned_tmux_stdout"}


def _launch_process(root,run_id):
    argv=[sys.executable,"-m","survey_tool.steward_runtime","--project",str(pathlib.Path(root).resolve()),"--run",run_id]
    return subprocess.Popen(argv,cwd=str(pathlib.Path(__file__).resolve().parent.parent),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True,close_fds=True)


def prepare_steward_handoff(root,run_id,expected_updated):
    """Validate one Run and return a copy-only terminal command; start nothing."""
    from survey_tool import experiments
    root=pathlib.Path(root).resolve(); run_id=_safe_run_id(run_id)
    run=next((row for row in experiments.experiment_data(root)["runs"] if row.get("id")==run_id),None)
    if not run: raise KeyError("Run not found")
    if str(expected_updated or "")!=str(run.get("updated") or ""): raise RuntimeError("registry_version_conflict")
    if run.get("workflow_version")!=2: raise ValueError("只有 workflow-v2 Run 可交给 Steward")
    if experiments.run_review_status(run)!="approved" or not run.get("execution_authorized_at"):
        prepared=experiments.prepare_direct_steward_run(root,run_id,expected_updated,"human:web-v2")
        run=prepared["run"]
    with _START_LOCK:
        prior=_runtime_rows(root)["runs"].get(run_id,{})
        observed=steward_status(root,run_id)
        if observed.get("supervisor_active"):
            raise ValueError("Steward 已在运行，不能生成第二条启动命令")
        dispatch=observed.get("dispatch") or {}
        if observed.get("supervisor",{}).get("agent_status") in {"done","idle","blocked"} and prior.get("runtime_kind")=="herdr_pi" and dispatch.get("status") in {"claimed","acknowledged"}:
            experiments.recover_abandoned_steward_claim(root,str(dispatch.get("dispatch_id") or ""),"owned_agent_settled")
        if dispatch.get("status")=="running":
            if not observed.get("can_resume"): raise ValueError("旧 Pi 已中断，但 managed lease 尚未过期；过期后可重新接管同一 execution attempt")
            dispatch_id=str(dispatch.get("dispatch_id") or ""); message="旧 Pi 已中断；等待新 Pi reattach 同一 running execution attempt"
        elif dispatch.get("status")=="failed":
            restarted=experiments.restart_failed_run_execution(root,run_id,run.get("updated",""),"human:web-v2:auto-restart")
            run=restarted["run"]; fresh_dispatch=restarted["dispatch"]
            dispatch_id=str(fresh_dispatch.get("dispatch_id") or "")
            message="旧 failed attempt 已保留；等待新 Pi 调研仓库、补齐实现与运行参数后启动新 attempt"
        else:
            queued=experiments.ensure_authorization_dispatch(root,run_id,"steward_handoff")
            if not queued.get("queued") or queued.get("needs_attention"):
                raise ValueError(str(queued.get("error") or queued.get("dispatch",{}).get("last_error") or "执行授权已失效，请重新授权"))
            dispatch_id=str(queued.get("dispatch",{}).get("dispatch_id") or ""); message="等待新 Pi 读取批准上下文并调用 Steward 扩展"
        runtime_fields={"phase":"handoff_ready","runtime_kind":"herdr_pi","dispatch_id":dispatch_id,"error_class":"","finished_at":"","message":message}
        if prior.get("dispatch_id") and str(prior.get("dispatch_id"))!=dispatch_id:
            # A previous Herdr Pi may still have an open tab, but it no longer
            # controls this new attempt.  Do not let its name/pane make the new
            # dispatch appear active or prevent creation of a replacement Pi.
            runtime_fields.update({"internal_agent_name":"","internal_pane_id":"","agent_status":"superseded"})
        _update_runtime(root,run_id,**runtime_fields)
    plan=run.get("trial_plan") if isinstance(run.get("trial_plan"),dict) else None; plan_fingerprint=_trial_plan_fingerprint(plan)
    package_root=pathlib.Path(__file__).resolve().parent.parent
    argv=["env",f"PYTHONPATH={package_root}","HERDR_ENV=1",sys.executable,"-m","survey_tool.steward_runtime","--project",str(root),"--run",run_id,"--start-agent","--expected-updated",str(run.get("updated") or "")]
    if plan_fingerprint: argv.extend(["--expected-trial-plan",plan_fingerprint])
    return {"run_id":run_id,"handoff_command":shlex.join(argv),"trial_plan_fingerprint":plan_fingerprint,"trial_planning_mode":str((plan or {}).get("planning_mode") or ""),"trial_budget":int((plan or {}).get("trial_budget") or len((plan or {}).get("trials") or [])),"execution_started":False,"herdr_invoked":False,"lease_exposed":False,"prompt_used":False,"supervisor_phase":"handoff_ready"}


def force_restart_steward_handoff(root,run_id,expected_updated,actor="human:web-v2"):
    """Explicitly replace only the local Pi controller for a running attempt."""
    from survey_tool import experiments
    root=pathlib.Path(root).resolve(); run_id=_safe_run_id(run_id)
    forced=experiments.force_expire_managed_steward_lease(root,run_id,expected_updated,actor)
    _update_runtime(root,run_id,phase="handoff_ready",runtime_kind="herdr_pi",dispatch_id=forced["dispatch"]["dispatch_id"],internal_agent_name="",internal_pane_id="",agent_status="",error_class="",finished_at="",message="人工已撤销旧 Pi 的控制 lease；等待新 Pi reattach 同一远端 execution attempt")
    package_root=pathlib.Path(__file__).resolve().parent.parent
    argv=["env",f"PYTHONPATH={package_root}","HERDR_ENV=1",sys.executable,"-m","survey_tool.steward_runtime","--project",str(root),"--run",run_id,"--start-agent","--expected-updated",str(expected_updated or "")]
    return {"run_id":run_id,"dispatch":forced["dispatch"],"handoff_command":shlex.join(argv),"execution_started":False,"execution_restarted":False,"herdr_invoked":False,"lease_exposed":False,"prompt_used":False,"supervisor_phase":"handoff_ready"}


def start_steward_background(root,run_id,expected_updated,launcher=_launch_process,capability_getter=None,expected_trial_plan=""):
    """Create one visible Herdr Pi Steward for an approved/authorized Run."""
    import server
    from survey_tool import experiments
    from survey_tool.v2.capabilities import herdr_capability
    from survey_tool.v2.herdr_adapter import HerdrAdapter, build_task_envelope
    root=pathlib.Path(root).resolve(); run_id=_safe_run_id(run_id); data=experiments.experiment_data(root)
    run=next((row for row in data["runs"] if row.get("id")==run_id),None)
    if not run: raise KeyError("Run not found")
    if str(expected_updated or "")!=str(run.get("updated") or ""): raise RuntimeError("registry_version_conflict")
    if expected_trial_plan:
        if not re.fullmatch(r"sha256:[0-9a-f]{64}",str(expected_trial_plan)) or _trial_plan_fingerprint(run.get("trial_plan"))!=str(expected_trial_plan):
            raise RuntimeError("trial_plan_version_conflict")
    if run.get("workflow_version")!=2 or experiments.run_review_status(run)!="approved" or not run.get("execution_authorized_at"):
        raise ValueError("Run 必须是 workflow v2、approved 且已单独授权")
    with _START_LOCK:
        observed=steward_status(root,run_id)
        if observed.get("supervisor_active"):
            return {**observed,"worker_started":False,"already_running":True}
        _update_runtime(root,run_id,phase="preparing",started_at=server.now_iso(),finished_at="",error_class="",message="已明确交给 Steward，正在检查执行队列")
        try:
            resume=bool(observed.get("can_resume") and (observed.get("dispatch") or {}).get("status")=="running")
            if resume:
                dispatch_id=observed["dispatch"]["dispatch_id"]; dispatch_status="running"
            elif run.get("workflow_stage")=="ready_to_run":
                queued=experiments.ensure_authorization_dispatch(root,run_id,"steward_background")
                if not queued.get("queued") or queued.get("needs_attention"): raise ValueError(str(queued.get("error") or queued.get("dispatch",{}).get("last_error") or "执行队列未就绪"))
                dispatch_id=queued["dispatch"]["dispatch_id"]; dispatch_status=str(queued["dispatch"].get("status") or "queued")
            else: raise ValueError("Run 仅可从 ready_to_run 启动，或在 running lease 过期后恢复监督")
        except Exception as exc:
            _update_runtime(root,run_id,phase="attention_required",finished_at=server.now_iso(),error_class=type(exc).__name__,message=str(exc)[:300])
            raise
        capability=(capability_getter or herdr_capability)()
        if os.environ.get("HERDR_ENV")!="1" or capability.get("managed") is not True or capability.get("cli_available") is not True or capability.get("pi_supported") is not True:
            message="Survey Tool server 必须从 Herdr pane 内启动，且 Herdr 必须支持 pi"
            _update_runtime(root,run_id,phase="attention_required",finished_at=server.now_iso(),error_class="herdr_pi_unavailable",message=message)
            raise ValueError(message)
        agent_name=_new_steward_agent_name(run_id,run.get("execution_authorized_at"),dispatch_id)
        trial_plan=run.get("trial_plan") if isinstance(run.get("trial_plan"),dict) else None
        if trial_plan:
            mode="AI 自主规划" if trial_plan.get("planning_mode")=="ai_planned" else "参数矩阵"
            count=int(trial_plan.get("trial_budget") or len(trial_plan.get("trials") or [])); goal=str(trial_plan.get("request") or run.get("purpose") or "").strip()
            summary=f"参数批量实验（{mode}，约 {count} Trials）：{goal}"[:500]
        else: summary=(str(run.get("purpose") or run.get("research_question") or run.get("variant") or "执行并监督已批准 Run").strip())[:500]
        exp=next((row for row in data.get("experiments",[]) if row.get("id")==run.get("experiment_id")),{})
        workspace=next((row for row in data.get("workspaces",[]) if row.get("id")==str(run.get("workspace_id") or exp.get("workspace_id") or "")),{})
        bound_server=next((row for row in data.get("servers",[]) if row.get("id")==workspace.get("server_id")),{})
        remote_repo=str(workspace.get("remote_repo") or ""); ssh_host=str(bound_server.get("ssh_host") or "")
        context={"experiment":{"id":exp.get("id"),"title":str(exp.get("title") or "")[:200],"objective":str(exp.get("objective") or "")[:500]},"run":{"id":run_id,"research_question":str(run.get("research_question") or "")[:500],"purpose":str(run.get("purpose") or "")[:500],"metric_plan":str(run.get("metric_plan") or "")[:500],"command":str(run.get("command") or "")[:1000],"implementation_ref":run.get("implementation_ref"),"trial_plan":trial_plan},"workspace":{"id":workspace.get("id"),"server_id":workspace.get("server_id"),"ssh_host":ssh_host,"remote_repo":remote_repo[:500]}}
        remote_workspace={"ssh_host":ssh_host,"remote_repo":remote_repo,"tmux_session":f"st-{agent_name}","code_map_summary":"请先只读核验当前仓库入口；不要扫描无关目录"} if not resume and ssh_host and remote_repo.startswith("/") else None
        envelope=build_task_envelope(target_type="run",target_id=run_id,target_title=str(run.get("variant") or run_id),task_type="run_implementation",task_summary=summary,reasoning_effort="medium",max_turns=20,run_state={"experiment_id":run.get("experiment_id"),"workflow_stage":"running" if resume else run.get("workflow_stage"),"review_status":experiments.run_review_status(run),"execution_authorized":True,"dispatch_status":dispatch_status,"resume_dispatch_id":dispatch_id if resume else ""},run_context=context,remote_workspace=remote_workspace)
        active_adapter=HerdrAdapter() if launcher is _launch_process else launcher
        _update_runtime(root,run_id,phase="agent_starting",runtime_kind="herdr_pi",dispatch_id=dispatch_id,message="正在 Herdr 新标签中创建专属 Pi Steward")
        try:
            display=_steward_display(run,agent_name,trial_plan)
            if remote_workspace and hasattr(active_adapter,"start_remote_owned"):
                attestation=active_adapter.start_remote_owned(local_project_root=str(root),ssh_host=ssh_host,remote_repo=remote_repo,**display)
            else:
                attestation=active_adapter.start_owned(project_root=str(root),agent_kind="pi",topology="new_tab",**display)
            if attestation.agent_name!=agent_name: raise ValueError("Herdr Pi ownership attestation mismatch")
            _update_runtime(root,run_id,phase="agent_starting",runtime_kind="herdr_pi",dispatch_id=dispatch_id,internal_agent_name=attestation.agent_name,internal_pane_id=attestation.pane_id,message="Pi Steward 已创建，正在提交受控 Run 上下文")
            turn=active_adapter.prompt_owned_async(agent_name=attestation.agent_name,envelope=envelope)
        except Exception as exc:
            failure_class=getattr(exc,"failure_class","") or type(exc).__name__
            _update_runtime(root,run_id,phase="attention_required",runtime_kind="herdr_pi",finished_at=server.now_iso(),error_class=failure_class,message=str(exc)[:300])
            raise ValueError(f"Herdr Pi Steward 创建或 Prompt 提交失败：{failure_class}") from exc
        _update_runtime(root,run_id,phase="agent_running",runtime_kind="herdr_pi",dispatch_id=dispatch_id,internal_agent_name=attestation.agent_name,internal_pane_id=attestation.pane_id,agent_status=turn.agent_status,message="专属 Pi Steward 已接收 Run；将通过受控工具启动、监控、修复并收集结果")
        return {**steward_status(root,run_id),"worker_started":True,"already_running":False,"agent_created":True}


def run_supervisor(root,run_id,*,poll_seconds=30,max_cycles=None,sleep=time.sleep):
    """Claim, start and supervise exactly one Run. Raw lease stays in this process."""
    import server
    from survey_tool import experiments, managed_execution
    root=pathlib.Path(root).resolve(); run_id=_safe_run_id(run_id); consumer=f"steward:{run_id}:{uuid.uuid4().hex[:10]}"
    token=""; dispatch_id=""; running=False
    try:
        _update_runtime(root,run_id,phase="claiming",pid=os.getpid(),message="正在领取该 Run 的单次执行授权")
        current=next((row for row in experiments.experiment_data(root)["runs"] if row.get("id")==run_id),None)
        if current and current.get("workflow_stage")=="running":
            item=next((row for row in experiments.execution_outbox_public(root)["execution_outbox"]["items"] if row.get("run_id")==run_id and row.get("status")=="running"),None)
            if not item: raise ValueError("running Run 缺少可恢复的 managed dispatch")
            attached=experiments.reattach_managed_execution(root,item["dispatch_id"],consumer); token=attached["lease_token"]; dispatch_id=item["dispatch_id"]; running=True
            _update_runtime(root,run_id,phase="running",dispatch_id=dispatch_id,message="已轮换 lease 并恢复后台监督")
        else:
            claim=experiments.claim_run_execution(root,run_id,consumer)
            if not claim.get("claimed"): raise ValueError("该 Run 没有可领取的已授权执行")
            token=claim["lease_token"]; dispatch=claim["task"]["dispatch"]; dispatch_id=dispatch["dispatch_id"]
            experiments._leased_transition(root,dispatch_id,token,consumer,"acknowledge",{"executor_kind":"steward"})
            _update_runtime(root,run_id,phase="starting",dispatch_id=dispatch_id,message="正在执行安全预检并启动远端 tmux")
            managed_execution.managed_execution_start(root,dispatch_id,token,consumer); running=True
        _update_runtime(root,run_id,phase="running",message="Steward 正在后台监控；未使用 AI Prompt")
        cycles=0
        while max_cycles is None or cycles<max_cycles:
            cycles+=1; status=managed_execution.managed_execution_status(root,dispatch_id,token,consumer,heartbeat=True)
            if status.get("completion_candidate"):
                _update_runtime(root,run_id,phase="collecting",message="进程已结束，正在核验指标与产物")
                try: managed_execution.managed_execution_complete(root,dispatch_id,token,consumer)
                except ValueError as exc:
                    if "not yet stable" not in str(exc): raise
                    sleep(max(1,min(int(poll_seconds),30))); managed_execution.managed_execution_complete(root,dispatch_id,token,consumer)
                _update_runtime(root,run_id,phase="analysis_pending",finished_at=server.now_iso(),message="运行证据已收集，等待人工科研分析")
                return {"ok":True,"run_id":run_id,"phase":"analysis_pending"}
            if not status.get("tmux_alive"):
                managed_execution.managed_execution_fail(root,dispatch_id,token,consumer,"environment","远端 tmux 已结束但缺少受控完成证据",False)
                _update_runtime(root,run_id,phase="attention_required",finished_at=server.now_iso(),error_class="missing_completion_evidence",message="远端进程结束但完成证据不完整")
                return {"ok":False,"run_id":run_id,"phase":"attention_required"}
            sleep(max(1,min(int(poll_seconds),300)))
        _update_runtime(root,run_id,phase="running",message="测试监督周期结束；真实后台监督仍应持续运行")
        return {"ok":True,"run_id":run_id,"phase":"running"}
    except Exception as exc:
        if token and dispatch_id and not running:
            try: experiments.release_execution(root,dispatch_id,token,consumer,"steward start failed")
            except Exception: pass
        _update_runtime(root,run_id,phase="attention_required",finished_at=server.now_iso(),error_class=type(exc).__name__,message=str(exc)[:300])
        return {"ok":False,"run_id":run_id,"phase":"attention_required","error_class":type(exc).__name__}


def main(argv=None):
    parser=argparse.ArgumentParser(description="Survey Tool prompt-free Run Steward")
    parser.add_argument("--project",required=True); parser.add_argument("--run",required=True)
    parser.add_argument("--start-agent",action="store_true"); parser.add_argument("--expected-updated",default=""); parser.add_argument("--expected-trial-plan",default="")
    args=parser.parse_args(argv)
    if args.start_agent:
        result=start_steward_background(pathlib.Path(args.project),args.run,args.expected_updated,expected_trial_plan=args.expected_trial_plan)
        print(json.dumps({key:value for key,value in result.items() if key not in {"dispatch"}},ensure_ascii=False,default=str))
        return 0
    result=run_supervisor(pathlib.Path(args.project),args.run)
    return 0 if result.get("ok") else 1


if __name__=="__main__": raise SystemExit(main())
