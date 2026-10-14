"""Pibridge domain extracted from the legacy HTTP server."""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import secrets
import selectors
import shlex
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import uuid
from contextlib import contextmanager

import server
from server import PI_BIN, PI_BINDING_SCHEMA, now_iso, read_tool_json, write_tool_json
from survey_tool.canonical import read_questions
from survey_tool.experiments import experiment_data
import queue

__all__ = [
    "pi_sessions_root",
    "_canonical_path",
    "_safe_session_path",
    "read_pi_binding",
    "write_pi_binding",
    "session_dir_for",
    "PiBridge",
    "bridge_for",
    "_session_meta",
    "_session_category",
    "_session_files",
    "resolve_persisted_session",
    "list_sessions",
    "persist_bridge_state",
    "pi_state_payload",
    "public_agent_session",
    "public_herdr_launch_request",
    "public_herdr_execution",
    "public_herdr_execution_event",
    "current_pi_binding_summary",
    "ensure_v2_binding_target"
]

def pi_sessions_root(): return pathlib.Path.home()/".pi"/"agent"/"sessions"

def _canonical_path(value):
    try: return str(pathlib.Path(value).expanduser().resolve())
    except Exception: return str(pathlib.Path(value).expanduser().absolute())

def _safe_session_path(value, must_exist=True):
    if not value: raise ValueError("missing: session path 为空")
    path=pathlib.Path(value).expanduser()
    if must_exist and not path.is_file(): raise ValueError(f"missing: session 文件不存在：{path}")
    resolved=path.resolve(strict=must_exist)
    root=server.pi_sessions_root().resolve()
    try: resolved.relative_to(root)
    except ValueError: raise ValueError("invalid_path: session 文件必须位于 ~/.pi/agent/sessions 内")
    if resolved.suffix!=".jsonl": raise ValueError("invalid_path: session 文件必须是 .jsonl")
    return resolved

def read_pi_binding(root):
    value=read_tool_json(pathlib.Path(root).resolve(),"pi-binding.json",{})
    if not isinstance(value,dict) or value.get("schema")!=PI_BINDING_SCHEMA: return {}
    if value.get("project")!=_canonical_path(root): return {}
    return value

def write_pi_binding(root,meta,bound_at=""):
    root=pathlib.Path(root).resolve(); old=read_pi_binding(root); now=now_iso()
    snapshot={"schema":PI_BINDING_SCHEMA,"version":1,"project":str(root),"session_file":str(meta.get("path") or ""),"session_id":str(meta.get("sessionId") or ""),"session_name":meta.get("name") or "","topic":meta.get("topic") or "","bound_at":bound_at or old.get("bound_at") or now,"updated_at":now,"last_verified_at":now}
    write_tool_json(root,"pi-binding.json",snapshot); return snapshot

def session_dir_for(cwd: str) -> pathlib.Path:
    """pi stores sessions at ~/.pi/agent/sessions/--<cwd-with-slashes-as-dashes>--/"""
    enc = "--" + str(cwd).replace("/", "-").lstrip("-") + "--"
    return pathlib.Path.home() / ".pi" / "agent" / "sessions" / enc

class PiBridge:
    """One bound pi RPC conversation for a project cwd."""
    def __init__(self, cwd):
        self.cwd = _canonical_path(cwd)
        self.proc = None
        self._lock = threading.Lock()
        self._completion_lock = threading.Lock()
        self._completion_pending = False
        self._pending = {}            # id -> queue.Queue for response
        self._seq = 0
        self.events = []               # rolling buffer of events for SSE
        self.event_cv = threading.Condition()
        self.session_file = None
        self.session_name = None
        self.is_streaming = False
        self._cur_text = ""            # accumulating assistant text for current turn
        snapshot=read_pi_binding(pathlib.Path(self.cwd))
        self.session_file=snapshot.get("session_file") or None
        self.session_name=snapshot.get("session_name") or None

    def start(self, session=None):
        if self.proc and self.proc.poll() is None:
            return {"ok":True,"note":"already running"}
        args = [PI_BIN, "--mode", "rpc", "--name", pathlib.Path(self.cwd).name]
        # choose session target via CLI flags
        if session == "continue":
            args += ["-c"]                      # resume most-recent session in this cwd
        elif session and session not in ("new", None):
            args += ["--session", str(_safe_session_path(session))]  # bind to a validated session file
        # session == "new" or None → fresh session (no flag)
        self.proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL, text=True, bufsize=1, cwd=self.cwd)
        t = threading.Thread(target=self._reader, daemon=True); t.start()
        st = self.send({"type":"get_state"}, timeout=12)
        if not st or not st.get("success"):
            return {"ok":False,"error":"pi did not respond","raw":st}
        data = st.get("data",{})
        self.session_file = data.get("sessionFile")
        self.session_name = data.get("sessionName")
        if session == "new":
            # ensure truly fresh even if -c semantics differ
            self.send({"type":"new_session"}, timeout=10)
            st2 = self.send({"type":"get_state"}, timeout=5)
            if st2.get("success"):
                self.session_file = st2["data"].get("sessionFile"); self.session_name = st2["data"].get("sessionName")
        return {"ok":True,"state":data}

    def _reader(self):
        for line in self.proc.stdout:
            line=line.rstrip("\n")
            if line.endswith("\r"): line=line[:-1]
            if not line.strip(): continue
            try: obj=json.loads(line)
            except Exception: continue
            if obj.get("type")=="response" and "id" in obj:
                q=self._pending.pop(obj["id"],None)
                if q: q.put(obj)
            else:
                self._handle_event(obj)

    def _handle_event(self, ev):
        t=ev.get("type")
        if t=="agent_start": self.is_streaming=True; self._cur_text=""
        elif t=="agent_end": self.is_streaming=False
        elif t=="message_update":
            d=ev.get("assistantMessageEvent",{})
            if d.get("type")=="text_delta": self._cur_text+=d.get("delta","")
        with self.event_cv:
            self._seq+=1
            ev2=dict(ev); ev2["_seq"]=self._seq
            if t=="message_update" and ev.get("assistantMessageEvent",{}).get("type")=="text_delta":
                ev2["_text_so_far"]=self._cur_text
            self.events.append(ev2)
            if len(self.events)>500: self.events=self.events[-500:]
            self.event_cv.notify_all()

    def send(self, cmd, timeout=30):
        with self._lock:
            cid="r"+str(self._seq2())
            cmd=dict(cmd); cmd["id"]=cid
            q=queue.Queue(); self._pending[cid]=q
            try:
                self.proc.stdin.write(json.dumps(cmd)+"\n"); self.proc.stdin.flush()
            except Exception as e:
                self._pending.pop(cid,None); return {"success":False,"error":str(e)}
        try: return q.get(timeout=timeout)
        except Exception: self._pending.pop(cid,None); return {"success":False,"error":"timeout"}
    _c=0
    def _seq2(self):
        PiBridge._c+=1; return PiBridge._c

    def prompt(self, msg):
        if self._completion_pending: return {"success":False,"error":"completion already pending"}
        return self.send({"type":"prompt","message":msg}, timeout=15)
    def prompt_completion(self, msg, timeout=90):
        """Submit one prompt and wait for its agent_start/agent_end text events."""
        timeout=max(1,min(float(timeout),120))
        if not self._completion_lock.acquire(blocking=False): return {"success":False,"error":"completion already pending"}
        try:
            if not self.proc or self.proc.poll() is not None: return {"success":False,"error":"pi offline"}
            if self.is_streaming: return {"success":False,"error":"pi already streaming"}
            self._completion_pending=True
            with self.event_cv: start_seq=self._seq
            response=self.send({"type":"prompt","message":msg},timeout=15)
            if not response or not response.get("success"): return {"success":False,"error":str((response or {}).get("error") or "prompt rejected")}
            deadline=time.monotonic()+timeout; cursor=start_seq; started=False; chunks=[]
            while True:
                with self.event_cv:
                    events=[event for event in self.events if event.get("_seq",0)>cursor]
                    if not events:
                        remaining=deadline-time.monotonic()
                        if remaining<=0: return {"success":False,"error":"completion timeout"}
                        self.event_cv.wait(timeout=remaining); continue
                for event in events:
                    cursor=max(cursor,event.get("_seq",0)); kind=event.get("type")
                    if kind=="agent_start": started=True; chunks=[]
                    elif started and kind=="message_update":
                        delta=event.get("assistantMessageEvent",{})
                        if delta.get("type")=="text_delta": chunks.append(str(delta.get("delta") or ""))
                    elif started and kind=="agent_end": return {"success":True,"text":"".join(chunks)}
                if time.monotonic()>=deadline: return {"success":False,"error":"completion timeout"}
        finally: self._completion_pending=False; self._completion_lock.release()
    def steer(self, msg):
        return self.send({"type":"steer","message":msg}, timeout=15)
    def abort(self):
        return self.send({"type":"abort"}, timeout=10)
    def state(self):
        r=self.send({"type":"get_state"}, timeout=8)
        if r.get("success"):
            d=r["data"]; self.session_file=d.get("sessionFile"); self.session_name=d.get("sessionName"); self.is_streaming=d.get("isStreaming",False)
            return d
        return None
    def switch(self, path):
        r=self.send({"type":"switch_session","sessionPath":path}, timeout=10)
        if r.get("success"): self.state()
        return r
    def new(self):
        r=self.send({"type":"new_session"}, timeout=10)
        if r.get("success"): self.state()
        return r
    def clone(self):
        r=self.send({"type":"clone"}, timeout=15)
        if r.get("success"): self.state()
        return r
    def set_name(self, name):
        r=self.send({"type":"set_session_name","name":name}, timeout=8)
        if r.get("success"): r["state"]=self.state()
        return r
    def get_models(self):
        r=self.send({"type":"get_available_models"}, timeout=10)
        return r.get("data",{}).get("models",[]) if r.get("success") else []
    def set_model(self, provider, model_id):
        return self.send({"type":"set_model","provider":provider,"modelId":model_id}, timeout=10)
    def current_model(self):
        st=self.state(); return (st or {}).get("model")
    def messages(self):
        r=self.send({"type":"get_messages"}, timeout=10)
        return r.get("data",{}).get("messages",[]) if r.get("success") else []
    def close(self):
        try: self.proc.terminate()
        except Exception: pass

def bridge_for(root: pathlib.Path) -> PiBridge:
    key=_canonical_path(root)
    b=server.BRIDGES.get(key)
    if not b:
        b=PiBridge(root); server.BRIDGES[key]=b
    return b

def _session_meta(path: pathlib.Path):
    """Read a session.jsonl: first user message (topic), msg count, name (from /name = session_info entries)."""
    topic=""; msg_count=0; name=None; first_user=None; session_id=""; cwd=""
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try: o=json.loads(line)
                except Exception: continue
                t=o.get("type")
                if t=="session":
                    session_id=str(o.get("id") or session_id); cwd=str(o.get("cwd") or cwd)
                    name = o.get("name") or name
                elif t=="session_info":
                    # /name writes session_info entries; last one wins
                    if o.get("name"): name = o["name"]
                elif t=="message":
                    msg_count+=1
                    m=o.get("message",{})
                    if first_user is None and m.get("role")=="user":
                        c=m.get("content")
                        if isinstance(c,list):
                            c=" ".join(b.get("text","") for b in c if isinstance(b,dict) and b.get("type")=="text")
                        first_user=str(c or "").replace("\n"," ").strip()
                        topic=first_user[:90]
    except Exception:
        pass
    return {"path":str(path.resolve()),"sessionId":session_id,"cwd":cwd,"topic":topic,"msgCount":msg_count,"name":name}

def _session_category(s, proj_name):
    label = s.get("name") or s.get("topic") or ""
    # strip leading "project · " if present
    if " · " in label:
        label = label.split(" · ",1)[1]
    if label.startswith("七问"): return "七问深挖"
    if label.startswith("对比:"): return "对比"
    if label==proj_name or label.startswith("主线") or label.startswith("main"): return "主线"
    if not s.get("name"): return "未命名"
    return "其他"

def _session_files(limit=5000):
    root=server.pi_sessions_root()
    if not root.is_dir(): return []
    files=[]
    try:
        for path in root.glob("**/*.jsonl"):
            files.append(path)
            if len(files)>=limit: break
    except OSError: pass
    return files

def resolve_persisted_session(root,snapshot=None):
    root=pathlib.Path(root).resolve(); snapshot=snapshot or read_pi_binding(root)
    if not snapshot: return {"ok":False,"reason":"missing","error":"没有已保存的 pi 绑定"}
    raw=snapshot.get("session_file") or ""
    if raw:
        try:
            path=_safe_session_path(raw); meta=_session_meta(path)
            if (not snapshot.get("session_id") or meta["sessionId"]==snapshot["session_id"]) and (not meta["cwd"] or _canonical_path(meta["cwd"])==str(root)):
                return {"ok":True,"path":str(path),"meta":meta,"source":"snapshot_path"}
        except ValueError as exc:
            if str(exc).startswith("invalid_path"): return {"ok":False,"reason":"invalid_path","error":str(exc)}
    sid=str(snapshot.get("session_id") or ""); basename=pathlib.Path(raw).name if raw else ""
    candidates=[]
    for path in _session_files():
        if sid or path.name==basename:
            meta=_session_meta(path)
            if (sid and meta["sessionId"]==sid) or (not sid and path.name==basename):
                if not meta["cwd"] or _canonical_path(meta["cwd"])==str(root): candidates.append(meta)
    unique={m["path"]:m for m in candidates}
    if len(unique)==1:
        meta=next(iter(unique.values())); write_pi_binding(root,meta,snapshot.get("bound_at",""))
        return {"ok":True,"path":meta["path"],"meta":meta,"source":"session_id_or_basename"}
    if len(unique)>1: return {"ok":False,"reason":"ambiguous","error":"找到多个匹配的 pi session，拒绝随机恢复","candidates":list(unique.values())}
    # Final fallback: use the JSONL header cwd, not an encoded-directory guess.
    cwd_matches=[]
    for path in _session_files():
        meta=_session_meta(path)
        if meta["cwd"] and _canonical_path(meta["cwd"])==str(root): cwd_matches.append(meta)
    if len(cwd_matches)==1: return {"ok":True,"path":cwd_matches[0]["path"],"meta":cwd_matches[0],"source":"canonical_cwd"}
    if len(cwd_matches)>1: return {"ok":False,"reason":"ambiguous","error":"项目存在多个可恢复 session，请从列表明确选择","candidates":cwd_matches}
    return {"ok":False,"reason":"stale" if raw or sid else "missing","error":"已保存的 pi session 已丢失或不属于当前项目"}

def list_sessions(root: pathlib.Path, current_file=None):
    lexical=pathlib.Path(root).expanduser().absolute(); root=pathlib.Path(root).resolve(); snapshot=read_pi_binding(root); paths={}
    canonical=root
    for cwd in {str(lexical),str(canonical)}:
        directory=session_dir_for(cwd)
        if directory.is_dir():
            for path in directory.glob("*.jsonl"): paths[str(path.resolve())]=path.resolve()
    persisted=snapshot.get("session_file")
    if persisted:
        try:
            safe=_safe_session_path(persisted); paths[str(safe.parent)]=safe.parent
            for path in safe.parent.glob("*.jsonl"): paths[str(path.resolve())]=path.resolve()
        except ValueError: pass
    # Encoded directories vary across symlinks/pi versions; header cwd is authoritative.
    for path in _session_files():
        meta=_session_meta(path)
        if meta["cwd"] and _canonical_path(meta["cwd"])==str(root): paths[meta["path"]]=path.resolve()
    current_id=""; current_base=pathlib.Path(current_file).name if current_file else ""
    if current_file:
        try: current_id=_session_meta(_safe_session_path(current_file))["sessionId"]
        except ValueError: pass
    out=[]; seen=set()
    for path in paths.values():
        if not path.is_file() or path.suffix!=".jsonl": continue
        meta=_session_meta(path); key=meta["sessionId"] or meta["path"]
        if key in seen: continue
        seen.add(key); stat=path.stat(); is_current=bool((current_id and meta["sessionId"]==current_id) or (current_base and path.name==current_base))
        out.append({**meta,"mtime":datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),"size":stat.st_size,"isCurrent":is_current,"recoverable":True})
    return sorted(out,key=lambda x:x["mtime"],reverse=True)

def persist_bridge_state(root,bridge,state=None,new_binding=False):
    state=state or bridge.state()
    if not state or not bridge.session_file: return None
    path=_safe_session_path(bridge.session_file); meta=_session_meta(path)
    bridge.session_file=str(path); bridge.session_name=state.get("sessionName") or meta.get("name")
    meta["name"]=bridge.session_name or meta.get("name"); return write_pi_binding(root,meta,now_iso() if new_binding else "")

def pi_state_payload(root,bridge=None):
    root=pathlib.Path(root).resolve(); bridge=bridge or bridge_for(root); live=bool(bridge.proc and bridge.proc.poll() is None)
    state=bridge.state() if live else None
    snapshot=read_pi_binding(root); recovery=resolve_persisted_session(root,snapshot) if snapshot else {"ok":False,"reason":"missing"}
    if state:
        persist_bridge_state(root,bridge,state); snapshot=read_pi_binding(root)
    return {"bound":bool(state),"live_bound":bool(state),"persisted_bound":bool(snapshot),"recoverable":bool(snapshot and recovery.get("ok")),"recovery_reason":None if recovery.get("ok") else recovery.get("reason"),"recovery_candidates":recovery.get("candidates",[]),"state":state,"sessionFile":bridge.session_file if state else snapshot.get("session_file"),"sessionId":snapshot.get("session_id"),"sessionName":bridge.session_name if state else snapshot.get("session_name"),"topic":snapshot.get("topic","") ,"isStreaming":bridge.is_streaming if state else False}

def public_agent_session(row):
    value=dict(row); external=str(value.pop("external_ref","") or "")
    value["identity_fingerprint"]="sha256:"+hashlib.sha256(external.encode()).hexdigest()[:16] if external else ""
    return value

def public_herdr_launch_request(row):
    allowed={"id","lifecycle_status","revision","target_object_id","agent_kind","task_type","task_summary","safe_config","approved_at","created_at","updated_at"}
    return {key:value for key,value in dict(row).items() if key in allowed}

def public_herdr_execution(row):
    value=dict(row)
    allowed={"id","state","revision","target_object_id","approved_request_revision","not_after","attempt","safe_runtime","authorized_at","revoked_at","created_at","updated_at"}
    result={key:value for key,value in value.items() if key in allowed}
    result["launch_request_id"]=value.get("launch_request_object_id","")
    return result

def public_herdr_execution_event(row):
    allowed={"id","kind","occurred_at","from_revision","to_revision","summary","details"}
    return {key:value for key,value in dict(row).items() if key in allowed}

def current_pi_binding_summary(root):
    root=pathlib.Path(root).resolve(); snapshot=read_pi_binding(root); stable_id=str(snapshot.get("session_id") or "")
    bridge=server.BRIDGES.get(str(root)); live=bool(bridge and bridge.proc and bridge.proc.poll() is None)
    return {"available":bool(stable_id),"status":"live" if live else "stale" if stable_id else "unavailable","session_name":str(snapshot.get("session_name") or ""),"last_verified_at":str(snapshot.get("last_verified_at") or ""),"identity_fingerprint":"sha256:"+hashlib.sha256(stable_id.encode()).hexdigest()[:16] if stable_id else "","messages_exposed":False,"prompt_exposed":False,"session_path_exposed":False}

def ensure_v2_binding_target(root,store,object_id):
    object_id=str(object_id or "").strip()
    try: return store.get_object(object_id)
    except KeyError: pass
    question=next((item for item in read_questions(root) if item.get("id")==object_id),None)
    experiment_registry=experiment_data(root)
    experiment=next((item for item in experiment_registry["experiments"] if item.get("id")==object_id),None)
    run=next((item for item in experiment_registry["runs"] if item.get("id")==object_id),None)
    if question: target_type="question"; title=question.get("title",""); canonical_path=question.get("path",""); authority="markdown"
    elif experiment: target_type="experiment"; title=experiment.get("title",""); canonical_path=""; authority="legacy_json"
    elif run: target_type="run"; title=run.get("variant") or run.get("purpose") or run.get("id",""); canonical_path=""; authority="legacy_json"
    else: raise KeyError(f"verified binding target not found: {object_id}")
    created=store.create_object(object_id=object_id,object_type=target_type,project_id=f"PROJECT-{hashlib.sha256(str(pathlib.Path(root).resolve()).encode()).hexdigest()[:16]}",title=str(title),lifecycle_status="reference",canonical_path=str(canonical_path),actor_kind="human",actor_id="web-v2-binding")
    created["authority"]=authority; created["reference_identity_only"]=True
    return created
