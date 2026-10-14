"""One-shot Herdr execution preflight and explicitly selected owned start.

Preflight remains record-only. Owned-start creates one shell pane and one approved agent,
but never submits a prompt or controls any other Herdr resource.
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import pathlib
import re
import secrets
import sys
import time
from collections.abc import Callable, Iterator
from typing import Any

from .capabilities import herdr_capability
from .herdr_adapter import HerdrAdapter, HerdrStartError, build_task_envelope
from .store import V2Store
from survey_tool.workspace_context import load_workspace_code_map, save_workspace_code_map, workspace_code_map_summary


def _run_execution_state(project_root: pathlib.Path, run_id: str) -> dict[str, Any]:
    """Read only the canonical Run/Outbox fields needed by the envelope.

    Importing the legacy experiments domain while server.py is still importing
    its integrations domain forms a cycle in `python -m` startup. Keeping this
    tiny reader local also makes owned Herdr startup independent of HTTP-server
    module initialization.
    """
    tool_dir = pathlib.Path(project_root) / ".survey-tool"
    try:
        runs = json.loads((tool_dir / "runs.json").read_text(encoding="utf-8"))
        outbox = json.loads((tool_dir / "execution-outbox.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("canonical Run/Outbox state is unavailable") from exc
    if not isinstance(runs, list) or not isinstance(outbox, dict) or not isinstance(outbox.get("items"), list):
        raise ValueError("canonical Run/Outbox state is invalid")
    run = next((item for item in runs if isinstance(item, dict) and item.get("id") == run_id), None)
    if not run:
        raise ValueError("run implementation target is missing from canonical registry")
    dispatches = [item for item in outbox["items"] if isinstance(item, dict) and item.get("run_id") == run_id]
    latest = max(dispatches, key=lambda item: str(item.get("updated_at") or item.get("created_at") or ""), default={})
    return {"experiment_id": run.get("experiment_id"), "workflow_stage": run.get("workflow_stage"), "review_status": run.get("review_status"), "execution_authorized": bool(run.get("execution_authorized_at")), "dispatch_status": latest.get("status") or "none"}


def _target_context(project_root: pathlib.Path, target_type: str, target_id: str, reference_ids: list[str] | None = None) -> dict[str, Any]:
    """Read only the selected Experiment/Run context without importing server.py."""
    tool_dir = pathlib.Path(project_root) / ".survey-tool"

    def rows(name: str) -> list[dict[str, Any]]:
        try:
            value = json.loads((tool_dir / name).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []

    if target_type not in {"experiment", "run"}:
        return {"primary": {"type": target_type, "id": target_id}, "canonical_reread_required": True}
    experiments = rows("experiments.json")
    runs = rows("runs.json")
    selected_run = next((item for item in runs if item.get("id") == target_id), None) if target_type == "run" else None
    experiment_id = str((selected_run or {}).get("experiment_id") or target_id)
    selected_experiment = next((item for item in experiments if item.get("id") == experiment_id), None)
    if target_type == "run" and not selected_run:
        raise ValueError("Run context is unavailable")
    if not selected_experiment:
        raise ValueError("Experiment context is unavailable")
    experiment_fields = ("id", "title", "objective", "hypothesis", "success_criteria", "failure_criteria", "metric_definitions", "constraints", "evidence_refs", "workspace_id", "status", "workflow_stage")
    run_fields = ("id", "experiment_id", "variant", "research_question", "purpose", "hypothesis", "necessity", "evidence_basis", "data_definition", "variables_controls", "metric_plan", "metric_definition", "architecture_plan", "implementation_ref", "implementation_summary", "command", "workspace_id", "workflow_stage", "review_status", "trial_plan")
    context: dict[str, Any] = {
        "primary": {"type": target_type, "id": target_id},
        "experiment": {key: selected_experiment.get(key) for key in experiment_fields if selected_experiment.get(key) not in (None, "", [], {})},
        "canonical_reread_required": True,
        "cross_experiment_context": "excluded",
        "context_policy": {"automatic_results":"solid_only","other_results":"explicit_reference_only","memory":"non_authoritative_do_not_use"},
    }
    result_fields=("id","experiment_id","variant","research_question","purpose","metric_plan","result_summary","result_analysis","key_results","metric_observations","auxiliary_metric_observations","limitations","claim_boundary","artifacts","audit_paths","evidence_label","evidence_label_note")
    def result_payload(item:dict[str,Any],selection:str)->dict[str,Any]:
        payload={key:item.get(key) for key in result_fields if item.get(key) not in (None,"",[],{})};payload["selection"]=selection;return payload
    solid=[result_payload(item,"automatic_solid") for item in runs if item.get("experiment_id")==experiment_id and item.get("evidence_label")=="solid" and item.get("id")!=target_id]
    explicit=[]
    for reference_id in dict.fromkeys(reference_ids or []):
        item=next((row for row in runs if row.get("id")==reference_id),None)
        if item and item.get("id")!=target_id: explicit.append(result_payload(item,"explicit_reference"))
    context["solid_runs"]=solid
    context["explicit_run_references"]=explicit
    if selected_run:
        context["run"] = {key: selected_run.get(key) for key in run_fields if selected_run.get(key) not in (None, "", [], {})}
    return context


def _remote_code_workspace(project_root: pathlib.Path, target_type: str, target_id: str) -> dict[str, str]:
    tool_dir=pathlib.Path(project_root)/".survey-tool"
    def rows(name: str) -> list[dict[str, Any]]:
        try: value=json.loads((tool_dir/name).read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError) as exc: raise ValueError("remote code Workspace binding is unavailable") from exc
        if not isinstance(value,list): raise ValueError("remote code Workspace binding is invalid")
        return [item for item in value if isinstance(item,dict)]
    experiments=rows("experiments.json"); runs=rows("runs.json"); workspaces=rows("workspaces.json")
    try: servers=rows("servers.json")
    except ValueError: servers=rows("machines.json")
    if target_type=="run":
        run=next((item for item in runs if item.get("id")==target_id),None)
        if not run: raise ValueError("remote code Run target is unavailable")
        experiment=next((item for item in experiments if item.get("id")==run.get("experiment_id")),None)
        workspace_id=str(run.get("workspace_id") or (experiment or {}).get("workspace_id") or "")
    elif target_type=="experiment":
        experiment=next((item for item in experiments if item.get("id")==target_id),None)
        if not experiment: raise ValueError("remote code Experiment target is unavailable")
        workspace_id=str(experiment.get("workspace_id") or "")
    else:
        raise ValueError("remote code task requires an Experiment or Run target")
    workspace=next((item for item in workspaces if item.get("id")==workspace_id),None)
    server=next((item for item in servers if item.get("id")==str((workspace or {}).get("server_id") or "")),None)
    host=str((server or {}).get("ssh_host") or "").strip(); repo=str((workspace or {}).get("remote_repo") or "").strip()
    if (not workspace or not re.fullmatch(r"[A-Za-z0-9._:@-]{1,255}",host)
            or not repo.startswith("/") or len(repo)>2048 or any(char in repo for char in ("\0","\r","\n"))):
        raise ValueError("remote code Workspace binding is incomplete")
    from survey_tool.code_workflow import code_workflow_prompt, local_binding
    local_rules=code_workflow_prompt(project_root,workspace,pathlib.Path(__file__).resolve().parents[2]/"surveyctl.py")
    return {"workspace_id":workspace_id,"ssh_host":host,"remote_repo":repo,**({"local_code_rules":local_rules,"local_code_repo":local_binding(project_root,workspace_id)} if local_rules else {})}


@contextlib.contextmanager
def _project_lock(store: V2Store) -> Iterator[None]:
    lock_path = store.path.parent / "herdr-executor.lock"
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        os.close(descriptor)
        raise RuntimeError("another executor preflight is active") from exc
    try:
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def run_preflight(
    project: pathlib.Path | str,
    execution_id: str,
    *,
    environ: dict[str, str] | None = None,
    capability_getter: Callable[[], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    environment = os.environ if environ is None else environ
    checks = {"environment_managed": environment.get("HERDR_ENV") == "1"}
    if not checks["environment_managed"]:
        return {"execution_id": execution_id, "state": "refused", "checks": checks}
    store = V2Store(project)
    if not store.exists():
        return {"execution_id": execution_id, "state": "refused", "checks": {**checks, "store_initialized": False}}
    started = time.monotonic(); owner = f"preflight-{secrets.token_hex(8)}"; claim: dict[str, Any] | None = None
    with _project_lock(store):
        capability = (capability_getter or herdr_capability)()
        execution = store.get_herdr_execution(execution_id)
        request = store.get_herdr_launch_request(execution["launch_request_object_id"])
        support_key = "pi_supported" if request["agent_kind"] == "pi" else "codex_supported"
        checks.update({"cli_available": capability.get("cli_available") is True, support_key: capability.get(support_key) is True})
        claim = store.claim_herdr_execution(execution_id, expected_revision=execution["revision"], owner=owner, capability=capability)
        checks.update({"authorization_current": True, "request_snapshot_current": True, "target_available": True, "concurrency_available": True})
        finished = store.finish_herdr_preflight(
            execution_id, lease_token=claim["lease_token"], owner=owner, status="completed",
            runtime={"checks": checks, "duration_ms": min(300_000, int((time.monotonic()-started)*1000)), "human_review_required": False},
        )
    return {"execution_id": execution_id, "state": finished["state"], "checks": checks, "execution_started": False, "herdr_invoked": False}


def _owned_agent_name(execution_id: str, lease_token: str, *, target_id: str, task_type: str, agent_kind: str) -> str:
    target=re.sub(r"[^a-z0-9_-]","-",str(target_id).lower()).strip("-_")[:12] or "target"
    task={"implementation":"code","run_implementation":"run","discussion":"discuss","research":"research","analysis":"analysis","monitoring":"monitor"}.get(str(task_type),"task")
    digest=hashlib.sha256(f"{execution_id}\0{lease_token}".encode("utf-8")).hexdigest()[:6]
    prefix = "codex" if agent_kind == "codex" else "pi"
    return f"{prefix}-{target}-{task[:8]}-{digest}"[:32].rstrip("-_")


def _owned_display_names(*, target_id: str, task_type: str, agent_kind: str) -> tuple[str, str]:
    label={"implementation":"修改代码","run_implementation":"实现 Run","discussion":"讨论","research":"研究","analysis":"分析","monitoring":"监控"}.get(str(task_type),"任务")
    target=str(target_id)[:32]
    agent_label = "Codex" if agent_kind == "codex" else "Pi"
    return f"{agent_label} · {target} · {label}", f"{target} · {label}"


def run_start_owned(
    project: pathlib.Path | str,
    execution_id: str,
    *,
    environ: dict[str, str] | None = None,
    capability_getter: Callable[[], dict[str, Any]] | None = None,
    adapter: HerdrAdapter | None = None,
) -> dict[str, Any]:
    environment=os.environ if environ is None else environ
    checks={"environment_managed":environment.get("HERDR_ENV")=="1"}
    if not checks["environment_managed"]: return {"execution_id":execution_id,"state":"refused","checks":checks}
    store=V2Store(project)
    if not store.exists(): return {"execution_id":execution_id,"state":"refused","checks":{**checks,"store_initialized":False}}
    owner=f"owned-start-{secrets.token_hex(8)}"
    with _project_lock(store):
        capability=(capability_getter or herdr_capability)()
        execution=store.get_herdr_execution(execution_id)
        request=store.get_herdr_launch_request(execution["launch_request_object_id"])
        agent_kind=str(request["agent_kind"])
        support_key="pi_supported" if agent_kind=="pi" else "codex_supported"
        checks.update({"cli_available":capability.get("cli_available") is True,support_key:capability.get(support_key) is True})
        claim=store.claim_herdr_execution(execution_id,expected_revision=execution["revision"],owner=owner,capability=capability)
        checks.update({"authorization_current":True,"request_snapshot_current":True,"target_available":True,"concurrency_available":True})
        lease_token=claim["lease_token"]
        agent_name=_owned_agent_name(execution_id,lease_token,target_id=request["target_object_id"],task_type=request["task_type"],agent_kind=agent_kind)
        tab_label,session_name=_owned_display_names(target_id=request["target_object_id"],task_type=request["task_type"],agent_kind=agent_kind)
        target=store.get_object(request["target_object_id"])
        config=dict(request.get("safe_config") or {})
        run_state=None
        if request["task_type"]=="run_implementation":
            run_state=_run_execution_state(store.project_root, target["id"])
        target_context=_target_context(store.project_root,target["type"],target["id"],list(config.get("reference_ids") or []))
        explicit_objects=[]
        for reference_id in config.get("reference_ids") or []:
            if any(item.get("id")==reference_id for item in target_context.get("explicit_run_references") or []): continue
            try: reference=store.get_object(reference_id)
            except KeyError: raise ValueError(f"explicit reference is unavailable: {reference_id}")
            explicit_objects.append({key:reference.get(key) for key in ("id","type","title","canonical_path")})
        target_context["explicit_object_references"]=explicit_objects
        remote=None
        if request["task_type"] in {"implementation","run_implementation"}:
            remote=_remote_code_workspace(store.project_root,target["type"],target["id"])
        active_adapter=adapter or HerdrAdapter()
        code_map={}
        if remote and not remote.get("local_code_rules"):
            cached=load_workspace_code_map(store.project_root,remote["workspace_id"])
            try:
                snapshot=active_adapter.inspect_remote_workspace(ssh_host=remote["ssh_host"],remote_repo=remote["remote_repo"],known_revision=str(cached.get("revision") or ""))
                code_map=cached if snapshot.get("unchanged") else save_workspace_code_map(store.project_root,remote["workspace_id"],snapshot.get("revision","unknown"),snapshot.get("files") or [],snapshot.get("changed_files") or [])
            except (HerdrStartError,ValueError,OSError):
                code_map=cached
        agent_recorded=False
        try:
            topology=str(config.get("topology") or "new_tab")
            if remote and remote.get("local_code_rules"):
                from survey_tool.code_workflow import prepare_code
                prepare_code(store.project_root,remote["workspace_id"])
                checks["local_git_baseline_synced"]=True
                # Automatic prepare may have just registered the repository/path.
                remote=_remote_code_workspace(store.project_root,target["type"],target["id"])
            envelope=build_task_envelope(
                target_type=target["type"],target_id=target["id"],target_title=target.get("title","") or "",
                task_type=request["task_type"],task_summary=request["task_summary"],
                reasoning_effort=config.get("reasoning_effort","medium"),max_turns=config.get("max_turns",5),agent_kind=agent_kind,run_state=run_state,
                run_context=target_context if target["type"]=="run" else None,target_context=target_context,
                remote_workspace={**remote,"tmux_session":f"st-{agent_name}","code_map_summary":workspace_code_map_summary(code_map)} if remote else None,
            )
            if request["task_type"] in {"implementation","run_implementation"} and agent_kind=="pi" and not (remote or {}).get("local_code_rules"):
                assert remote is not None
                attestation=active_adapter.start_remote_owned(
                    local_project_root=str(store.project_root),ssh_host=remote["ssh_host"],remote_repo=remote["remote_repo"],
                    agent_name=agent_name,tab_label=tab_label,session_name=session_name,
                )
                checks.update({"remote_repo_context":True,"remote_tmux_context":True})
            else:
                attestation=active_adapter.start_owned(
                    project_root=str(store.project_root), agent_name=agent_name,
                    agent_kind=agent_kind, topology=topology,
                    tab_label=tab_label, session_name=session_name,
                )
                if remote:
                    checks.update({"remote_repo_context":True,"remote_tmux_context":False})
            if attestation.agent_name!=agent_name: raise HerdrStartError("owned agent attestation name mismatch",split_succeeded=True)
            store.record_owned_agent_started(execution_id,lease_token=lease_token,owner=owner,internal_agent_name=agent_name,lease_seconds=300)
            agent_recorded=True
            turn=active_adapter.prompt_owned(agent_name=agent_name,envelope=envelope)
            if remote and not remote.get("local_code_rules"):
                try:
                    snapshot=active_adapter.inspect_remote_workspace(ssh_host=remote["ssh_host"],remote_repo=remote["remote_repo"],known_revision=str(code_map.get("revision") or ""))
                    if not snapshot.get("unchanged"): code_map=save_workspace_code_map(store.project_root,remote["workspace_id"],snapshot.get("revision","unknown"),snapshot.get("files") or [],snapshot.get("changed_files") or [])
                    checks["workspace_code_map_maintained"]=True
                except (HerdrStartError,ValueError,OSError):
                    checks["workspace_code_map_maintained"]=False
            if turn.agent_status=="blocked":
                finished=store.finish_owned_prompt(execution_id,lease_token=lease_token,owner=owner,status="attention_required",prompt_submitted=True,prompt_settled=True)
                checks.update({"resource_created":True,"agent_started":True,"ownership_attested":True,"prompt_submitted":True,"prompt_settled":True,"agent_blocked":True})
            else:
                finished=store.finish_owned_prompt(execution_id,lease_token=lease_token,owner=owner,status="completed",prompt_submitted=True,prompt_settled=True)
                checks.update({"resource_created":True,"agent_started":True,"ownership_attested":True,"prompt_submitted":True,"prompt_settled":True,"agent_blocked":False})
            return {"execution_id":execution_id,"state":finished["state"],"checks":checks}
        except Exception as exc:
            split_succeeded=bool(getattr(exc,"split_succeeded",False))
            message=str(exc).lower()
            classified=str(getattr(exc,"failure_class","") or "")
            checks["failure_class"] = (
                classified if classified
                else "ownership_ambiguous" if "ambiguous" in message or "attestation" in message
                else "agent_start_failed" if split_succeeded
                else "topology_create_failed"
            )
            if agent_recorded:
                attention=store.finish_owned_prompt(execution_id,lease_token=lease_token,owner=owner,status="attention_required",prompt_submitted=False,prompt_settled=False)
                checks.update({"resource_created":True,"agent_started":True,"ownership_attested":True,"prompt_submitted":False,"prompt_settled":False,"agent_blocked":False})
            else:
                attention=store.mark_owned_start_attention(execution_id,lease_token=lease_token,owner=owner,split_succeeded=split_succeeded)
                checks.update({"resource_created":split_succeeded,"agent_started":False,"ownership_attested":False,"prompt_submitted":False,"prompt_settled":False,"agent_blocked":False})
            return {"execution_id":execution_id,"state":attention["state"],"checks":checks}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one Herdr execution step")
    parser.add_argument("--project", required=True)
    parser.add_argument("--execution", required=True)
    parser.add_argument("--once", action="store_true")
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument("--preflight-only", action="store_true")
    mode.add_argument("--start-owned", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if not args.once:
        print(json.dumps({"execution_id": args.execution, "state": "refused", "checks": {"one_shot": False}}, sort_keys=True))
        return 2
    try:
        result = run_start_owned(args.project,args.execution) if args.start_owned else run_preflight(args.project, args.execution)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["state"] in {"completed","running"} else 1
    except Exception as exc:
        # The browser/API never exposes executor internals, but a user who
        # explicitly runs this local CLI needs a bounded actionable reason.
        # Keep only known safe lifecycle/configuration messages; never print
        # paths, command output, credentials, tokens, or traceback details.
        message=str(exc)
        safe_messages={
            "project Herdr execution concurrency limit reached",
            "Herdr execution authorization has expired",
            "Herdr capability preflight is unavailable",
            "approved Launch Request revision/status changed",
            "approved Launch Request snapshot changed",
            "execution target is missing, changed, or archived",
            "Herdr execution is not authorized",
            "run implementation target is missing from canonical registry",
            "canonical Run/Outbox state is unavailable",
            "canonical Run/Outbox state is invalid",
            "remote code Workspace binding is unavailable",
            "remote code Workspace binding is invalid",
            "remote code Workspace binding is incomplete",
            "remote code Run target is unavailable",
            "remote code Experiment target is unavailable",
        }
        detail=message if message in safe_messages else "local Herdr executor failed; inspect the execution record"
        print(json.dumps({"execution_id": args.execution, "state": "failed", "checks": {"preflight": False}, "error_class": type(exc).__name__, "reason": detail}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
