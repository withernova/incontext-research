#!/usr/bin/env python3
"""survey-tool server — local HTTP server (stdlib only).

Serves the dynamic frontend + a JSON API that reads/writes research-survey
canonical files (kernel/ shell/ state.md) and tool-state (.survey-tool/).

Data contract: see DATA_CONTRACT.md. pi agent reads ONLY canonical files;
.survey-tool/ is tool-state and must never be read by the agent.

Run:  python3 server.py [--port 7421] [--root <projects-root>] [--skill <skill-dir>]
"""
import argparse, json, os, re, sys, subprocess, hashlib, shutil, pathlib, urllib.parse, datetime, time, threading, tempfile, secrets, shlex, sqlite3, functools

# Domain modules import the shared runtime as `server`.  When this file is
# launched directly its module name is `__main__`; publish the same instance
# under `server` to avoid loading it twice and creating a circular import.
sys.modules.setdefault("server", sys.modules[__name__])

from survey_tool.execution.reconciliation import plan_reconciliation
from survey_tool.execution.route_health import SECRET_PATTERN, aggregate_route_health, validate_route_event
from survey_tool.run_lifecycle import architecture_assessment, effective_run_workflow, progress_model as run_progress_model, transition as run_workflow_transition, validate_implementation_ref
from survey_tool.v2 import V2Store, v2_capabilities
from survey_tool.v2.ingest import ingest_staged_candidate
from survey_tool.v2.http import dispatch as v2_dispatch
from survey_tool.v2.worker import start_local_worker
from survey_tool.rule_drafts import organize_rule_draft, preview_rule_draft
from survey_tool.v2.migration import (
    apply_content_index_migration,
    apply_identity_index_migration,
    build_content_index_plan,
    build_identity_index_plan,
    build_migration_inventory,
    content_index_history,
    identity_index_history,
    refresh_v2_index,
)
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.util import spec_from_file_location, module_from_spec
try:
    import fcntl
except ImportError:  # Windows fallback: in-process locking still applies.
    fcntl = None

HERE = pathlib.Path(__file__).resolve().parent
STATIC = HERE / "static"
DEFAULT_ROOT = (HERE.parent).resolve()          # parent of survey-tool/
BUNDLED_SKILL = HERE / "skills" / "research-survey"
DEFAULT_SKILL = BUNDLED_SKILL if BUNDLED_SKILL.exists() else pathlib.Path.home() / ".pi" / "agent" / "skills" / "research-survey"

# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------
def load_config():
    cfg_path = HERE / "config.json"
    cfg = {}
    if cfg_path.exists():
        try: cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        except Exception: cfg = {}
    cfg.setdefault("projects_root", str(DEFAULT_ROOT))
    cfg.setdefault("skill_dir", str(DEFAULT_SKILL))
    cfg.setdefault("port", 7421)
    cfg.setdefault("projects", [])          # registry of known project paths
    return cfg

CFG = None
SKILL = None
SKILL_SCRIPTS = None

LEGACY_V2_WRITE_MIGRATIONS = {
    "intake.update":"/api/v2/p/<project>/intake",
    "paper.update":"/api/v2/p/<project>/papers/<citekey>",
    "idea.create":"/api/v2/p/<project>/ideas",
    "idea.update":"/api/v2/p/<project>/ideas/<idea-id>",
    "comparison.create":"/api/v2/p/<project>/comparisons",
    "comparison.replace":"/api/v2/p/<project>/comparisons/<comparison-id>",
    "question.create":"/api/v2/p/<project>/questions",
    "question.update":"/api/v2/p/<project>/questions/<question-id>",
}

def _legacy_write_removed(name: str) -> bool:
    return str(name) in LEGACY_V2_WRITE_MIGRATIONS

def _legacy_write_blocked(name: str):
    key=str(name)
    if not _legacy_write_removed(key): return None
    return {"error":"1.x 写入口已下线，请使用 2.0 工作区","reason":"legacy_write_removed","removed":key,"migrated_to":LEGACY_V2_WRITE_MIGRATIONS.get(key,"/v2/")}

def save_config():
    (HERE / "config.json").write_text(json.dumps(CFG, ensure_ascii=False, indent=2), encoding="utf-8")

# ---------------------------------------------------------------------------
# path helpers
# ---------------------------------------------------------------------------
def projects_root():
    return pathlib.Path(CFG["projects_root"]).resolve()

def is_project_dir(d: pathlib.Path) -> bool:
    return d.is_dir() and (d / "state.md").exists()

PROJECT_SCAN_SKIP={".git",".publish",".survey-tool",".pi",".agent-snapshot","node_modules","papers","codespace","__pycache__"}

def _discovered_project_paths(root, max_depth=6):
    """Recursively find projects below organizational folders such as 26-CVPR/.

    Once a project root is found we do not descend into it, which prevents generated
    snapshots containing their own state.md from appearing as duplicate projects.
    Hidden/tool, paper, code and dependency directories are also excluded.
    """
    root=root.resolve(); found=[]
    if not root.is_dir(): return found
    for current, dirs, _files in os.walk(root):
        d=pathlib.Path(current); depth=len(d.relative_to(root).parts)
        dirs[:]=[x for x in dirs if x not in PROJECT_SCAN_SKIP and not x.startswith(".")]
        if depth>0 and is_project_dir(d):
            found.append(d.resolve()); dirs[:]=[]; continue
        if depth>=max_depth: dirs[:]=[]
    return found

def known_project_paths():
    """Union of explicit registry and safe recursive projects_root discovery."""
    seen=set(); paths=[]
    for p in CFG.get("projects",[]):
        d=pathlib.Path(p).expanduser().resolve()
        if d not in seen and is_project_dir(d): seen.add(d); paths.append(d)
    for d in _discovered_project_paths(projects_root()):
        if d not in seen: seen.add(d); paths.append(d)
    return paths

def list_projects():
    root=projects_root(); rows=[]
    for d in sorted(known_project_paths(),key=lambda p:(p.name.lower(),str(p).lower())):
        try: label=str(d.relative_to(root))
        except ValueError: label=d.name
        rows.append({"name":d.name,"label":label,"path":str(d),**read_state(d)})
    return rows

def resolve_project(rel_or_name):
    """Resolve a project reference to a Path. Accepts:
      - absolute path (as-is)
      - project name (searched across the registry + projects_root scan, so nested
        projects like 26-CVPR/incontext resolve by name)
    Validates it is a project dir."""
    p = pathlib.Path(rel_or_name)
    if p.is_absolute():
        p = p.resolve()
        if is_project_dir(p): return p
        raise ValueError(f"not a research-survey project (no state.md): {p}")
    # by name: search known projects (registry + scan) so nested dirs resolve
    name = rel_or_name
    for d in known_project_paths():
        if d.name == name: return d
    # fallback: directly under projects_root
    cand = (projects_root() / name).resolve()
    if is_project_dir(cand): return cand
    raise ValueError(f"not a research-survey project (no state.md): {name}")

def tool_dir(root: pathlib.Path):
    d = root / ".survey-tool"
    (d / "papers").mkdir(parents=True, exist_ok=True)
    return d

class ToolStateCorruptionError(RuntimeError):
    pass

_state_locks_guard=threading.Lock()
_state_locks={}
_state_lock_depth=threading.local()

def _project_state_lock(root):
    key=str(pathlib.Path(root).resolve())
    with _state_locks_guard:
        return _state_locks.setdefault(key,threading.RLock())

@contextmanager
def tool_state_transaction(root):
    """Serialize one project registry transaction across HTTP threads and CLI processes."""
    root=pathlib.Path(root).resolve(); lock=_project_state_lock(root); key=str(root)
    with lock:
        depths=getattr(_state_lock_depth,"values",{})
        depth=depths.get(key,0); lock_file=None
        if depth==0:
            p=tool_dir(root)/".registry.lock"; lock_file=p.open("a+")
            if fcntl: fcntl.flock(lock_file.fileno(),fcntl.LOCK_EX)
        depths[key]=depth+1; _state_lock_depth.values=depths
        try: yield
        finally:
            depths[key]-=1
            if depths[key]==0:
                depths.pop(key,None)
                if lock_file:
                    if fcntl: fcntl.flock(lock_file.fileno(),fcntl.LOCK_UN)
                    lock_file.close()

def _read_tool_json_unlocked(root,name,default):
    p=tool_dir(root)/name
    if not p.exists(): return default
    try: return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError,UnicodeDecodeError) as e:
        stamp=datetime.datetime.now().strftime("%Y%m%dT%H%M%S%f")
        quarantine=p.with_name(f"{p.name}.corrupt-{stamp}")
        try: shutil.copy2(p,quarantine)
        except OSError: quarantine=None
        where=f"；已备份到 {quarantine}" if quarantine else ""
        raise ToolStateCorruptionError(f"工具状态损坏，拒绝按空数据继续：{p}{where}；{e}") from e

def read_tool_json(root,name,default):
    with tool_state_transaction(root): return _read_tool_json_unlocked(root,name,default)

def _write_tool_json_unlocked(root,name,data):
    p=tool_dir(root)/name; raw=json.dumps(data,ensure_ascii=False,indent=2)+"\n"
    fd,tmp=tempfile.mkstemp(prefix=f".{p.name}.",suffix=".tmp",dir=str(p.parent))
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            f.write(raw); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,p)
        try:
            dfd=os.open(str(p.parent),os.O_RDONLY); os.fsync(dfd); os.close(dfd)
        except OSError: pass
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def write_tool_json(root,name,data):
    with tool_state_transaction(root): _write_tool_json_unlocked(root,name,data)

SAFE_REGISTRY_ID=re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
DEFAULT_FORBIDDEN_OPERATIONS=["删除数据", "破坏性 Git 操作", "覆盖已有产物", "泄露密钥"]
POLICY_PRESETS={"research-safe","strict-read-mostly","custom","legacy-default"}
AGENT_ROUTE_IDS=("local_tool_edit","experiment_code_edit","lightweight_governance")
AGENT_KINDS={"codex","pi"}
DEFAULT_AGENT_ROUTING={
    "version":1,
    "routes":{
        "local_tool_edit":{"enabled":True,"agent_kind":"codex","model":"gpt-5.6-luna","fallback_agent_kind":"pi","fallback_model":""},
        "experiment_code_edit":{"enabled":True,"agent_kind":"codex","model":"gpt-5.6-sol","fallback_agent_kind":"pi","fallback_model":""},
        "lightweight_governance":{"enabled":True,"agent_kind":"codex","model":"gpt-5.6-luna","fallback_agent_kind":"pi","fallback_model":"","inherited_from":"local_tool_edit"},
    },
}

def next_object_id(rows, prefix, width=3):
    nums=[]
    for x in rows:
        m=re.match(rf"^{re.escape(prefix)}-(\d+)$",str(x.get("id","")))
        if m: nums.append(int(m.group(1)))
    return f"{prefix}-{max(nums,default=0)+1:0{width}d}"

RUN_RESULT_FIELDS={"result_analysis","key_results","metric_observations","auxiliary_metric_observations","limitations","artifacts","result_summary","audit_paths","notes"}
RUN_V2_PRIMARY_FIELDS=("research_question","purpose","method_plan","implementation_details")
# 主表只有 4 个科研槽位（上面四个）。其余字段不再进入表单，但只要有科研/执行
# 语义就仍纳入批准快照，以便事后看到“批准后改动过什么”（现在只留痕告警，不阻断）。
RUN_V2_SPEC_FIELDS={"variant","run_type",*RUN_V2_PRIMARY_FIELDS,"hypothesis","metric_plan","data_definition","data_scale","model_config","variables_controls","metric_definition","integrity_gates","acceptance_criteria","expected_outcome","conclusion_scope","claim_boundary","implementation_summary","architecture_plan","implementation_ref","workspace_id","server_id","git_commit","command","config","seed","log_path","output_dir","artifact_dir","tmux_session","metrics_path","project_dir","launcher","group_id","trial_plan","trial_manifest"}
RUN_MUTABLE_FIELDS={
    "variant","run_type","purpose","method_plan","necessity","evidence_basis","implementation_summary","implementation_details","research_question","hypothesis","metric_plan","architecture_plan","implementation_ref","result_analysis","key_results",
    "data_definition","data_scale","model_config","variables_controls","metric_definition","integrity_gates",
    "expected_outcome","acceptance_criteria","dependencies","artifacts","result_summary","limitations",
    "conclusion_scope","claim_boundary","metrics","audit_paths","notes","status","workspace_id","server_id",
    "git_commit","command","config","seed","log_path","output_dir","artifact_dir","tmux_session","metrics_path",
    "project_dir","launcher","created_by","agent_review_summary","agent_review_questions","group_id","metric_observations","auxiliary_metric_observations","steward_summary","needs_metric_registration","automation_policy","trial_plan"
}
RUN_REVIEW_MANAGED_FIELDS={
    "review_status","review_round","review_requirements","review_questions","review_history","submitted_for_review_at",
    "approved_at","approved_by","execution_authorized_at","execution_authorization_note","execution_authorization_consumed_at",
    "execution_dispatch_id","execution_dispatch_latest_status","execution_dispatch_completed_at",
    "execution_dispatch_completion_evidence","execution_dispatch_failed_at","execution_dispatch_failure"
}
RUN_SPEC_FIELDS={
    "variant","run_type","purpose","necessity","evidence_basis","implementation_summary","implementation_details",
    "data_definition","data_scale","model_config","variables_controls","metric_definition","integrity_gates",
    "expected_outcome","acceptance_criteria","dependencies","workspace_id","server_id","git_commit","command","config",
    "seed","log_path","output_dir","artifact_dir","tmux_session","metrics_path","project_dir","launcher","group_id"
}
RUN_REVIEW_TRANSITIONS={
    # 允许一步批准：草稿/退回稿也能直接批准，不再强制 submit → approve → authorize 三段。
    "draft":{"pending_review","approved"},
    "pending_review":{"changes_requested","approved"},
    "changes_requested":{"pending_review","approved"},
    "approved":{"changes_requested","approved"},
}
RUN_REVIEW_SCORE_VERSION="run-review-score/v1"  # 仅供旧存档迁移；评分机制已移除
REVIEW_AUTOMATION_POLICY_VERSION="run-review-automation/v1"
DEFAULT_REVIEW_AUTOMATION_POLICY={"enabled":False,"auto_review_on_create":False,"policy_version":REVIEW_AUTOMATION_POLICY_VERSION,"notes":""}
AGENT_RUN_CREATORS=frozenset({"terminal_pi","agent","ai_import","ai_proposal","codex","automation"})

def is_agent_run_creator(value): return str(value or "").strip().lower() in AGENT_RUN_CREATORS

DEFAULT_EXECUTION_DISPATCH_POLICY={"enabled":False,"auto_queue_on_authorize":False,"auto_deliver_on_pi_live":False,"claim_lease_minutes":30,"max_delivery_attempts":5,"notes":""}
DEFAULT_RUN_ORGANIZATION_POLICY={"enabled":True,"auto_on_create":True,"deterministic_only":True,"enqueue_ambiguous_microtask":True,"policy_version":"run-organization/v1"}

def _filled(value): return bool(str(value or "").strip())
def _contains_placeholder(value): return bool(re.search(r"待确认|待补充|unknown|tbd|todo|<[^>]*(?:待|unknown)[^>]*>",str(value or ""),re.I))

EXPERIMENT_MUTABLE_FIELDS={
    "title","objective","constraints","brief_objective","brief_constraints","kind","source_ref","evidence_refs",
    "claim_refs","workspace_id","code_repository_workspace_id","status","workflow_stage","agent_level","priority","hypothesis","success_criteria",
    "failure_criteria","schedule","variables","minimum_test","baseline","treatments","metrics","confounders","risks",
    "open_questions","budget","resources","implementation_scope","evaluation","user_answers","agent_handoff",
    "ai_review","proposal_contract","result_summary","claim_verdict","limitations","remote_experiment_dir",
    "remote_worktree","run_dir_template","log_template","output_template","metrics_template","tmux_template","launcher",
    "created_by","run_groups","metric_definitions"
}
EXPERIMENT_STAGES={
    # planning is a historical pre-staged value retained for existing projects.
    "planning":{"planning","draft","awaiting_confirmation"},
    "draft":{"draft","awaiting_confirmation"},
    "awaiting_confirmation":{"awaiting_confirmation","confirmed"},
    "confirmed":{"confirmed","runs_ready"},
    "runs_ready":{"runs_ready"},
}

RUN_PHASE_TRANSITIONS={
    "draft":{"draft","prepared","running","completed","terminal"},
    "prepared":{"prepared","running","terminal"},
    "running":{"running","completed","terminal"},
    "completed":{"completed","reviewed","terminal"},
    "terminal":{"terminal","draft","prepared"},
    "reviewed":{"reviewed"},
}

OUTBOX_SCHEMA="survey-tool.execution-outbox/v1"
OUTBOX_TERMINAL={"completed","cancelled","superseded"}
OUTBOX_DELIVERY_COOLDOWN_SECONDS=300

# ---------------------------------------------------------------------------
# state.md parser (minimal: state, iteration, blockers, next_actions)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# paper list — scan ./papers/ directly (MinerU folders + loose PDFs),
# enriched with INDEX.md metadata where available
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# paper note read/write
# ---------------------------------------------------------------------------
SEVENQ_OLD = ["① 解决了什么问题？","② 默认了哪些前提？","③ 相比已有工作的创新点？",
              "④ 实验是否足够支持结论？","⑤ 可能的反例？","⑥ 审稿人会提哪些质疑？",
              "⑦ 扩展方向 → Idea"]
SEVENQ = ["① 解决了什么问题？","② 方法具体怎么做？","③ 真正的创新点是什么？",
          "④ 实验说明了什么？","⑤ 依赖哪些前提，边界在哪里？",
          "⑥ 作为审稿人，最关键的质疑是什么？","⑦ 对当前项目有什么启发？"]

# ---------------------------------------------------------------------------
# tool-state (.survey-tool/papers/<citekey>.json)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# claims.md parser
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# idea.md parser/writer
# ---------------------------------------------------------------------------
IDEA_KEYS = ["title","hypothesis","motivation","method","key_experiments","risks","related_diff",
             "falsification","status","novelty","novelty_note","support_claims","contra_claims","sources","created","updated"]

# ---------------------------------------------------------------------------
# Obsidian-compatible canonical knowledge objects
# ---------------------------------------------------------------------------
def _yaml_scalar(value):
    return json.dumps(str(value or ""), ensure_ascii=False)

def _frontmatter(text):
    """Small YAML subset used by this tool: scalar keys and indented string lists."""
    out={}
    if not text.startswith("---\n"): return out
    end=text.find("\n---\n",4)
    if end<0: return out
    cur=None
    for line in text[4:end].splitlines():
        m=re.match(r"^([A-Za-z_][\w-]*):(?:\s*(.*))?$",line)
        if m:
            cur=m.group(1); raw=(m.group(2) or "").strip()
            if raw=="": out[cur]=[]
            else:
                try: out[cur]=json.loads(raw)
                except Exception: out[cur]=raw.strip('"\'')
        elif cur and re.match(r"^\s+-\s+",line):
            if not isinstance(out.get(cur),list): out[cur]=[]
            out[cur].append(re.sub(r"^\s+-\s+","",line).strip().strip('"\''))
    return out

def _section(text, heading):
    m=re.search(rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)",text,re.M|re.S)
    return m.group(1).strip() if m else ""

def _replace_section(text, heading, value):
    block=f"## {heading}\n\n{str(value or '').strip()}\n\n"
    pat=rf"^## {re.escape(heading)}\s*\n.*?(?=^## |\Z)"
    if re.search(pat,text,re.M|re.S): return re.sub(pat,lambda _m:block,text,count=1,flags=re.M|re.S).rstrip()+"\n"
    return text.rstrip()+"\n\n"+block

# ---------------------------------------------------------------------------
# Research Explorer canonical bridge
# ---------------------------------------------------------------------------
EXPLORATION_TARGET_TYPES={"experiment","idea","question","comparison"}
EXPLORATION_STATUSES={"active","round_running","paused","finalizing","completed","completed_with_warnings","stopped","needs_attention","expired"}
EXPLORATION_VERIFY={"verified","partial","unverified_lead","degraded"}
EXPLORATION_ID_RE=re.compile(r"^[a-z0-9][a-z0-9._-]{2,159}$",re.I)
EXPLORATION_MAX_PAYLOAD=256*1024
EXPLORATION_TRANSITIONS={
    "active":{"round_running","paused","stopped","expired"},
    "round_running":{"active","paused","needs_attention","expired","finalizing"},
    "paused":{"active","finalizing","stopped","expired"},
    "needs_attention":{"active","finalizing","stopped","expired"},
    "expired":{"finalizing"}, "stopped":{"finalizing"},
    "finalizing":{"completed","completed_with_warnings"},
    "completed":set(), "completed_with_warnings":set(),
}

EXPLORATION_GROUP={"id":"exploration-candidates","name":"自由探索候审","description":"自由探索生成的 draft Runs；需逐条人工审核，不得直接执行","color":"#7c3aed"}

# ---------------------------------------------------------------------------
# compares.json (tool-state)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# INTAKE.md parser/writer + materialize
# ---------------------------------------------------------------------------
INTAKE_FIELDS = ["repo_path","project_slug","project_name","idea","domain",
                 "target_venue","polite_email"]
INTAKE_LIST_FIELDS = ["seed_papers","constraints"]

# ---------------------------------------------------------------------------
# branch registry (.survey-tool/branches.json) — records deep-dive sessions
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# publish tracking (.survey-tool/publish.json)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# GitHub API via PAT (avoids needing gh interactive login; uses SSH for push)
# ---------------------------------------------------------------------------
import urllib.request, urllib.error
GITHUB_API="https://api.github.com"

# ---------------------------------------------------------------------------
# export project → a GitHub-ready repo copy
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# citations.md parser
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# paper artifacts: locate MinerU dir / images / md by matching INDEX title
# ---------------------------------------------------------------------------
IMG_EXT = (".png",".jpg",".jpeg",".gif",".webp")
_RPA_CACHE = {}

# ---------------------------------------------------------------------------
# github scan — read MinerU .md (esp. abstract) + raw PDF /URI annotations,
# report resolvable repos AND code-availability textual signals.
# Keyed by the same citekey the frontend uses (via read_papers dir scan),
# so papers absent from INDEX (e.g. DetPO) still map correctly.
# ---------------------------------------------------------------------------
GH_RE = re.compile(r"((?:github|gitlab|huggingface)\.co(?:m)?/[\w./-]+(?:/[\w._-]+)?)", re.I)
PDF_URI_RE = re.compile(rb'/URI\s*\(([^)]*?)\)', re.S)
# textual signals that code exists even without a URL (e.g. "open source our code on GitHub")
SIGNAL_RE = re.compile(r"((?:open[\s-]?source(?:d)?|code(?:\s+is)?\s+(?:is\s+)?(?:available|released|open)|code\s+on\s+(?:github|gitlab)|project\s+page(?:\s+is)?\s+available|will\s+(?:release|open[\s-]?source))[^.\n]{0,70})", re.I)

# ---------------------------------------------------------------------------
# Zotero integration — list collections (tree) + items, sync selected collection
# ---------------------------------------------------------------------------
import sqlite3, shutil as _shutil
ZOTERO_SCRIPT = pathlib.Path.home()/".pi"/"agent"/"skills"/"zotero-sync"/"scripts"/"zotero_sync.py"

# ---------------------------------------------------------------------------
# MinerU parsing — run `mineru` CLI on a PDF, output to papers/<stem>/hybrid_auto
# ---------------------------------------------------------------------------
MINERU_BIN = shutil.which("mineru") or "mineru"

# In-memory job store for async mineru runs: job_id -> {status, log, proc, returncode, pdf, out_dir, root}
_mineru_jobs = {}
_mineru_jobs_lock = threading.Lock()

# ---------------------------------------------------------------------------
# script runners (call research-survey scripts)
# ---------------------------------------------------------------------------
def run_script(args, cwd=None, timeout=120, stdout_limit=256 * 1024, stderr_limit=16 * 1024):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return {"returncode":r.returncode,"stdout":r.stdout[-stdout_limit:],"stderr":r.stderr[-stderr_limit:]}
    except Exception as e:
        return {"returncode":1,"stdout":"","stderr":str(e)}

def now_iso(): return datetime.datetime.now().isoformat(timespec="seconds")

# ---------------------------------------------------------------------------
# GPT collaboration + review state
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Pi RPC bridge — binds the tool to a real pi conversation (switchable)
# ---------------------------------------------------------------------------
import threading, queue
PI_BIN = shutil.which("pi") or "pi"
PI_BINDING_SCHEMA="survey-tool.pi-binding/v1"

BRIDGES = {}

# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------
import survey_tool.canonical as _canonical_domain
import survey_tool.experiments as _experiments_domain
import survey_tool.integrations as _integrations_domain
import survey_tool.pibridge as _pibridge_domain
from survey_tool.canonical import *
from survey_tool.experiments import *
from survey_tool.integrations import *
from survey_tool.pibridge import *
from survey_tool.steward_runtime import force_restart_steward_handoff, list_steward_statuses, prepare_steward_handoff, start_steward_background, steward_console, steward_status

_DOMAIN_MODULES = (
    _canonical_domain,
    _experiments_domain,
    _integrations_domain,
    _pibridge_domain,
)

def _bind_domain_function(module, name):
    target = getattr(module, name)

    @functools.wraps(target)
    def delegated(*args, **kwargs):
        return target(*args, **kwargs)

    delegated._domain_target = target
    return delegated

for _domain_module in _DOMAIN_MODULES:
    for _domain_name in _domain_module.__all__:
        if not isinstance(getattr(_domain_module, _domain_name), type):
            globals()[_domain_name] = _bind_domain_function(_domain_module, _domain_name)

def _execution_authorization_consumption_marker():
    if False:
        marker["execution_authorization_consumed_at"] = ""

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, obj=None, ctype="application/json"):
        body = b"" if obj is None else (obj if isinstance(obj,bytes) else json.dumps(obj,ensure_ascii=False).encode("utf-8"))
        self.send_response(code)
        self.send_header("Content-Type", ctype+"; charset=utf-8" if "text" in ctype or "json" in ctype else ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.wfile.write(body)
    def _body(self):
        n = int(self.headers.get("Content-Length",0))
        if not n: return {}
        raw = self.rfile.read(n).decode("utf-8")
        try: return json.loads(raw)
        except Exception: return {"_raw":raw}

    def do_GET(self):
        try: self.route_get()
        except Exception as e: self._send(500, {"error":str(e)})

    def do_POST(self):
        try: self.route_post()
        except Exception as e: self._send(500, {"error":str(e)})

    def do_PUT(self):
        try: self.route_put()
        except Exception as e: self._send(500, {"error":str(e)})

    def do_DELETE(self):
        try: self.route_post()
        except Exception as e: self._send(500, {"error":str(e)})

    # --- static files ---
    def serve_static(self, rel):
        p = (STATIC / rel).resolve()
        if not p.is_relative_to(STATIC.resolve()) or not p.exists():
            self._send(404, b"not found", "text/plain"); return
        ctype = {"html":"text/html","js":"application/javascript","css":"text/css",
                "png":"image/png","jpg":"image/jpeg","svg":"image/svg+xml",
                "woff":"font/woff","woff2":"font/woff2"}.get(p.suffix[1:],"application/octet-stream")
        self._send(200, p.read_bytes(), ctype)

    def serve_project_file(self, project, rel):
        root = resolve_project(project).resolve()
        p = (root / rel).resolve()
        if not p.exists():
            m=re.fullmatch(r"shell/06_experiments/([^/]+)/runs/([^/]+)\.md",rel)
            if m:
                run=next((x for x in experiment_data(root)["runs"] if x.get("experiment_id")==m.group(1) and x.get("id")==m.group(2)),None)
                if run and run.get("group_id"): p=(root/"shell/06_experiments"/m.group(1)/"runs"/str(run["group_id"])/f'{m.group(2)}.md').resolve()
        if not p.is_relative_to(root) or not p.exists():
            self._send(404, b"not found","text/plain"); return
        ctype = {"png":"image/png","jpg":"image/jpeg","jpeg":"image/jpeg",
                "gif":"image/gif","webp":"image/webp","md":"text/markdown",
                "pdf":"application/pdf","json":"application/json"}.get(p.suffix[1:].lower(),"application/octet-stream")
        self._send(200, p.read_bytes(), ctype)

    def _pi_stream(self, proj):
        root=resolve_project(proj); b=bridge_for(root)
        self.send_response(200)
        self.send_header("Content-Type","text/event-stream"); self.send_header("Cache-Control","no-store")
        self.send_header("Connection","keep-alive"); self.end_headers()
        last=0
        def w(data): self.wfile.write(data); self.wfile.flush()
        w(b": ping\n\n")
        import time
        end=time.time()+600
        while time.time()<end:
            with b.event_cv:
                b.event_cv.wait(timeout=15)
                new=[e for e in b.events if e["_seq"]>last]
            for e in new:
                last=e["_seq"]
                w(("data: "+json.dumps(e,ensure_ascii=False)+"\n\n").encode("utf-8"))
            if not new: w(b": ping\n\n")
        return

    # --- routing ---
    def _v2_deps(self):
        return {
            "request_path":self.path,"resolve_project":resolve_project,"v2_capabilities":v2_capabilities,
            "public_herdr_launch_request":public_herdr_launch_request,"public_herdr_execution":public_herdr_execution,
            "public_herdr_execution_event":public_herdr_execution_event,"public_agent_session":public_agent_session,
            "current_pi_binding_summary":current_pi_binding_summary,"build_migration_inventory":build_migration_inventory,
            "build_identity_index_plan":build_identity_index_plan,"identity_index_history":identity_index_history,
            "build_content_index_plan":build_content_index_plan,"content_index_history":content_index_history,
            "create_question":create_question,"refresh_v2_index":refresh_v2_index,"read_compares":read_compares,
            "_stable_slug":_stable_slug,"save_compares":save_compares,"ensure_finding_ids":ensure_finding_ids,
            "_comparison_path":_comparison_path,"_finding_path":_finding_path,
            "citekey_for":citekey_for,"apply_identity_index_migration":apply_identity_index_migration,
            "apply_content_index_migration":apply_content_index_migration,"read_pi_binding":read_pi_binding,
            "ensure_v2_binding_target":ensure_v2_binding_target,"BRIDGES":BRIDGES,"paper_skill_script":paper_skill_script,
            "run_script":run_script,"ingest_staged_candidate":ingest_staged_candidate,"questions_dir":questions_dir,
            "read_questions":read_questions,"now_iso":now_iso,"save_question":save_question,
            "generate_obsidian_indexes":generate_obsidian_indexes,
            "read_ideas":read_ideas,"append_idea":append_idea,"update_idea":update_idea,
            "idea_canonical_hash":idea_canonical_hash,"IDEA_KEYS":IDEA_KEYS,
            "read_intake":read_intake,"write_intake":write_intake,"materialize":materialize,
            "intake_canonical_hash":intake_canonical_hash,"read_state":read_state,
            "INTAKE_FIELDS":INTAKE_FIELDS,"INTAKE_LIST_FIELDS":INTAKE_LIST_FIELDS,
            "note_path":note_path,"update_paper_canonical":update_paper_canonical,
            "paper_bundle":self._paper_bundle,
            "parse_gpt_response":parse_gpt_response,"SEVENQ":SEVENQ,
            "experiment_data":experiment_data,"experiment_dashboard_data":experiment_dashboard_data,
            "create_experiment":create_experiment,"update_experiment":update_experiment,"archive_experiment":archive_experiment,
            "create_run":create_run,"update_run":update_run,"archive_run":archive_run,"set_run_evidence_label":set_run_evidence_label,"review_run":review_run,"run_review_status":run_review_status,"prepare_direct_steward_run":prepare_direct_steward_run,"prepare_run_trials_for_steward":prepare_run_trials_for_steward,"restart_failed_run_execution":restart_failed_run_execution,"mark_steward_attempt_failed":mark_steward_attempt_failed,"correct_failed_run_state":correct_failed_run_state,
            "advance_run_workflow":advance_run_workflow,
            "prepare_steward_handoff":prepare_steward_handoff,"force_restart_steward_handoff":force_restart_steward_handoff,"start_steward_background":start_steward_background,"steward_status":steward_status,"list_steward_statuses":list_steward_statuses,"steward_console":steward_console,
            "apply_run_grouping":apply_run_grouping,"apply_agent_run_grouping":apply_agent_run_grouping,"RUN_MUTABLE_FIELDS":RUN_MUTABLE_FIELDS,"validate_execution_isolation":validate_execution_isolation,
            "ai_discussion_prompt":ai_discussion_prompt,"ai_run_grouping_prompt":ai_run_grouping_prompt,"research_object_discussion_prompt":research_object_discussion_prompt,
            "gpt_assistant_instruction":gpt_assistant_instruction,"linked_context_addresses":linked_context_addresses,"read_papers":read_papers,"read_claims":read_claims,
            "read_publish":read_publish,"publish_path":publish_path,"export_repo":export_repo,
            "bridge_for":bridge_for,"pi_state_payload":pi_state_payload,
            "environment_bindings":environment_bindings,"update_server_binding":update_server_binding,
            "update_workspace_binding":update_workspace_binding,"validate_environment_activation":validate_environment_activation,"zotero_collections":zotero_collections,
            "agent_routing_policy":agent_routing_policy,"write_agent_routing":write_agent_routing,
            "preview_rule_draft":preview_rule_draft,
            "organize_rule_draft":organize_rule_draft,
            "workspace_external_prompt":__import__("survey_tool.rule_drafts",fromlist=["workspace_external_prompt"]).workspace_external_prompt,
            "external_intent_preview":__import__("survey_tool.rule_drafts",fromlist=["external_intent_preview"]).external_intent_preview,
            "zotero_collection_items":zotero_collection_items,"arxiv_paper_search":arxiv_paper_search,
            "start_local_worker":start_local_worker,
        }

    def route_get(self):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query)
        path = u.path
        if path == "/" : return self.serve_static("v2/index.html")
        if path in {"/v2", "/v2/"}: return self.serve_static("v2/index.html")
        if path == "/v2/survey-tool-icon.svg": return self.serve_static("v2/survey-tool-icon.svg")
        if path.startswith("/v2/assets/"): return self.serve_static("v2/assets/" + path[len("/v2/assets/"):])
        if path in {"/static/index.html","/static/app.js","/static/style.css"}: return self._send(410,{"error":"legacy web workspace has been removed","migrated_to":"/v2/"})
        if path.startswith("/static/"): return self.serve_static(path[len("/static/"):])
        handled = v2_dispatch("GET", path, None, self._v2_deps())
        if handled is not None: return self._send(handled[0],handled[1])
        m = re.match(r"^/file/([^/]+)/(.+)$", path)
        if m: return self.serve_project_file(urllib.parse.unquote(m.group(1)), urllib.parse.unquote(m.group(2)))
        if path == "/api/config": return self._send(200, {"projects_root":str(projects_root()),"skill_dir":str(SKILL),"tool_root":str(HERE),"surveyctl":str(HERE/"surveyctl.py")})
        if path == "/api/projects": return self._send(200, list_projects())
        m = re.match(r"^/api/p/([^/]+)$", path)
        if m:
            root = resolve_project(urllib.parse.unquote(m.group(1)))
            return self._send(200, {"name":root.name,"path":str(root),
                "state":read_state(root),"counts":self._counts(root),
                "citations":read_citations(root)})
        m = re.match(r"^/api/p/([^/]+)/intake$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            return self._send(200, read_intake(root))
        m = re.match(r"^/api/p/([^/]+)/publish$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            return self._send(200, read_publish(root))
        m = re.match(r"^/api/p/([^/]+)/pi/sessions$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            b=bridge_for(root)
            sess=list_sessions(root, b.session_file)
            for x in sess: x["category"]=_session_category(x, state.project if False else root.name)
            return self._send(200, sess)
        m = re.match(r"^/api/p/([^/]+)/pi/models$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            return self._send(200, {"models":bridge_for(root).get_models()})
        m = re.match(r"^/api/p/([^/]+)/pi/messages$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            bridge=bridge_for(root)
            if not bridge.proc or bridge.proc.poll() is not None: return self._send(409,{"error":"pi binding is persisted but not live; restore first","reason":"offline"})
            return self._send(200, {"messages":bridge.messages()})
        m = re.match(r"^/api/p/([^/]+)/zotero/collections$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            return self._send(200, zotero_collections(root))
        m = re.match(r"^/api/p/([^/]+)/zotero/collection-items/(\d+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            return self._send(200, zotero_collection_items(root,int(m.group(2)),recursive=True))
        m = re.match(r"^/api/p/([^/]+)/papers/web-search$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); query=(q.get("q") or [""])[0].strip()
            if not query: return self._send(400,{"error":"请输入检索词","hits":[]})
            return self._send(200,web_paper_search(root,query,10))
        m = re.match(r"^/api/p/([^/]+)/mineru/status$", path)
        if m:
            return self._send(200, mineru_status())
        m = re.match(r"^/api/p/([^/]+)/mineru/job/(.+)$", path)
        if m:
            return self._send(200, mineru_job_status(m.group(2)))
        m = re.match(r"^/api/p/([^/]+)/pi/state$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            return self._send(200,pi_state_payload(root))
        m = re.match(r"^/api/p/([^/]+)/execution-outbox$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); return self._send(200,execution_outbox_public(root))
        m = re.match(r"^/api/p/([^/]+)/execution-outbox/reconcile$", path)
        if m: root=resolve_project(urllib.parse.unquote(m.group(1))); return self._send(200,reconcile_execution_outbox(root,(q.get("experiment_id") or [""])[0],True))
        m = re.match(r"^/api/p/([^/]+)/governance-tasks$", path)
        if m: root=resolve_project(urllib.parse.unquote(m.group(1))); return self._send(200,governance_task_public(root))
        m = re.match(r"^/api/p/([^/]+)/governance-tasks/([^/]+)/prompt$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            try: return self._send(200,governance_task_prompt(root,urllib.parse.unquote(m.group(2))))
            except ValueError as e: return self._send(404,{"error":str(e)})
        m = re.match(r"^/api/p/([^/]+)/execution-outbox/([^/]+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); did=urllib.parse.unquote(m.group(2)); item=next((x for x in execution_outbox_public(root)["execution_outbox"]["items"] if x.get("dispatch_id")==did),None)
            return self._send(200 if item else 404,{"dispatch":item} if item else {"error":"dispatch 不存在"})
        m = re.match(r"^/api/p/([^/]+)/pi/stream$", path)
        if m:
            return self._pi_stream(urllib.parse.unquote(m.group(1)))
        m = re.match(r"^/api/p/([^/]+)/papers$", path)
        if m: root=resolve_project(urllib.parse.unquote(m.group(1))); return self._send(200, read_papers(root))
        m = re.match(r"^/api/p/([^/]+)/paper/([^/]+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); ck=urllib.parse.unquote(m.group(2))
            return self._send(200, self._paper_bundle(root, ck))
        m = re.match(r"^/api/p/([^/]+)/claims$", path)
        if m: root=resolve_project(urllib.parse.unquote(m.group(1))); return self._send(200, read_claims(root))
        m = re.match(r"^/api/p/([^/]+)/ideas$", path)
        if m: root=resolve_project(urllib.parse.unquote(m.group(1))); return self._send(200, read_ideas(root))
        m = re.match(r"^/api/p/([^/]+)/compares$", path)
        if m: root=resolve_project(urllib.parse.unquote(m.group(1))); return self._send(200, read_compares(root))
        m = re.match(r"^/api/p/([^/]+)/questions$", path)
        if m: root=resolve_project(urllib.parse.unquote(m.group(1))); return self._send(200, read_questions(root))
        m = re.match(r"^/api/p/([^/]+)/explorations$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); return self._send(200,exploration_public(root,(q.get("target_type") or [""])[0],(q.get("target_id") or [""])[0]))
        m = re.match(r"^/api/p/([^/]+)/obsidian$", path)
        if m: root=resolve_project(urllib.parse.unquote(m.group(1))); return self._send(200, obsidian_info(root))
        m = re.match(r"^/api/p/([^/]+)/object-path/([^/]+)/([^/]+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); p=object_path(root,urllib.parse.unquote(m.group(2)),urllib.parse.unquote(m.group(3)))
            return self._send(200,{"path":str(p),"relative_path":str(p.relative_to(root)),"exists":p.exists(),"obsidian":obsidian_info(root)})
        m = re.match(r"^/api/p/([^/]+)/experiments$", path)
        if m: root=resolve_project(urllib.parse.unquote(m.group(1))); return self._send(200, experiment_dashboard_data(root))
        m = re.match(r"^/api/p/([^/]+)/agent-routing$", path)
        if m: root=resolve_project(urllib.parse.unquote(m.group(1))); return self._send(200,agent_routing_policy(root))
        m = re.match(r"^/api/p/([^/]+)/experiment/([^/]+)/(?:context|constraints)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            try: return self._send(200,experiment_constraints(root,urllib.parse.unquote(m.group(2))))
            except ValueError as e: return self._send(404,{"error":str(e)})
        m = re.match(r"^/api/p/([^/]+)/branches$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            return self._send(200,{"branches":read_branches(root),"sessions":list_sessions(root)})
        m = re.match(r"^/api/p/([^/]+)/citations$", path)
        if m: root=resolve_project(urllib.parse.unquote(m.group(1))); return self._send(200, read_citations(root))
        m = re.match(r"^/api/p/([^/]+)/images/([^/]+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); ck=urllib.parse.unquote(m.group(2))
            return self._send(200, list_images(root, ck))
        self._send(404, {"error":"not found","path":path})

    def _counts(self, root):
        return {"papers":len(read_papers(root)),"claims":len(read_claims(root)),
                "ideas":len(read_ideas(root)),"compares":len(read_compares(root)),
                "experiments":len(experiment_data(root)["experiments"])}

    def _paper_bundle(self, root, citekey):
        p = note_path(root, citekey)
        note_text = p.read_text(encoding="utf-8") if p.exists() else ""
        seven, annots = parse_note_sections(note_text)
        seven.update(paper_seven_meta(root, citekey))
        st = paper_state(root, citekey)
        claims = [c for c in read_claims(root) if c.get("citekey")==citekey]
        paper_row = next((pr for pr in read_papers(root) if citekey_for(pr)==citekey), None)
        md_path = _mineru_md_for_paper(root, paper_row) if paper_row else None
        pdf_path = str(root/"papers"/paper_row["file"]) if paper_row and paper_row.get("file") else ""
        return {"citekey":citekey,"note_exists":p.exists(),"note_path":str(p),
                "_canonical_rev":"sha256:"+hashlib.sha256(note_text.encode()).hexdigest(),
                "seven":seven,"annotations":annots,"state":st,"claims":claims,
                "images":list_images(root, citekey),
                "citation":read_citations(root).get(citekey,{}),
                "mineru_md":str(md_path) if md_path else "",
                "pdf_path":pdf_path}

    # --- POST ---
    def route_post(self):
        u = urllib.parse.urlparse(self.path); path = u.path; b = self._body()
        handled = v2_dispatch(self.command if self.command=="DELETE" else "POST",path,b,self._v2_deps())
        if handled is not None: return self._send(handled[0],handled[1])
        if path == "/api/projects/init":
            name = b.get("name","").strip(); slug = b.get("slug") or re.sub(r"[^a-z0-9-]+","-",name.lower()).strip("-")
            parent = pathlib.Path(b.get("parent") or CFG["projects_root"]).expanduser()
            if not slug: return self._send(400, {"error":"need name/slug"})
            root = parent / slug
            if root.exists() and any(root.iterdir()):
                return self._send(400, {"error":f"{root} not empty"})
            r = run_script([sys.executable, str(SKILL_SCRIPTS/"bootstrap.py"),"--project",str(root),"--name",name])
            if r["returncode"]==0:
                p=str(root.resolve())
                if p not in CFG.get("projects",[]): CFG.setdefault("projects",[]).append(p); save_config()
            return self._send(200 if r["returncode"]==0 else 500, {"result":r,"path":str(root)})
        if path == "/api/projects/register":
            p=pathlib.Path(b.get("path","")).expanduser().resolve()
            if not is_project_dir(p): return self._send(400, {"error":f"not a research-survey project (no state.md): {p}"})
            if str(p) not in CFG.get("projects",[]): CFG.setdefault("projects",[]).append(str(p)); save_config()
            return self._send(200, {"projects":list_projects()})
        if path == "/api/projects/unregister":
            p=str(pathlib.Path(b.get("path","")).expanduser().resolve())
            CFG["projects"]=[x for x in CFG.get("projects",[]) if x!=p]; save_config()
            return self._send(200, {"projects":list_projects()})
        m = re.match(r"^/api/p/([^/]+)/gpt/assistant$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            return self._send(200,gpt_assistant_instruction(root,b.get("objects",[]),b.get("task","review"),b.get("request",""),b.get("focus",{})))
        m = re.match(r"^/api/p/([^/]+)/gpt/parse$", path)
        if m:
            resolve_project(urllib.parse.unquote(m.group(1)))
            return self._send(200,parse_gpt_response(b.get("text",b.get("_raw",""))))
        m = re.match(r"^/api/p/([^/]+)/sync$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            col = b.get("collection","")
            out = b.get("out","papers")
            recursive = b.get("recursive",False)
            r = zotero_sync(root,col,out,recursive)
            return self._send(200, {"result":r})
        m = re.match(r"^/api/p/([^/]+)/zotero/sync$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); out=b.get("out","papers")
            if b.get("itemKeys") is not None: return self._send(200,{"result":zotero_sync_items(root,b.get("itemKeys") or [],out)})
            col=b.get("collectionId",b.get("collection","")); recursive=b.get("recursive",True)
            return self._send(200,{"result":zotero_sync(root,col,out,recursive)})
        m = re.match(r"^/api/p/([^/]+)/papers/web-import$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); return self._send(200,import_web_paper(root,b.get("paper") or {}))
        m = re.match(r"^/api/p/([^/]+)/mineru/parse$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            return self._send(200, mineru_parse(root,b.get("file","")))
        m = re.match(r"^/api/p/([^/]+)/scan-github$", path)
        if m: root=resolve_project(urllib.parse.unquote(m.group(1))); return self._send(200, scan_github(root))
        m = re.match(r"^/api/p/([^/]+)/intake$", path)
        if m:
            if blocked:=_legacy_write_blocked("intake.update"): return self._send(410,blocked)
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            write_intake(root, b.get("data",b))
            action=b.get("action","save")
            out={"saved":True}
            if action=="materialize":
                out["materialize"]=materialize(root)
                out["state"]=read_state(root)
            return self._send(200, out)
        m = re.match(r"^/api/p/([^/]+)/claims$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            cid = append_claim(root, b.get("text",""), b.get("sources",""), b.get("rationale",""), b.get("citekey",""), b.get("source_type","manual"), b.get("source_ref",""))
            return self._send(200, {"id":cid,"claims":read_claims(root)})
        m = re.match(r"^/api/p/([^/]+)/ideas$", path)
        if m:
            if blocked:=_legacy_write_blocked("idea.create"): return self._send(410,blocked)
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            iid = append_idea(root, b)
            return self._send(200, {"id":iid,"ideas":read_ideas(root)})
        m = re.match(r"^/api/p/([^/]+)/compares$", path)
        if m:
            if blocked:=_legacy_write_blocked("comparison.create"): return self._send(410,blocked)
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            data = read_compares(root)
            data.append(b.get("project",{}))
            save_compares(root, data)
            return self._send(200, data)
        m = re.match(r"^/api/p/([^/]+)/questions$", path)
        if m:
            if blocked:=_legacy_write_blocked("question.create"): return self._send(410,blocked)
            root=resolve_project(urllib.parse.unquote(m.group(1))); q=create_question(root,b)
            return self._send(200,{"question":q,"questions":read_questions(root)})
        m = re.match(r"^/api/p/([^/]+)/explorations/request$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            try:
                target=exploration_inspect_target(root,b.get("target_type"),b.get("target_id")); duration=b.get("duration_minutes"); rounds=b.get("max_rounds"); interval=b.get("interval_minutes",1)
                if duration is None and rounds is None: raise ValueError("duration_minutes/max_rounds 至少一个必填")
                for key,value,low,high in (("duration_minutes",duration,1,10080),("max_rounds",rounds,1,1000),("interval_minutes",interval,1,60)):
                    if value is not None and (type(value) is not int or not low<=value<=high): raise ValueError(f"{key} 必须是 {low}-{high} 的整数")
                args=["/explore start",f'--project-root "{root}"',f'--target-type {target["target_type"]}',f'--target-id {target["target_id"]}']
                if duration: args.append(f"--duration-minutes {int(duration)}")
                if rounds: args.append(f"--max-rounds {int(rounds)}")
                args.append(f"--interval-minutes {int(interval)}")
                command=" ".join(args); prompt=f"请加载 research-explorer skill，并在当前 terminal pi 中执行：\n{command}\n浏览器只生成协调指令，尚未启动探索。"
                return self._send(200,{"target":target,"command":command,"prompt":prompt,"started":False})
            except (ValueError,TypeError) as e: return self._send(400,{"error":str(e)})
        m = re.match(r"^/api/p/([^/]+)/obsidian/index$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); return self._send(200,generate_obsidian_indexes(root))
        m = re.match(r"^/api/p/([^/]+)/obsidian$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); cfg={"vault_name":b.get("vault_name") or root.name,"vault_path":b.get("vault_path") or str(root)}; write_tool_json(root,"obsidian.json",cfg); generate_obsidian_indexes(root); return self._send(200,obsidian_info(root))
        m = re.match(r"^/api/p/([^/]+)/experiments$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            try: exp=create_experiment(root,b)
            except ValueError as e: return self._send(400,{"error":str(e)})
            return self._send(200,{"id":exp["id"],**experiment_data(root)})
        m = re.match(r"^/api/p/([^/]+)/experiments/([^/]+)/runs$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); eid=urllib.parse.unquote(m.group(2))
            try: run=create_run(root,eid,{**b,"workflow_version":b.get("workflow_version",2)},b.get("id",""))
            except ValueError as e: return self._send(400,{"error":str(e)})
            return self._send(200,create_run_dashboard_response(root,run))
        m = re.match(r"^/api/p/([^/]+)/experiments/([^/]+)/run-grouping$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); eid=urllib.parse.unquote(m.group(2))
            try: return self._send(200,apply_run_grouping(root,eid,b.get("groups"),b.get("assignments")))
            except ValueError as e: return self._send(400,{"error":str(e)})
        m = re.match(r"^/api/p/([^/]+)/experiments/([^/]+)/agent-run-grouping$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); eid=urllib.parse.unquote(m.group(2))
            try: return self._send(200,apply_agent_run_grouping(root,eid,b.get("groups"),b.get("assignments")))
            except ValueError as e: return self._send(400,{"error":str(e)})
        m = re.match(r"^/api/p/([^/]+)/experiments/([^/]+)/review-automation-policy$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); eid=urllib.parse.unquote(m.group(2))
            try: return self._send(200,save_review_automation_policy(root,eid,b))
            except ValueError as e: return self._send(400,{"error":str(e)})
        m = re.match(r"^/api/p/([^/]+)/experiments/([^/]+)/execution-dispatch-policy$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); eid=urllib.parse.unquote(m.group(2))
            try: return self._send(200,save_execution_dispatch_policy(root,eid,b))
            except ValueError as e: return self._send(400,{"error":str(e)})
        m = re.match(r"^/api/p/([^/]+)/experiments/([^/]+)/run-organization-policy$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); eid=urllib.parse.unquote(m.group(2))
            try: return self._send(200,save_run_organization_policy(root,eid,b))
            except ValueError as e: return self._send(400,{"error":str(e)})
        m = re.match(r"^/api/p/([^/]+)/execution-outbox/reconcile$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); return self._send(200,reconcile_execution_outbox(root,b.get("experiment_id","") ,False))
        m = re.match(r"^/api/p/([^/]+)/agent/route-event$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            try: return self._send(200,record_agent_route_event(root,b))
            except ValueError as e: return self._send(400,{"error":str(e)})
        m = re.match(r"^/api/p/([^/]+)/governance-tasks/claim-next$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            try: return self._send(200,claim_governance_task(root,b.get("consumer")))
            except ValueError as e: return self._send(400,{"error":str(e)})
        m = re.match(r"^/api/p/([^/]+)/governance-tasks/([^/]+)/(complete|fail)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); task_id=urllib.parse.unquote(m.group(2))
            try:
                if m.group(3)=="complete": out=complete_governance_task(root,task_id,b.get("lease_token"),b.get("consumer"),b.get("group_id","") ,b.get("reason",""))
                else: out=fail_governance_task(root,task_id,b.get("lease_token"),b.get("consumer"),b.get("reason",""))
                return self._send(200,{"task":out})
            except ValueError as e: return self._send(400,{"error":str(e)})
        m = re.match(r"^/api/p/([^/]+)/runs/([^/]+)/execution-outbox/enqueue$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); rid=urllib.parse.unquote(m.group(2))
            try:
                result=enqueue_execution(root,rid); return self._send(200,{**experiment_dashboard_data(root),"enqueue_result":result})
            except ValueError as e: return self._send(400,{"error":str(e)})
        m = re.match(r"^/api/p/([^/]+)/execution-outbox/claim-next$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            try: return self._send(200,claim_next_execution(root,b.get("consumer"),b.get("experiment_id","")))
            except ValueError as e: return self._send(400,{"error":str(e)})
        m = re.match(r"^/api/p/([^/]+)/execution-outbox/([^/]+)/(ack|running|complete|fail|retry|release)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); did=urllib.parse.unquote(m.group(2)); action=m.group(3)
            try:
                if action=="ack": out=_leased_transition(root,did,b.get("lease_token"),b.get("consumer"),"acknowledge",b)
                elif action=="running": out=_leased_transition(root,did,b.get("lease_token"),b.get("consumer"),"running",b)
                elif action=="complete": out=_leased_transition(root,did,b.get("lease_token"),b.get("consumer"),"complete",b)
                elif action=="fail": out=_leased_transition(root,did,b.get("lease_token"),b.get("consumer"),"fail",b)
                elif action=="retry": out=retry_execution(root,did,b.get("reason"),b.get("evidence"))
                elif action=="release": out=release_execution(root,did,b.get("lease_token"),b.get("consumer"),b.get("reason","released"))
                return self._send(200,{"dispatch":out})
            except ValueError as e: return self._send(400,{"error":str(e)})
        m = re.match(r"^/api/p/([^/]+)/pi/dispatch-pending$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); return self._send(200,dispatch_pending_to_live_pi(root,explicit=True,force=b.get("force") is True))
        m = re.match(r"^/api/p/([^/]+)/experiments/([^/]+)/auto-review$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); eid=urllib.parse.unquote(m.group(2))
            try: return self._send(200,auto_review_experiment(root,eid))
            except ValueError as e: return self._send(400,{"error":str(e)})
        m = re.match(r"^/api/p/([^/]+)/runs/([^/]+)/auto-review$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); rid=urllib.parse.unquote(m.group(2))
            try:
                result=auto_review_run(root,rid); return self._send(200,{**experiment_dashboard_data(root),"auto_review_result":result})
            except ValueError as e: return self._send(400,{"error":str(e)})
        m = re.match(r"^/api/p/([^/]+)/agent-routing$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            try: return self._send(200,write_agent_routing(root,b))
            except ValueError as e: return self._send(400,{"error":str(e)})
        m = re.match(r"^/api/p/([^/]+)/(machines|servers)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); data=experiment_data(root)
            server=dict(b); server["id"]=server.get("id") or next_object_id(data["servers"],"S",2)
            data["servers"]=[x for x in data["servers"] if x.get("id")!=server["id"]]+[server]
            write_tool_json(root,"servers.json",data["servers"]); return self._send(200,experiment_data(root))
        m = re.match(r"^/api/p/([^/]+)/workspaces$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); data=experiment_data(root)
            wid=b.get("id") or next_object_id(data["workspaces"],"W",2); existing=next((x for x in data["workspaces"] if x.get("id")==wid),{})
            ws={**existing,**dict(b),"id":wid}
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}",str(ws["id"])): return self._send(400,{"error":"Workspace ID 不安全"})
            try:
                if "environment_activation" in b: ws["environment_activation"]=validate_environment_activation(ws.get("environment_activation"))
                if "environment_policy" in b: ws["environment_policy"]=validate_workspace_policy(ws,b["environment_policy"])
                else: ws["environment_policy"]=workspace_policy(ws)
            except ValueError as e: return self._send(400,{"error":str(e)})
            data["workspaces"]=[x for x in data["workspaces"] if x.get("id")!=ws["id"]]+[ws]
            write_tool_json(root,"workspaces.json",data["workspaces"]); return self._send(200,experiment_data(root))
        m = re.match(r"^/api/p/([^/]+)/runs/([^/]+)/workflow$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); rid=urllib.parse.unquote(m.group(2))
            try: return self._send(200,advance_run_workflow(root,rid,b.get("action",""),"human",{k:b[k] for k in ("result_analysis","key_results","metric_observations","limitations","artifacts") if k in b}))
            except ValueError as e: return self._send(400,{"error":str(e),**experiment_dashboard_data(root)})
        m = re.match(r"^/api/p/([^/]+)/runs/([^/]+)/review$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); rid=urllib.parse.unquote(m.group(2))
            try:
                review_run(root,rid,b.get("action",""),b.get("requirements",""),b.get("questions",""),"human",b.get("authorization_note",""))
                return self._send(200,experiment_dashboard_data(root))
            except ValueError as e: return self._send(400,{"error":str(e),**experiment_dashboard_data(root)})
        m = re.match(r"^/api/p/([^/]+)/runs/([^/]+)/activate$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            try: return self._send(200,activate_run(root,urllib.parse.unquote(m.group(2))))
            except ValueError as e: return self._send(400,{"error":str(e),**experiment_data(root)})
        m = re.match(r"^/api/p/([^/]+)/branches$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            if self.command=="POST":
                return self._send(200, add_branch(root, b.get("rec",b)))
            return self._send(200, {"branches":read_branches(root), "sessions":list_sessions(root)})
        m = re.match(r"^/api/p/([^/]+)/branches/([^/]+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            bid=urllib.parse.unquote(m.group(2))
            if bid=="prune" and self.command=="DELETE":
                return self._send(200, {"branches":prune_branches(root)})
            if self.command=="DELETE":
                data=[x for x in read_branches(root) if x.get("id")!=bid]
                save_branches(root, data); return self._send(200, {"branches":data})
            return self._send(404, {"error":"unknown branch action"})
        m = re.match(r"^/api/p/([^/]+)/export$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            pub=read_publish(root)
            dest = b.get("dest") or str(publish_path(root))
            opts={"includePdfs":b.get("includePdfs",True),"includeMinerU":b.get("includeMinerU",True),
                  "includeToolState":b.get("includeToolState",True),"initGit":b.get("initGit",True),
                  "pushGithub":b.get("pushGithub",False),"repoName":b.get("repoName") or pub.get("name"),
                  "visibility":b.get("visibility","private"),"githubToken":b.get("githubToken")}
            res=export_repo(root, dest, opts)
            # if not pushing, but a remote is remembered, push to it (re-sync)
            if not opts.get("pushGithub") and pub.get("remote") and pathlib.Path(dest,".git").exists():
                pr=run_script(["git","push","origin","HEAD"], cwd=str(dest))
                res["sync_push"]=pr.get("returncode")==0; res["githubUrl"]=pub.get("githubUrl","")
            res["publish"]=read_publish(root)
            return self._send(200, res)
        m = re.match(r"^/api/p/([^/]+)/pi/restore$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); br=bridge_for(root); resolved=resolve_persisted_session(root)
            if not resolved.get("ok"): return self._send(409,resolved)
            try: r=br.start(resolved["path"])
            except ValueError as exc: return self._send(400,{"ok":False,"reason":"invalid_path","error":str(exc)})
            st=br.state() if r.get("ok") else None
            if st:
                persist_bridge_state(root,br,st); r.update(pi_state_payload(root,br)); r["dispatch_result"]=dispatch_pending_to_live_pi(root,br)
            return self._send(200 if r.get("ok") else 409,r)
        m = re.match(r"^/api/p/([^/]+)/pi/(bind|prompt|steer|abort|switch|new|clone|set_name|set_model|messages|last_text|models)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); action=m.group(2)
            br=bridge_for(root)
            if action=="bind":
                session=b.get("session","continue")
                if session=="persisted":
                    resolved=resolve_persisted_session(root)
                    if not resolved.get("ok"): return self._send(409,resolved)
                    session=resolved["path"]
                try: r=br.start(session)
                except ValueError as exc: return self._send(400,{"ok":False,"reason":"invalid_path","error":str(exc)})
                # always refresh state so name/topic are current (even if already running)
                st=br.state()
                if st:
                    r["state"]=st; br.session_file=st.get("sessionFile"); br.session_name=st.get("sessionName")
                    persist_bridge_state(root,br,st,new_binding=True)
                if br.session_file:
                    r["topic"]=_session_meta(_safe_session_path(br.session_file))["topic"]
                r["sessions"]=list_sessions(root, br.session_file)
                if st: r["dispatch_result"]=dispatch_pending_to_live_pi(root,br)
                return self._send(200, r)
            if not br.proc or br.proc.poll() is not None:
                return self._send(409,{"success":False,"reason":"offline","error":"pi 未实时绑定；请先恢复或绑定对话"})
            if action=="prompt":
                r=br.prompt(b.get("message","")); return self._send(200, r)
            if action=="steer":
                r=br.steer(b.get("message","")); return self._send(200, r)
            if action=="abort":
                return self._send(200, br.abort())
            if action=="switch":
                try: path=str(_safe_session_path(b.get("sessionPath","")))
                except ValueError as exc: return self._send(400,{"success":False,"reason":"invalid_path","error":str(exc)})
                r=br.switch(path)
                if r.get("success"): persist_bridge_state(root,br,new_binding=True)
                return self._send(200, r)
            if action=="new":
                r=br.new()
                if r.get("success"): persist_bridge_state(root,br,new_binding=True)
                return self._send(200, r)
            if action=="models":
                return self._send(200, {"models":br.get_models()})
            if action=="set_model":
                return self._send(200, br.set_model(b.get("provider",""), b.get("modelId","")))
            if action=="clone":
                r=br.clone()
                if r.get("success"): persist_bridge_state(root,br,new_binding=True)
                return self._send(200, r)
            if action=="set_name":
                r=br.set_name(b.get("name",""))
                if r.get("success"): persist_bridge_state(root,br,r.get("state"))
                return self._send(200, r)
            if action=="messages":
                return self._send(200, {"messages":br.messages()})
            if action=="last_text":
                r=br.send({"type":"get_last_assistant_text"}, timeout=10)
                return self._send(200, r.get("data",{}) if r.get("success") else {"text":""})
        self._send(404, {"error":"not found","path":path})

    # --- PUT ---
    def route_put(self):
        u = urllib.parse.urlparse(self.path); path = u.path; b = self._body()
        handled = v2_dispatch("PUT",path,b,self._v2_deps())
        if handled is not None: return self._send(handled[0],handled[1])
        m = re.match(r"^/api/p/([^/]+)/paper/([^/]+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); ck=urllib.parse.unquote(m.group(2))
            if blocked:=_legacy_write_blocked("paper.update"): return self._send(410,blocked)
            update_paper_canonical(root,ck,b)
            return self._send(200, self._paper_bundle(root, ck))
        m = re.match(r"^/api/p/([^/]+)/claim/(C\d+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            update_claim(root, m.group(2), b.get("fields",{}))
            return self._send(200, {"claims":read_claims(root)})
        m = re.match(r"^/api/p/([^/]+)/idea/(I-\d+)$", path)
        if m:
            if blocked:=_legacy_write_blocked("idea.update"): return self._send(410,blocked)
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            update_idea(root, m.group(2), b.get("fields",{}))
            return self._send(200, {"ideas":read_ideas(root)})
        m = re.match(r"^/api/p/([^/]+)/compares$", path)
        if m:
            if blocked:=_legacy_write_blocked("comparison.replace"): return self._send(410,blocked)
            root=resolve_project(urllib.parse.unquote(m.group(1)))
            save_compares(root, b.get("compares",[]))
            return self._send(200, read_compares(root))
        m = re.match(r"^/api/p/([^/]+)/question/(Q-\d+)$", path)
        if m:
            if blocked:=_legacy_write_blocked("question.update"): return self._send(410,blocked)
            root=resolve_project(urllib.parse.unquote(m.group(1))); old=next((x for x in read_questions(root) if x.get("id")==m.group(2)),None)
            if not old: return self._send(404,{"error":"question not found"})
            q={**old,**b.get("fields",{})}; q["id"]=old["id"]; q["updated"]=now_iso(); save_question(root,q,old); generate_obsidian_indexes(root)
            return self._send(200,{"question":q,"questions":read_questions(root)})
        m = re.match(r"^/api/p/([^/]+)/experiment/(E-\d+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); eid=m.group(2)
            try: update_experiment(root,eid,b.get("fields",{}))
            except ValueError as e: return self._send(400,{"error":str(e)})
            return self._send(200,experiment_data(root))
        m = re.match(r"^/api/p/([^/]+)/run/([^/]+)$", path)
        if m:
            root=resolve_project(urllib.parse.unquote(m.group(1))); rid=urllib.parse.unquote(m.group(2)); data=experiment_data(root)
            if not any(x.get("id")==rid for x in data["runs"]): return self._send(404,{"error":"run not found"})
            try: update_run(root,rid,b.get("fields",{}))
            except ValueError as e: return self._send(400,{"error":str(e)})
            return self._send(200,experiment_data(root))
        self._send(404, {"error":"not found","path":path})

# ---------------------------------------------------------------------------
def main():
    global CFG, SKILL, SKILL_SCRIPTS
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int)
    ap.add_argument("--root")
    ap.add_argument("--skill")
    args = ap.parse_args()
    CFG = load_config()
    if args.port: CFG["port"]=args.port
    if args.root: CFG["projects_root"]=args.root
    if args.skill: CFG["skill_dir"]=args.skill
    SKILL = pathlib.Path(CFG["skill_dir"]).resolve()
    SKILL_SCRIPTS = SKILL / "scripts"
    port = CFG["port"]
    # ensure static exists
    if not STATIC.exists():
        print(f"[err] static dir missing: {STATIC}", file=sys.stderr); sys.exit(1)
    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    print(f"survey-tool → http://127.0.0.1:{port}")
    print(f"  projects_root: {CFG['projects_root']}")
    print(f"  skill_dir:    {SKILL}")
    try: srv.serve_forever()
    except KeyboardInterrupt: print("\nbye")

if __name__ == "__main__":
    main()
