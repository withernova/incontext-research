"""Explicit local development, safe baseline sync, and commit-pinned deployment.

No push, clone, training, or network call occurs at import or binding save time.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import shlex
import socket
import subprocess
import sys

from survey_tool.code_git_worker import github_identity


def machine_key():
    return hashlib.sha256((socket.gethostname() + "|" + str(pathlib.Path.home())).encode()).hexdigest()[:24]


def validate_binding(value):
    if not isinstance(value, dict) or set(value) - {"mode", "repository_url", "branch", "storage", "transport"}:
        raise ValueError("code_development contains unsupported fields")
    if value.get("mode") == "auto" or value.get("mode") == "remote":
        return {"mode": value["mode"]}
    if value.get("mode") != "local-git":
        raise ValueError("code_development.mode must be auto, remote or local-git")
    url = str(value.get("repository_url") or "").strip().removesuffix(".git")
    if not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", url):
        raise ValueError("repository_url must be a credential-free GitHub HTTPS URL")
    github_identity(url)
    branch = str(value.get("branch") or "")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,159}", branch) or any(x in branch for x in ("..", "//", "@{")) or branch.endswith(("/", ".", ".lock")):
        raise ValueError("branch must be an explicit safe Git branch (not a guessed default)")
    storage=value.get("storage","external")
    if not isinstance(storage,str) or storage not in {"project","external"}:
        raise ValueError("code_development.storage must be project or external")
    transport = value.get("transport", "https")
    if not isinstance(transport, str) or transport not in {"https", "ssh"}:
        raise ValueError("code_development.transport must be https or ssh")
    return {"mode": "local-git", "repository_url": url, "branch": branch, **({"storage":storage} if "storage" in value else {}), **({"transport":transport} if "transport" in value else {})}


def validate_local_path(value):
    if not isinstance(value, str) or not value.startswith("/") or any(ord(c) < 32 for c in value):
        raise ValueError("local_code_repo must be an absolute path on the tool host")
    if ".publish" in pathlib.Path(value).parts or value == "/":
        raise ValueError("local_code_repo cannot be a publish snapshot or filesystem root")
    return value


PROJECT_CODE_DIRECTORY="code-repositories"


def project_repo_path(root, wid, binding):
    """Derive a relocatable project-owned path; never follow directory aliases."""
    binding=validate_binding(binding)
    name=binding.get("repository_url","").rsplit("/",1)[-1]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}",str(wid)) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,159}",name):
        raise ValueError("unsafe Workspace identity or repository directory name")
    base=pathlib.Path(root).resolve()
    if ".publish" in base.parts:
        raise ValueError("project code cannot be stored in a publish snapshot")
    target=base/PROJECT_CODE_DIRECTORY/str(wid)/name
    for component in (base/PROJECT_CODE_DIRECTORY,target.parent,target):
        if component.is_symlink():
            raise ValueError("project code directory must not be a symlink")
    return str(target)


def local_binding(root, wid, workspace=None):
    from survey_tool.experiments import read_tool_json
    if workspace is None:
        workspace=next((row for row in read_tool_json(root,"workspaces.json",[]) if row.get("id")==wid),{})
    binding=workspace.get("code_development") or {}
    if binding.get("mode")=="local-git" and binding.get("storage")=="project":
        return project_repo_path(root,wid,binding)
    rows = read_tool_json(root, "local-code-bindings.json", {})
    return rows.get(machine_key(), {}).get(wid, "")


def ensure_project_clone(root, wid, binding, *, runner=None):
    """Clone only a missing project-owned directory, never an external binding."""
    if binding.get("storage")!="project":
        return False
    binding=validate_binding(binding)
    target=pathlib.Path(project_repo_path(root,wid,binding))
    if target.exists():
        if not target.is_dir() or not (target/".git").exists():
            raise ValueError("project code directory already exists without Git; no overwrite or cleanup")
        return False
    target.parent.mkdir(parents=True,exist_ok=True)
    # Revalidate after mkdir and reserve the exact destination exclusively.
    project_repo_path(root,wid,binding)
    target.mkdir()
    env={key:value for key,value in os.environ.items() if not key.startswith("GIT_")}
    env["GIT_TERMINAL_PROMPT"]="0"
    clone_url = "git@github.com:" + github_identity(binding["repository_url"]) + ".git" if binding.get("transport") == "ssh" else binding["repository_url"]
    args=["git","-c","core.hooksPath=/dev/null","-c","core.fsmonitor=false","-c","submodule.recurse=false","clone","--no-recurse-submodules","--single-branch","--branch",binding["branch"],"--",clone_url,str(target)]
    try:
        result=(runner or subprocess.run)(args,env=env,capture_output=True,timeout=210)
    except (OSError,subprocess.SubprocessError):
        raise ValueError("project clone failed; check authentication locally; reserved directory retained") from None
    if result.returncode:
        raise ValueError("project clone failed; check authentication/branch locally; reserved directory retained (stderr withheld)")
    if not (target/".git").is_dir():
        raise ValueError("clone did not create an independent Git repository")
    return True


def save_local_binding(root, wid, value):
    from survey_tool.experiments import read_tool_json, write_tool_json
    value = validate_local_path(value) if value else ""
    rows = read_tool_json(root, "local-code-bindings.json", {})
    rows.setdefault(machine_key(), {})[wid] = value
    write_tool_json(root, "local-code-bindings.json", rows)


def _workspace_context(root, wid):
    from survey_tool.experiments import experiment_data, workspace_policy
    data = experiment_data(root)
    ws = next((x for x in data["workspaces"] if x.get("id") == wid), None)
    if not ws:
        raise ValueError("Workspace not found")
    host = next((x.get("ssh_host") for x in data["servers"] if x.get("id") == ws.get("server_id")), "")
    if not host or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:@-]{0,254}", host):
        raise ValueError("bound Server ssh_host missing or unsafe")
    remote = str(ws.get("remote_repo") or "")
    if not remote.startswith("/") or any(ord(c) < 32 for c in remote):
        raise ValueError("remote_repo missing or unsafe")
    return data, ws, host, remote, workspace_policy(ws)


def _context(root, wid):
    data, ws, host, remote, policy = _workspace_context(root, wid)
    binding = validate_binding(ws.get("code_development") or {"mode": "auto"})
    if binding["mode"] != "local-git":
        raise ValueError("run code prepare to automatically bind local Git development")
    local = validate_local_path(local_binding(root, wid, ws))
    return data, ws, binding, local, host, remote, policy


def _idle(root, data, host, repo):
    from survey_tool.experiments import resolve_run_config, execution_outbox_public
    active = {x.get("run_id") for x in execution_outbox_public(root)["execution_outbox"]["items"] if x.get("status") in {"claimed", "acknowledged", "running"}}
    for run in data["runs"]:
        resolved = resolve_run_config(pathlib.Path(root), run, data)
        if resolved.get("ssh_host") == host and resolved.get("remote_repo") == repo and (run.get("id") in active or run.get("status") == "running" or run.get("workflow_stage") == "running"):
            raise ValueError("bound repository has an active Run/lease; stop or repair it before syncing")


def _invoke(host, spec, runner=None):
    from survey_tool.managed_execution import _ssh_client_files
    source = pathlib.Path(__file__).with_name("code_git_worker.py").read_text(encoding="utf-8")
    args = ["python3" if host else sys.executable, "-c", source, json.dumps(spec)]
    if host:
        args = ["ssh", "-T", *_ssh_client_files(), "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-o", "ClearAllForwardings=yes", "-o", "StrictHostKeyChecking=yes", host, shlex.join(args)]
    try:
        result = (runner or subprocess.run)(args, capture_output=True, timeout=210)
        payload = json.loads(result.stdout.decode("utf-8") if isinstance(result.stdout, bytes) else result.stdout)
    except (OSError, subprocess.SubprocessError, ValueError):
        raise ValueError("Git/SSH observation failed; authentication or connectivity must be resolved locally") from None
    if result.returncode or not payload.get("ok"):
        raise ValueError(str(payload.get("error") or "Git/SSH operation blocked"))
    return payload


def _spec(binding, repo, action, policy=None, **extra):
    return {**binding, "repo": repo, "action": action, "remote": policy is not None, **({key: policy[key] for key in ("allowed_write_roots", "read_only_roots", "forbidden_paths")} if policy else {}), **extra}


def _receipt(root, wid, result):
    from survey_tool.experiments import read_tool_json, write_tool_json, workspace_execution_hash, experiment_data
    rows = read_tool_json(root, "code-sync-receipts.json", {})
    ws = next(x for x in experiment_data(root)["workspaces"] if x["id"] == wid)
    record = {"contract": "survey-tool.code-sync/v1", "workspace_id": wid, "machine": machine_key(), "workspace_hash": workspace_execution_hash(ws), "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(), **result}
    rows.setdefault(machine_key(), {})[wid] = record
    write_tool_json(root, "code-sync-receipts.json", rows)
    return record


def auto_bind_code(root, wid, *, invoke=_invoke):
    """Explicit local prepare discovers a missing binding; never replaces local-git."""
    from survey_tool.experiments import _binding_registry_hash, update_workspace_binding
    from server import tool_state_transaction
    data, ws, host, remote, policy = _workspace_context(root, wid)
    current = validate_binding(ws.get("code_development") or {"mode": "auto"})
    if current["mode"] == "local-git":
        return False
    _idle(root, data, host, remote)
    expected = _binding_registry_hash(data["workspaces"])
    state = invoke(host, _spec({}, remote, "discover", policy))
    binding = validate_binding({"mode": "local-git", "repository_url": state["repository_url"], "branch": state["branch"], "transport": state["transport"], "storage": "project"})
    target = pathlib.Path(project_repo_path(root, wid, binding))
    if target.exists() and (not target.is_dir() or not (target / ".git").exists()):
        raise ValueError("project code directory already exists without Git; no overwrite or cleanup")
    with tool_state_transaction(root):
        fresh, _, fresh_host, fresh_remote, _ = _workspace_context(root, wid)
        if _binding_registry_hash(fresh["workspaces"]) != expected or fresh_host != host or fresh_remote != remote:
            raise ValueError("Workspace/Server changed during discovery; retry without editing")
        _idle(root, fresh, host, remote)
        update_workspace_binding(root, wid, expected, {"code_development": binding})
    return True


def prepare_code(root, wid, *, invoke=_invoke, clone=ensure_project_clone):
    """Auto-bind if needed, checkpoint/push remote, then fast-forward local code."""
    binding_created = auto_bind_code(root, wid, invoke=invoke)
    data, ws, binding, local, host, remote, policy = _context(root, wid)
    from survey_tool.experiments import read_tool_json, write_tool_json
    receipts=read_tool_json(root,"code-sync-receipts.json",{})
    receipts.setdefault(machine_key(),{}).pop(wid,None)
    write_tool_json(root,"code-sync-receipts.json",receipts)
    _idle(root, data, host, remote)
    # Reject existing local edits before writing/pushing on the server.
    # A missing project clone is created only after the server checkpoint succeeds.
    cloned=False
    if binding.get("storage")=="project" and not pathlib.Path(local).exists():
        remote_state=invoke(host,_spec(binding,remote,"checkpoint",policy))
        cloned=clone(root,wid,binding)
        local_state=invoke("",_spec(binding,local,"inspect"))
    else:
        if binding.get("storage")=="project": ensure_project_clone(root,wid,binding)
        local_state = invoke("", _spec(binding, local, "inspect"))
        remote_state = invoke(host, _spec(binding, remote, "checkpoint", policy))
        # The checkpoint may have advanced upstream. Fetch that published SHA.
        refreshed = invoke("", _spec(binding, local, "inspect"))
        if refreshed["head"] != local_state["head"]:
            raise ValueError("local HEAD changed during remote checkpoint; rerun prepare without editing")
        local_state = refreshed
    if local_state["upstream"] != remote_state["upstream"]:
        raise ValueError("upstream changed between fetches; rerun prepare without editing")
    target = remote_state["upstream"]
    invoke(host, _spec(binding, remote, "advance", policy, expected_head=remote_state["head"], target=target))
    invoke("", _spec(binding, local, "advance", expected_head=local_state["head"], target=target))
    return _receipt(root, wid, {"binding_created":binding_created,"local_clone_created":cloned,"operation": "prepare", "baseline_commit": target, "local_repo": local, "remote_repo": remote, "ssh_host": host, "remote_commit_created": remote_state.get("commit_created", False), "push_performed": remote_state.get("push_performed", False), "execution_started": False})


def publish_code(root, wid, commit, *, invoke=_invoke):
    """Publish an exact, reviewed local checkpoint; never deploy or start a Run."""
    from survey_tool.experiments import read_tool_json, workspace_execution_hash
    if not re.fullmatch(r"[0-9a-f]{40}", commit or ""):
        raise ValueError("publish requires a full 40-character commit SHA")
    data, ws, binding, local, host, remote, policy = _context(root, wid)
    previous = read_tool_json(root, "code-sync-receipts.json", {}).get(machine_key(), {}).get(wid, {})
    if previous.get("workspace_hash") != workspace_execution_hash(ws) or previous.get("local_repo") != local or previous.get("operation") not in {"prepare", "publish"}:
        raise ValueError("run code prepare before editing; binding/baseline receipt missing or stale")
    _idle(root, data, host, remote)
    state = invoke("", _spec(binding, local, "publish", target=commit, baseline=previous.get("published_commit", previous.get("baseline_commit"))))
    return _receipt(root, wid, {"operation": "publish", "baseline_commit": previous["baseline_commit"], "published_commit": commit, "local_repo": local, "remote_repo": remote, "ssh_host": host, "push_performed": state["push_performed"], "execution_started": False})


def deploy_code(root, wid, commit, confirmation, *, invoke=_invoke):
    """Deploy only an explicitly authorized, already-published exact commit."""
    from survey_tool.experiments import read_tool_json, workspace_execution_hash
    if not re.fullmatch(r"[0-9a-f]{40}", commit or ""):
        raise ValueError("deploy requires a full 40-character commit SHA")
    if confirmation != f"DEPLOY CODE {wid} {commit}":
        raise ValueError("deployment requires explicit human confirmation for Workspace and commit")
    data, ws, binding, local, host, remote, policy = _context(root, wid)
    previous = read_tool_json(root, "code-sync-receipts.json", {}).get(machine_key(), {}).get(wid, {})
    if previous.get("workspace_hash") != workspace_execution_hash(ws) or previous.get("local_repo") != local or previous.get("operation") not in {"prepare", "publish", "deploy"}:
        raise ValueError("run code prepare before editing; binding/baseline receipt missing or stale")
    _idle(root, data, host, remote)
    local_state = invoke("", _spec(binding, local, "inspect"))
    if local_state["head"] != commit:
        raise ValueError("local HEAD must equal the explicitly authorized deployment commit")
    remote_state = invoke(host, _spec(binding, remote, "inspect", policy))
    if remote_state["head"] != previous.get("deployed_commit", previous.get("baseline_commit")):
        raise ValueError("remote HEAD changed since prepare/deploy; do not overwrite another task")
    invoke(host, _spec(binding, remote, "advance", policy, expected_head=remote_state["head"], target=commit))
    return _receipt(root, wid, {"operation": "deploy", "baseline_commit": previous["baseline_commit"], "deployed_commit": commit, "local_repo": local, "remote_repo": remote, "ssh_host": host, "push_performed": False, "execution_started": False, "linux_cuda_validation": "not_performed; only on explicit request"})


def verify_run_commit(root, ws, run, resolved, *, invoke=_invoke):
    binding = ws.get("code_development") or {}
    if binding.get("mode") != "local-git":
        return None
    binding = validate_binding(binding)
    commit = str(run.get("git_commit") or "")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("local-git Run requires an exact git_commit SHA, not branch/latest")
    return invoke(resolved["ssh_host"], _spec(binding, resolved["project_dir"], "verify", target=commit))


def code_workflow_prompt(root, ws, cli_path):
    binding = validate_binding(ws.get("code_development") or {"mode": "auto"})
    if binding["mode"] == "remote":
        return ""
    if not ws.get("remote_repo") or not ws.get("server_id"):
        return ""  # Missing execution Workspace is not permission to guess a repository.
    command = shlex.join(["python3", str(cli_path), "--project", str(root), "code", "prepare", "--workspace-id", ws["id"]])
    if binding["mode"] == "auto":
        return ("\n本地 Git 自动绑定优先\n"
                f"- 编辑前：{command}；无需手填绑定。\n"
                "- 远端 origin/分支自动绑定，保留 SSH；只改返回的 local_repo。失败停止，禁覆盖/SSH patch。\n"
                f"- 默认不测试；code_change_review、提交后 code publish --workspace-id {shlex.quote(ws['id'])} --commit <SHA>；不部署/Run，绑定变化重核授权。\n")
    local = local_binding(root, ws["id"], ws)
    publish = shlex.join(["python3", str(cli_path), "--project", str(root), "code", "publish", "--workspace-id", ws["id"], "--commit"]) + " <完整40位SHA>"
    return ("\n本地 Git 开发（覆盖上文远程修改指令）\n"
            f"- repository={binding['repository_url']} branch={binding['branch']} local_repo={local or '未绑定：停止并要求登记本机路径'}。本机指 Survey Tool 服务所在机器，不是浏览器所在机器。\n"
            f"- 每次代码修改任务在第一处编辑前自动执行：{command}。失败立即停止；禁止绕过改走 SSH patch。该命令先检查本机干净与服务器空闲，再自动提交远端代码改动并 push 绑定分支，最后将本机 ff-only 同步到该 SHA；不自动 stash/rebase/force-push。storage=project 时可首次克隆到项目 code-repositories/<Workspace-ID>/<仓库名>，已有目录不覆盖、不搬动。代码目录不进入研究 Publish。命令不启动 Run。\n"
            "- 只在上述 local_repo 内按原允许文件范围编辑；默认不运行测试、构建、smoke 或程序验证，只有用户明确要求时执行。读取该仓库 AGENTS.md；仓库默认测试约定不算本轮授权。\n"
            "- 对本地 diff 调用 code_change_review，审阅通过后按精确任务文件 checkpoint commit；未测试不阻断交付，标注‘未测试’。不要修改数据/权重/日志/凭据。\n"
            f"- 本地提交后立即自动发布：{publish}。使用刚通过审阅的完整提交 SHA，不需要另行询问 push；发布失败停止并报告，不强推。仅对本任务绑定的私人代码仓库和分支适用，不授权推送 Survey Tool 或其他仓库。\n"
            "- push 不等于服务器部署。部署、Linux/CUDA 检查和正式 Run 仍需对应授权。获得部署授权后用 code deploy --workspace-id <W> --commit <完整SHA> --confirmation 'DEPLOY CODE <W> <完整SHA>'；不要部署 latest。\n"
            "- Run git_commit 填实际已部署的完整 SHA。仅用户要求时执行 Linux/CUDA 测试；未执行标注‘未验证’，不编造命令、退出码或通过结论。报告 authored/deployed commit；Git 与代码审阅不等于运行验证，Run 启动门禁保留。\n")
