"""Fail-closed managed Run launcher. No network activity occurs unless explicitly called."""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import shlex
import subprocess
from typing import Any, Callable

from survey_tool.experiments import (_REPAIRABLE_EXECUTION_FAILURES,_approved_spec_hash,_dispatch_item_gate,_leased_transition,_managed_repair_budget,_outbox_read,_parse_iso,apply_managed_result_draft,begin_managed_execution_repair,experiment_data,execution_isolation,managed_execution_heartbeat,prevalidate_managed_result_draft,run_review_status,update_managed_execution_metadata,workspace_policy)

Runner=Callable[...,dict[str,Any]]
MAX_OUTPUT=65536
MARKER="SURVEY_TOOL_RUN_COMPLETE"
LAUNCH_STATE="SURVEY_TOOL_LAUNCHER_STARTED"
_CONDA_NAME=re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
# Locator for the already verified environment, not an alternate environment.
# Other hosts/names retain the generic activation discovery below.
_VERIFIED_CONDA_INSTALLATIONS={("SZY-3090", "IPLoc"): "/songzhengyue/miniconda3"}


def activation_contract(value, *, ssh_host=""):
    """Compile a declarative Workspace environment requirement into safe shell.

    Workspace rules deliberately store an environment *description*, not arbitrary
    shell.  Managed execution must therefore recognize a small declarative conda
    grammar and prove that the launched interpreter actually belongs to it.
    """
    raw=str(value or "").strip()
    if not raw or "\x00" in raw or "\r" in raw or "\n" in raw:
        raise ValueError("Workspace 未登记可验证的 environment_activation；禁止使用裸 python 或自行推断替代环境")
    match=re.fullmatch(r"conda:([A-Za-z0-9][A-Za-z0-9._-]{0,127})",raw)
    if not match:
        match=re.fullmatch(r"(?:使用\s*)?([A-Za-z0-9][A-Za-z0-9._-]{0,127})\s+conda(?:\s+环境)?",raw,re.I)
    if not match:
        raise ValueError("environment_activation 必须是 'conda:<环境名>' 或 '<环境名> conda 环境'；不得把说明文字或任意 shell 当作激活命令")
    name=match.group(1)
    if not _CONDA_NAME.fullmatch(name):
        raise ValueError("conda 环境名不安全")
    quoted=shlex.quote(name)
    installation=_VERIFIED_CONDA_INSTALLATIONS.get((str(ssh_host),name))
    bootstrap=""
    expected_prefix=""
    if installation:
        executable=shlex.quote(installation+"/bin/conda")
        hook=shlex.quote(installation+"/etc/profile.d/conda.sh")
        expected_prefix=installation+"/envs/"+name
        bootstrap=f'''# Use the verified installation even if login loaded a stale conda function.
if [ ! -x {executable} ] || [ ! -r {hook} ]; then
  echo "SURVEY_TOOL_ENV_PROOF_FAIL verified_conda_installation_unavailable" >&2; exit 88
fi
export CONDA_EXE={executable}
. {hook}
hash -r
'''
    script=f'''set -euo pipefail
# survey-tool controlled conda activation; do not fall back to system python.
{bootstrap}if ! type conda 2>/dev/null | grep -q "function"; then
  for f in "${{CONDA_EXE:+$(dirname \"$CONDA_EXE\")/../etc/profile.d/conda.sh}}" "$HOME/miniconda3/etc/profile.d/conda.sh" "$HOME/anaconda3/etc/profile.d/conda.sh" "/opt/conda/etc/profile.d/conda.sh"; do
    if [ -n "$f" ] && [ -f "$f" ]; then . "$f"; break; fi
  done
fi
if ! type conda 2>/dev/null | grep -q "function"; then
  echo "SURVEY_TOOL_ENV_PROOF_FAIL conda_shell_unavailable" >&2; exit 86
fi
conda activate {quoted}
if [ "${{CONDA_DEFAULT_ENV:-}}" != {quoted} ]; then
  echo "SURVEY_TOOL_ENV_PROOF_FAIL wrong_conda_env:${{CONDA_DEFAULT_ENV:-}}" >&2; exit 87
fi
python - {quoted} {shlex.quote(expected_prefix)} <<'PY'
import os, sys
expected=sys.argv[1]
expected_prefix=sys.argv[2]
if os.environ.get("CONDA_DEFAULT_ENV") != expected:
    raise SystemExit("CONDA_DEFAULT_ENV mismatch")
prefix=os.path.realpath(os.environ.get("CONDA_PREFIX", ""))
exe=os.path.realpath(sys.executable)
if not prefix or os.path.commonpath([prefix, exe]) != prefix:
    raise SystemExit("python is outside CONDA_PREFIX")
if expected_prefix and prefix != os.path.realpath(expected_prefix):
    raise SystemExit("python is not in the verified environment installation")
print("SURVEY_TOOL_ENV_PROOF", expected, prefix, exe)
PY'''
    return {"kind":"conda","name":name,"raw":raw,"script":script,
            "verified_installation":installation,"expected_prefix":expected_prefix}

def _default_runner(argv,*,input_data=b"",timeout=30):
    result=subprocess.run(argv,input=input_data,capture_output=True,timeout=timeout,shell=False)
    return {"returncode":result.returncode,"stdout":result.stdout.decode("utf-8","replace")[:MAX_OUTPUT],"stderr":result.stderr.decode("utf-8","replace")[:MAX_OUTPUT]}

def _run(runner,argv,*,input_data=b"",timeout=30):
    result=runner(list(argv),input_data=input_data,timeout=timeout)
    out={"returncode":int(result.get("returncode",-1)),"stdout":str(result.get("stdout") or "")[:MAX_OUTPUT],"stderr":str(result.get("stderr") or "")[:MAX_OUTPUT]}
    return out

SSH_CONFIG_ENV="SURVEY_TOOL_SSH_CONFIG"
KNOWN_HOSTS_ENV="SURVEY_TOOL_KNOWN_HOSTS"

def _ssh_client_files(home=None):
    """Resolve this machine's local ssh client files instead of one host's absolute paths.

    The operator's ssh config lives in a different place per machine (WSL keeps the
    Windows profile under /mnt/c, macOS under ~/.ssh).  Hardcoding one machine's
    path makes managed execution fail everywhere else, so an explicit per-machine
    override wins, otherwise the standard ~/.ssh/config is used when it exists.
    An explicitly configured path is passed even if missing, so the failure is
    visible instead of silently falling back to a different host configuration.
    """
    home=pathlib.Path(home or pathlib.Path.home())
    argv=[]
    configured=str(os.environ.get(SSH_CONFIG_ENV) or "")
    if configured:
        argv += ["-F",configured]
    else:
        default=home/".ssh"/"config"
        if default.is_file(): argv += ["-F",str(default)]
    known_hosts=str(os.environ.get(KNOWN_HOSTS_ENV) or "")
    if known_hosts: argv += ["-o",f"UserKnownHostsFile={known_hosts}"]
    return argv

def _ssh(runner,host,args,*,input_data=b"",timeout=30):
    remote_command=shlex.join([str(value) for value in args])
    argv=["ssh","-o","BatchMode=yes","-o","ConnectTimeout=10"]
    if host=="SZY-3090":
        argv += [*_ssh_client_files(),"-o","StrictHostKeyChecking=yes"]
    return _run(runner,[*argv,host,"--",remote_command],input_data=input_data,timeout=timeout)

def _tmux_binary(host):
    if host=="SZY-3090":
        return "/defaultShare/archive/songzhengyue/projects/IPLoc/tools/tmux-local/bin/tmux"
    return "tmux"

def _lease_context(root,dispatch_id,lease_token,consumer,allowed):
    data=experiment_data(root); box=_outbox_read(root); item=next((row for row in box["items"] if row.get("dispatch_id")==dispatch_id),None)
    if not item: raise ValueError("dispatch not found")
    if item.get("status") not in allowed: raise ValueError(f"dispatch status {item.get('status')} is not managed-start eligible")
    if item.get("consumer")!=str(consumer or ""): raise ValueError("lease consumer mismatch")
    expected=hashlib.sha256(str(lease_token or "").encode()).hexdigest()
    if not lease_token or not __import__("secrets").compare_digest(str(item.get("lease_token_hash") or ""),expected): raise ValueError("lease token invalid")
    expiry=_parse_iso(item.get("lease_expires_at"))
    if not expiry or expiry<=dt.datetime.now(): raise ValueError("lease expired")
    run=next((row for row in data["runs"] if row.get("id")==item.get("run_id")),None)
    if not run: raise ValueError("Run not found")
    if run.get("workflow_version")!=2: raise ValueError("Run is not workflow-v2")
    stage=str(run.get("workflow_stage") or "")
    if item.get("status") in {"claimed","acknowledged"} and stage!="ready_to_run":
        raise ValueError("managed start requires workflow-v2 ready_to_run")
    if item.get("status")=="running":
        same_attempt=(run.get("execution_dispatch_id")==dispatch_id and bool(run.get("execution_authorization_consumed_at")))
        started=(item.get("managed_execution") or {}).get("started_evidence")=="tmux_new_session_ok"
        # A legacy browser mark-failed could leave the Run projection at failed
        # while this exact managed dispatch remained running.  Do not strand the
        # lease holder: the running dispatch and remote start evidence are the
        # operational facts; reattach repairs the stale projection separately.
        if not same_attempt or not started or stage not in {"running","failed"}:
            raise ValueError("Run is not linked to this active managed execution")
    if run_review_status(run)!="approved" or run.get("execution_authorized_at")!=item.get("authorization_timestamp") or _approved_spec_hash(run)!=item.get("approved_spec_hash"): raise ValueError("approved authorization/spec snapshot invalid")
    resolved=_dispatch_item_gate(root,run,item,data)
    if not item.get("workspace_execution_hash") or item.get("workspace_execution_hash")!=resolved.get("workspace_execution_hash"): raise ValueError("Workspace binding/policy snapshot missing or changed after authorization")
    ws=next((row for row in data["workspaces"] if row.get("id")==resolved.get("workspace_id")),{}); isolation=execution_isolation(ws)
    if isolation.get("mode") not in {"bubblewrap","tmux-guarded"} or isolation.get("required") is not True: raise ValueError("managed execution blocked: required isolation is not configured")
    command=str(run.get("command") or "")
    if not command or len(command.encode())>16384 or "\0" in command: raise ValueError("approved Run command is empty or unsafe")
    if re.search(r"<[^>\n]{1,256}>",command): raise ValueError("Run command 仍含占位符；Pi 必须先调用 survey_run_execution prepare")
    activation=activation_contract(resolved.get("environment_activation"),
                                   ssh_host=resolved.get("ssh_host"))
    return data,item,run,resolved,ws,isolation,command,activation

def _under(path,roots): return any(path==root or path.startswith(root.rstrip("/")+"/") for root in roots)

def _safe_remote_path(value,name):
    value=str(value or "")
    if not value.startswith("/") or any(ch in value for ch in ("\0","\r","\n")): raise ValueError(f"{name} must be an absolute path without control characters")
    return value

def _realpath(runner,host,value,*,existing=False,name="path"):
    value=_safe_remote_path(value,name); result=_ssh(runner,host,["realpath",*([] if existing else ["-m"]),"--",value],timeout=15)
    resolved=result["stdout"].strip().splitlines()[0] if result["stdout"].strip() else ""
    if result["returncode"] or not resolved.startswith("/") or any(ch in resolved for ch in ("\0","\r","\n")): raise ValueError(f"cannot canonicalize {name}")
    return resolved

def _managed_execution_preflight(root,dispatch_id,lease_token,consumer,runner:Runner=_default_runner):
    root=pathlib.Path(root).resolve(); data,item,run,resolved,ws,isolation,command,activation=_lease_context(root,dispatch_id,lease_token,consumer,{"claimed","acknowledged","running"})
    if item["status"] not in {"acknowledged","running"}: raise ValueError("dispatch must be acknowledged before managed start")
    # A declared environment is not merely documentation: prove it remotely
    # before any launcher is uploaded or a run is allowed to consume authority.
    proof=_ssh(runner,str(resolved.get("ssh_host") or ""),["bash","-lc",activation["script"]],timeout=45)
    if proof["returncode"]!=0 or "SURVEY_TOOL_ENV_PROOF" not in proof["stdout"]:
        raise ValueError("environment activation proof failed; do not substitute another Python/conda environment")
    from survey_tool.code_workflow import verify_run_commit
    code_identity=verify_run_commit(root,ws,run,resolved)
    host=str(resolved.get("ssh_host") or ""); policy=workspace_policy(ws); writes=sorted(set(map(str,policy["allowed_write_roots"])),key=lambda x:(x.count("/"),x)); reads=sorted(set(map(str,policy["read_only_roots"])))
    tmux_bin=_tmux_binary(host)
    probe_cmd=("test -x "+shlex.quote(tmux_bin)) if tmux_bin.startswith("/") else "command -v tmux >/dev/null"
    if isolation["mode"]=="bubblewrap": probe_cmd="command -v bwrap >/dev/null && "+probe_cmd
    if code_identity: probe_cmd="command -v flock >/dev/null && "+probe_cmd
    probe=_ssh(runner,host,["sh","-c",probe_cmd],timeout=20)
    if probe["returncode"]!=0: raise ValueError("remote required isolation runtime unavailable")
    canonical_writes=[_realpath(runner,host,value,name="allowed write root") for value in writes]
    for value in canonical_writes:
        if _ssh(runner,host,["test","-w",value],timeout=10)["returncode"]!=0: raise ValueError(f"allowed write root is not writable: {value}")
    canonical_reads=[_realpath(runner,host,value,name="read-only root") for value in reads]
    # Bubblewrap can hide broad denied parents and remount narrow allow roots.
    # tmux-guarded cannot hide host paths; it verifies the declared allowlist
    # and records this explicit, lower-isolation mode for human review.
    explicit_allowed=sorted(set(canonical_writes+canonical_reads),key=lambda x:(x.count("/"),x))
    raw_denies=[*policy["forbidden_paths"],*(isolation.get("deny_read_roots") or [])]
    canonical_denies=[]; canonical_forbidden=[]
    for value in raw_denies:
        value=_safe_remote_path(value,"deny path")
        overlaps_allow=any(_under(root,[value]) or _under(value,[root]) for root in explicit_allowed)
        canonical=_realpath(runner,host,value,existing=overlaps_allow,name="deny path")
        if overlaps_allow and _ssh(runner,host,["test","-d",canonical],timeout=10)["returncode"]:
            raise ValueError(f"deny path must be an existing directory: {value}")
        if any(_under(canonical,[root]) for root in explicit_allowed): canonical_forbidden.append(canonical)
        else: canonical_denies.append(canonical)
    canonical_denies=sorted(set(canonical_denies),key=lambda x:(x.count("/"),x))
    canonical_forbidden=sorted(set(canonical_forbidden),key=lambda x:(x.count("/"),x))
    if code_identity:
        lock_file=code_identity["git_common_dir"].rstrip("/")+"/survey-tool-code.lock"
        canonical_lock=_realpath(runner,host,lock_file,name="code lock")
        if canonical_lock!=lock_file or not _under(canonical_lock,canonical_writes) or _under(canonical_lock,canonical_forbidden) or _under(canonical_lock,canonical_reads):
            raise ValueError("code lock escapes effective write policy")
        code_identity["lock_file"]=lock_file
    names=("project_dir","run_dir","log_file","output_dir","metrics_file"); paths={}
    for name in names:
        paths[name]=_realpath(runner,host,resolved.get(name),name=name)
        if not _under(paths[name],canonical_writes) or _under(paths[name],canonical_forbidden): raise ValueError(f"{name} escapes allowed or enters forbidden roots")
    artifact_paths=[]
    for index,value in enumerate(run.get("required_artifacts") or []):
        artifact=_realpath(runner,host,value,name=f"required artifact {index}")
        if not _under(artifact,canonical_writes) or _under(artifact,canonical_forbidden): raise ValueError(f"required artifact {index} escapes allowed roots")
        artifact_paths.append(artifact)
    data_root=str(resolved.get("remote_data_root") or "")
    if not data_root.startswith("/") or not any(_under(data_root,[value]) or _under(value,[data_root]) for value in canonical_reads): raise ValueError("remote_data_root is not declared read-only")
    datasets=[]; link_probe="import json,os,pathlib,sys;s=pathlib.Path(sys.argv[1]);t=pathlib.Path(sys.argv[2]);sk=('dir' if s.is_dir() else 'file' if s.is_file() else 'missing');tk=('absent' if not t.exists() and not t.is_symlink() else 'symlink_exact' if t.is_symlink() and t.resolve()==s.resolve() else 'symlink_mismatch' if t.is_symlink() else 'dir' if t.is_dir() else 'file');print(json.dumps({'source_kind':sk,'source_readable':os.access(s,os.R_OK),'target_kind':tk}))"
    for binding in resolved.get("dataset_bindings") or []:
        source=_realpath(runner,host,binding["source_path"],name=f"dataset {binding['id']} source"); parent=_realpath(runner,host,str(pathlib.PurePosixPath(binding["target_path"]).parent),name=f"dataset {binding['id']} target parent"); target=_safe_remote_path(binding["target_path"],f"dataset {binding['id']} target")
        if not _under(source,canonical_reads) or _under(source,canonical_writes) or not _under(target,canonical_writes) or not _under(parent,canonical_writes): raise ValueError(f"dataset {binding['id']} escapes effective policy")
        observed=_ssh(runner,host,["python3","-c",link_probe,source,target],timeout=15)
        try: state=json.loads(observed["stdout"])
        except Exception as exc: raise ValueError(f"dataset {binding['id']} observation failed") from exc
        if state.get("source_kind")!="dir":
            if binding.get("required") or state.get("source_kind")!="missing": raise ValueError(f"dataset {binding['id']} source must be a directory")
            continue
        if not state.get("source_readable"): raise ValueError(f"dataset {binding['id']} is not readable")
        target_kind=state.get("target_kind")
        if binding["mode"]=="bind_ro" and target_kind not in {"absent","dir"}: raise ValueError(f"dataset {binding['id']} bind target must be absent or a directory")
        if binding["mode"]=="bind_ro" and target_kind=="dir":
            target=_realpath(runner,host,target,existing=True,name=f"dataset {binding['id']} target")
            if not _under(target,canonical_writes): raise ValueError(f"dataset {binding['id']} target escapes allowed roots")
        if binding["mode"]=="symlink_ro" and target_kind not in {"absent","symlink_exact"}: raise ValueError(f"dataset {binding['id']} symlink target mismatch")
        datasets.append({**binding,"source_path":source,"target_path":target,"target_state":target_kind})
    paths["required_artifacts"]=artifact_paths
    guarded=isolation["mode"]=="tmux-guarded"
    return {"code_identity":code_identity,"ok":True,"dispatch_id":dispatch_id,"run_id":run["id"],"checks":{"lease":True,"approved_snapshot":True,"workspace_snapshot":True,"policy":True,"bubblewrap":not guarded,"tmux":True,"paths":True,"environment_activation":True,"data_read_only":True,"datasets":len(datasets),"degraded_host_visibility":guarded} ,"resolved":paths,"write_roots":canonical_writes,"read_only_roots":canonical_reads,"forbidden_roots":canonical_forbidden,"dataset_bindings":datasets,"isolation":{"mode":isolation["mode"],"required":True,"network":isolation["network"],"deny_read_roots":canonical_denies},"ssh_host":host,"tmux_session":str(resolved["tmux_session"]),"command":command,"activation":activation["script"],"environment_proof":proof["stdout"].strip()[:1024],"_run":run}

def managed_execution_preflight(root,dispatch_id,lease_token,consumer,runner:Runner=_default_runner):
    """Return only bounded, non-secret preflight evidence."""
    result=_managed_execution_preflight(root,dispatch_id,lease_token,consumer,runner)
    return {key:value for key,value in result.items() if key not in {"command","activation","_run","ssh_host","tmux_session","resolved","write_roots","read_only_roots","forbidden_roots","dataset_bindings"}}

def build_launcher(preflight):
    paths=preflight["resolved"]
    log=shlex.quote(paths["log_file"]); exit_file=shlex.quote(paths["run_dir"]+"/.survey-tool-exit-code"); marker_file=shlex.quote(paths["run_dir"]+"/.survey-tool-complete"); state_file=shlex.quote(paths["run_dir"]+"/.survey-tool-launch-state")
    commit_guard=""
    if preflight.get("code_identity"):
        repo=shlex.quote(paths["project_dir"]); commit=shlex.quote(preflight["code_identity"]["head"])
        safe_git=f'git -c core.hooksPath=/dev/null -c core.fsmonitor=false -C {repo}'
        lock=shlex.quote(preflight["code_identity"]["lock_file"])
        commit_guard=f'test ! -L {lock} && exec 9>>{lock} && flock -s -n 9 || exit 73\n'
        commit_guard+=f'test "$({safe_git} rev-parse HEAD)" = {commit} && state="$({safe_git} status --porcelain=v1 --untracked-files=all --ignore-submodules=none)" && test -z "$state" || exit 73\n'
    prefix="#!/usr/bin/env bash\nset -o pipefail\n"+commit_guard+"mkdir -p -- "+" ".join(shlex.quote(paths[k]) for k in ("run_dir","output_dir"))+" "+shlex.quote(str(pathlib.PurePosixPath(paths["log_file"]).parent))+"\nprintf '%s\\n' "+shlex.quote(LAUNCH_STATE)+" > "+state_file+".tmp\nmv -- "+state_file+".tmp "+state_file+"\nset +e\n"
    suffix="\nrc=${PIPESTATUS[0]}\nprintf '%s\\n' \"$rc\" > "+exit_file+".tmp\nmv -- "+exit_file+".tmp "+exit_file+"\nprintf '%s\\n' "+shlex.quote(MARKER)+" > "+marker_file+"\nexit \"$rc\"\n"
    if preflight["isolation"].get("mode", "bubblewrap")=="tmux-guarded":
        activation=preflight.get("activation","")
        script=prefix
        script+="# WARNING: tmux-guarded is a human-approved degraded isolation mode.\n"
        script+="# Host read visibility is not kernel-isolated; only approved command/path gates apply.\n"
        # Activation intentionally enables strict shell flags. Keep the entire
        # activation + command lifecycle inside tee's left-hand group so an
        # early conda/nounset failure still leaves a log, exit code and marker.
        script+="{\nprintf '%s\\n' SURVEY_TOOL_LAUNCH_BOOTSTRAP\n"+str(activation).strip()+"\nprintf '%s\\n' SURVEY_TOOL_ACTIVATION_OK\ncd -- "+shlex.quote(paths["project_dir"])+"\nprintf '%s\\n' SURVEY_TOOL_PROJECT_CWD_OK\n"+preflight["command"]+"\n} 2>&1 | tee -a "+log+suffix
        return script
    args=["bwrap","--die-with-parent","--new-session","--ro-bind","/","/"]
    if preflight["isolation"]["network"]=="none": args.append("--unshare-net")
    # Hide denied ancestors before remounting the explicit allowlist children.
    # Recreate only the minimal parent chain required by each exception.
    denies=sorted(set(preflight["isolation"].get("deny_read_roots") or []),key=lambda x:(x.count("/"),x))
    for root in denies: args += ["--tmpfs",root]
    exception_roots=[*preflight["write_roots"],*preflight["read_only_roots"]]
    for root in sorted(set(exception_roots),key=lambda x:(x.count("/"),x)):
        for deny in denies:
            if _under(root,[deny]):
                rel=pathlib.PurePosixPath(root).relative_to(deny)
                current=pathlib.PurePosixPath(deny)
                for part in rel.parts[:-1]:
                    current=current / part; args += ["--dir",str(current)]
    args += ["--tmpfs","/tmp"]
    for root in preflight["write_roots"]: args += ["--bind",root,root]
    for root in preflight["read_only_roots"]: args += ["--ro-bind",root,root]
    # More-specific forbidden children win over their enclosing write root.
    for root in preflight.get("forbidden_roots") or []: args += ["--ro-bind",root,root]
    for binding in preflight.get("dataset_bindings") or []:
        if binding["mode"]=="bind_ro":
            if binding.get("target_state")=="absent": args += ["--dir",binding["target_path"]]
            args += ["--ro-bind",binding["source_path"],binding["target_path"]]
        else: args += ["--ro-bind",binding["source_path"],binding["source_path"]]
    for root in sorted(preflight["isolation"]["deny_read_roots"]): args += ["--tmpfs",root]
    activation=preflight.get("activation","")
    if isinstance(activation,dict): activation=activation.get("script","")
    payload=(str(activation).strip()+"\n" if str(activation).strip() else "")+"printf '%s\\n' SURVEY_TOOL_ACTIVATION_OK\n"+preflight["command"]
    args += ["--chdir",paths["project_dir"],"bash","-lc",payload]
    command=" ".join(shlex.quote(x) for x in args)
    return prefix+"{\nprintf '%s\\n' SURVEY_TOOL_LAUNCH_BOOTSTRAP\n"+command+"\n} 2>&1 | tee -a "+log+suffix

def managed_execution_start(root,dispatch_id,lease_token,consumer,runner:Runner=_default_runner):
    pf=_managed_execution_preflight(root,dispatch_id,lease_token,consumer,runner); script=build_launcher(pf); run_id=pf["run_id"]; launcher=pf["resolved"]["run_dir"]+"/.survey-tool-managed/launcher.sh"; host=pf["ssh_host"]
    if pf.get("_run",{}).get("workflow_stage")!="ready_to_run": raise ValueError("managed start requires ready_to_run")
    link_code="import os,pathlib,sys;s=pathlib.Path(sys.argv[1]);t=pathlib.Path(sys.argv[2]);t.parent.mkdir(parents=True,exist_ok=True);\nif t.exists() or t.is_symlink():\n assert t.is_symlink() and t.resolve()==s.resolve(),'symlink mismatch'\nelse: os.symlink(str(s),str(t))"
    for binding in pf.get("dataset_bindings") or []:
        if binding["mode"]=="symlink_ro" and binding.get("target_state")=="absent":
            linked=_ssh(runner,host,["python3","-c",link_code,binding["source_path"],binding["target_path"]],timeout=20)
            if linked["returncode"]: raise ValueError(f"dataset {binding['id']} symlink creation failed")
    upload_code="import base64,os,pathlib,sys,tempfile;p=pathlib.Path(sys.argv[1]);p.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(dir=p.parent);os.write(fd,base64.b64decode(sys.stdin.buffer.read()));os.close(fd);os.chmod(tmp,0o700);os.replace(tmp,p)"
    up=_ssh(runner,host,["python3","-c",upload_code,launcher],input_data=base64.b64encode(script.encode()),timeout=30)
    if up["returncode"]: raise ValueError("launcher upload failed")
    reset_code="import pathlib,sys\nfor value in sys.argv[1:]:\n p=pathlib.Path(value)\n if p.is_file() or p.is_symlink(): p.unlink()"
    reset_paths=[pf["resolved"]["run_dir"]+suffix for suffix in ("/.survey-tool-launch-state","/.survey-tool-exit-code","/.survey-tool-complete")]
    reset=_ssh(runner,host,["python3","-c",reset_code,*reset_paths],timeout=15)
    if reset["returncode"]: raise ValueError("managed attempt evidence reset failed")
    started=_ssh(runner,host,[_tmux_binary(host),"new-session","-d","-s",pf["tmux_session"],launcher],timeout=20)
    if started["returncode"]: raise ValueError("tmux managed start failed")
    # tmux accepting a detached session is not proof that the launcher ran.
    # Wait for a small, launcher-owned bootstrap file before consuming the
    # authorization and projecting this dispatch as running.
    state_path=pf["resolved"]["run_dir"]+"/.survey-tool-launch-state"
    bootstrap_code="import pathlib,sys,time;p=pathlib.Path(sys.argv[1]);end=time.monotonic()+5.0\nwhile time.monotonic()<end:\n if p.is_file(): print(p.read_text()[:128].strip()); raise SystemExit(0)\n time.sleep(.1)\nraise SystemExit(3)"
    bootstrap=_ssh(runner,host,["python3","-c",bootstrap_code,state_path],timeout=8)
    if bootstrap["returncode"] or bootstrap["stdout"].strip()!=LAUNCH_STATE:
        _ssh(runner,host,[_tmux_binary(host),"kill-session","-t",pf["tmux_session"]],timeout=10)
        update_managed_execution_metadata(root,dispatch_id,{"launcher_path":launcher,"isolation_mode":pf["isolation"].get("mode", "bubblewrap"),"started_evidence":"launcher_bootstrap_missing","ssh_host":host,"tmux_session":pf["tmux_session"]})
        raise ValueError("managed launcher did not produce bootstrap evidence")
    try: dispatch=_leased_transition(root,dispatch_id,lease_token,consumer,"running",{"managed_execution":True})
    except Exception:
        _ssh(runner,host,[_tmux_binary(host),"kill-session","-t",pf["tmux_session"]],timeout=10)
        update_managed_execution_metadata(root,dispatch_id,{"launcher_path":launcher,"isolation_mode":pf["isolation"].get("mode", "bubblewrap"),"started_evidence":"remote_started_transition_failed","ssh_host":host,"tmux_session":pf["tmux_session"]})
        raise
    update_managed_execution_metadata(root,dispatch_id,{"launcher_path":launcher,"isolation_mode":pf["isolation"].get("mode", "bubblewrap"),"started_evidence":"tmux_new_session_ok","ssh_host":host,"tmux_session":pf["tmux_session"]})
    return {"ok":True,"dispatch":dispatch,"run_id":run_id,"managed":{"state":"running","isolation":pf["isolation"].get("mode", "bubblewrap"),"tmux_started":True}}

def managed_execution_status(root,dispatch_id,lease_token,consumer,runner:Runner=_default_runner,heartbeat=False):
    if heartbeat: managed_execution_heartbeat(root,dispatch_id,lease_token,consumer)
    pf=_managed_execution_preflight(root,dispatch_id,lease_token,consumer,runner); item=next(row for row in _outbox_read(root)["items"] if row.get("dispatch_id")==dispatch_id); run=pf["_run"]; resolved=pf["resolved"]
    host=str(pf["ssh_host"]); paths={key:str(resolved[key]) for key in ("log_file","metrics_file","output_dir","run_dir")}; paths.update({f"artifact:{i}":str(value) for i,value in enumerate(resolved.get("required_artifacts") or [])}); code="import json,os,pathlib,sys;p=json.loads(sys.argv[1]);out={};\nfor k,v in p.items():\n q=pathlib.Path(v);out[k]={'exists':q.exists(),'size':q.stat().st_size if q.is_file() else 0,'mtime':q.stat().st_mtime if q.exists() else 0}\nr=pathlib.Path(p['run_dir']);e=r/'.survey-tool-exit-code';m=r/'.survey-tool-complete';s=r/'.survey-tool-launch-state';out['exit_code']=e.read_text()[:64].strip() if e.is_file() else None;out['marker']=m.read_text()[:64].strip() if m.is_file() else '';out['launch_state']=s.read_text()[:128].strip() if s.is_file() else '';print(json.dumps(out))"
    observed=_ssh(runner,host,["python3","-c",code,json.dumps(paths,separators=(",",":"))],timeout=20); tmux=_ssh(runner,host,[_tmux_binary(host),"has-session","-t",str(pf["tmux_session"])],timeout=10)
    if observed["returncode"]: raise ValueError("managed status observation failed")
    try: details=json.loads(observed["stdout"][:MAX_OUTPUT])
    except Exception as exc: raise ValueError("managed status response invalid") from exc
    candidate=details.get("exit_code") is not None and details.get("marker")==MARKER
    safe={"tmux_alive":tmux["returncode"]==0,"observed_at":dt.datetime.now().isoformat(timespec="seconds"),"completion_candidate":candidate,"files":{k:details.get(k,{}) for k in paths},"exit_code":details.get("exit_code"),"marker_found":details.get("marker")==MARKER,"launch_state":details.get("launch_state") if details.get("launch_state")==LAUNCH_STATE else ""}
    update_managed_execution_metadata(root,dispatch_id,{"status_observation":safe})
    return {"ok":True,"dispatch_id":dispatch_id,"run_id":run["id"],"state":item["status"],**safe}

def _metric_rows(payload,declared,artifact):
    raw=payload.get("metrics",payload) if isinstance(payload,dict) else payload; rows=[]
    if isinstance(raw,dict): rows=[{"metric_id":str(k),"value":v,"artifact":artifact} for k,v in raw.items()]
    elif isinstance(raw,list): rows=[{"metric_id":str(row.get("metric_id") or row.get("id") or ""),"value":row.get("value"),"artifact":str(row.get("artifact") or artifact)} for row in raw if isinstance(row,dict)]
    else: raise ValueError("metrics JSON shape invalid")
    if not rows or len(rows)>256: raise ValueError("metrics JSON must contain 1-256 metrics")
    for row in rows:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}",row["metric_id"]): raise ValueError("metrics contain invalid IDs")
    return [row for row in rows if row["metric_id"] in declared],[row for row in rows if row["metric_id"] not in declared]


def _trial_metric_rows(payload,manifest,declared,artifact):
    raw=payload.get("trials") if isinstance(payload,dict) else None
    expected=manifest.get("trials") if isinstance(manifest,dict) else None
    if not isinstance(raw,list) or not isinstance(expected,list) or len(raw)!=len(expected): raise ValueError("Trial metrics must contain every planned Trial")
    expected_by_id={str(row.get("id") or ""):row for row in expected if isinstance(row,dict)}; rows=[]; auxiliary=[]
    if len(expected_by_id)!=len(expected): raise ValueError("Trial manifest IDs invalid")
    for result in raw:
        if not isinstance(result,dict) or set(result)-{"id","metrics","artifact"}: raise ValueError("Trial metric result shape invalid")
        trial_id=str(result.get("id") or ""); planned=expected_by_id.get(trial_id); metrics=result.get("metrics")
        if not planned or not isinstance(metrics,dict) or not metrics: raise ValueError("Trial metrics ID or values invalid")
        for metric_id,value in metrics.items():
            metric_id=str(metric_id)
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}",metric_id): raise ValueError("metrics contain invalid IDs")
            row={"metric_id":metric_id,"value":value,"artifact":str(result.get("artifact") or artifact),"provenance":{"trial_id":trial_id,"parameters":planned.get("parameters") or {}}}
            (rows if metric_id in declared else auxiliary).append(row)
    if {str(row.get("id") or "") for row in raw}!=set(expected_by_id): raise ValueError("Trial metrics must contain every planned Trial")
    if len(rows)+len(auxiliary)>2048: raise ValueError("Trial metrics exceed bounded result count")
    return rows,auxiliary

def managed_execution_complete(root,dispatch_id,lease_token,consumer,runner:Runner=_default_runner):
    status=managed_execution_status(root,dispatch_id,lease_token,consumer,runner,heartbeat=True)
    if not status["completion_candidate"] or str(status.get("exit_code"))!="0": raise ValueError("completion requires exit code 0 and fixed marker")
    data,item,run,resolved,_,_,_,_=_lease_context(pathlib.Path(root).resolve(),dispatch_id,lease_token,consumer,{"running"}); metric_stat=status["files"].get("metrics_file",{})
    if not metric_stat.get("exists") or not metric_stat.get("size") or metric_stat["size"]>1_000_000: raise ValueError("nonempty bounded metrics file required")
    previous=(item.get("managed_execution") or {}).get("stable_observation"); current={"size":metric_stat["size"],"mtime":metric_stat["mtime"]}
    if previous!=current: update_managed_execution_metadata(root,dispatch_id,{"stable_observation":current}); raise ValueError("metrics observation is not yet stable")
    content=_ssh(runner,resolved["ssh_host"],["head","-c","1000000","--",resolved["metrics_file"]],timeout=20)
    if content["returncode"]: raise ValueError("metrics read failed")
    try: payload=json.loads(content["stdout"])
    except Exception as exc: raise ValueError("metrics JSON invalid") from exc
    exp=next(row for row in data["experiments"] if row.get("id")==run.get("experiment_id")); declared={str(row.get("id")) for row in exp.get("metric_definitions",[]) if row.get("id")}
    manifest=run.get("trial_manifest") if isinstance(run.get("trial_manifest"),dict) else None
    rows,auxiliary=_trial_metric_rows(payload,manifest,declared,resolved["metrics_file"]) if run.get("trial_plan") else _metric_rows(payload,declared,resolved["metrics_file"])
    required=run.get("required_artifacts") or []
    for index,path in enumerate(required):
        if not status["files"].get(f"artifact:{index}",{}).get("exists"): raise ValueError(f"required artifact missing: {path}")
    key_rows=[{key:value for key,value in row.items() if key in {"metric_id","value","artifact","interpretation"}} for row in rows]
    warning=f"{len(auxiliary)} auxiliary metric(s) were preserved but are not registered in the Experiment; they are not primary evidence." if auxiliary else ""
    draft={"metric_observations":rows,"auxiliary_metric_observations":auxiliary,"key_results":key_rows,"result_analysis":f"Managed execution exited successfully with {len(rows)} declared and {len(auxiliary)} auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.","limitations":"Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions." if auxiliary else "Phase 1 records process evidence and declared metrics only; it does not validate causal or Claim conclusions.","artifacts":"\n".join([resolved["metrics_file"],resolved["log_file"]])}
    prevalidate_managed_result_draft(root,run["id"],draft)
    evidence={"log":resolved["log_file"],"artifact":resolved["metrics_file"],"result_message":"managed execution exited 0; metrics parsed; human analysis required","declared_metric_count":len(rows),"auxiliary_metric_count":len(auxiliary),"warning":warning}; dispatch=_leased_transition(root,dispatch_id,lease_token,consumer,"complete",evidence)
    try: updated=apply_managed_result_draft(root,run["id"],draft)
    except Exception as exc: return {"ok":False,"attention_required":True,"partial":"dispatch_completed_result_draft_write_failed","dispatch":dispatch,"error_class":type(exc).__name__,"claim_modified":False}
    return {"ok":True,"dispatch":dispatch,"run":{"id":updated["id"],"workflow_stage":updated["workflow_stage"]},"result_draft":draft,"warnings":[warning] if warning else [],"claim_modified":False}

def managed_execution_fail(root,dispatch_id,lease_token,consumer,failure_class,reason,retryable=False):
    failure_class=str(failure_class or "").strip(); reason=str(reason or "").strip()
    if failure_class not in _REPAIRABLE_EXECUTION_FAILURES|{"invalid_spec","scientific","authorization","external_dependency"}: raise ValueError("unsupported managed failure class")
    if not reason: raise ValueError("managed failure reason is required")
    if failure_class in _REPAIRABLE_EXECUTION_FAILURES:
        item=next((row for row in _outbox_read(root)["items"] if row.get("dispatch_id")==dispatch_id),None); data=experiment_data(root)
        run=next((row for row in data["runs"] if item and row.get("id")==item.get("run_id")),None)
        budget,_source=_managed_repair_budget(run or {}); used=int((item or {}).get("repair_count") or 0)
        if used<budget: raise ValueError(f"实现层错误仍有自动修复预算（{used}/{budget}）；请调用 repair，不能提前把整个 Run 标记 failed")
    return {"ok":True,"dispatch":_leased_transition(root,dispatch_id,lease_token,consumer,"fail",{"failure_class":failure_class,"reason":reason[:2000],"retryable":bool(retryable)})}

def managed_execution_repair(root,dispatch_id,lease_token,consumer,failure_class,reason):
    return begin_managed_execution_repair(root,dispatch_id,lease_token,consumer,failure_class,reason)
