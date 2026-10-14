"""Small local, disposable code maps for bound remote Workspaces."""

from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import re
import tempfile
from typing import Any

CONTRACT="survey-tool.workspace-code-map/v1"
MAX_FILES=400
KEY_NAMES={"pyproject.toml","package.json","Cargo.toml","go.mod","Makefile","README.md","requirements.txt","pytest.ini","tox.ini","Dockerfile"}


def _path(root: pathlib.Path | str) -> pathlib.Path:
    return pathlib.Path(root)/".survey-tool"/"workspace-code-maps.json"


def load_workspace_code_map(root: pathlib.Path | str, workspace_id: str) -> dict[str,Any]:
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,80}",str(workspace_id or "")): return {}
    try: value=json.loads(_path(root).read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError): return {}
    rows=value.get("maps",[]) if isinstance(value,dict) else []
    found=next((row for row in rows if isinstance(row,dict) and row.get("workspace_id")==workspace_id),{})
    return found if found.get("contract")==CONTRACT else {}


def save_workspace_code_map(root: pathlib.Path | str, workspace_id: str, revision: str, files: list[str], changed_files: list[str] | None = None) -> dict[str,Any]:
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,80}",str(workspace_id or "")): raise ValueError("invalid Workspace identity")
    clean=[]
    for raw in files[:MAX_FILES]:
        value=str(raw or "").strip()
        path=pathlib.PurePosixPath(value)
        if (not value or value.startswith("/") or ".." in path.parts or any(ord(char)<32 for char in value) or len(value)>500): continue
        clean.append(value)
    clean=list(dict.fromkeys(clean)); directories=sorted({pathlib.PurePosixPath(item).parts[0] for item in clean if len(pathlib.PurePosixPath(item).parts)>1})[:80]
    key_files=[item for item in clean if pathlib.PurePosixPath(item).name in KEY_NAMES][:80]
    changed=[]
    for raw in (changed_files or [])[:100]:
        value=str(raw or "").strip(); path=pathlib.PurePosixPath(value)
        if value and not value.startswith("/") and ".." not in path.parts and not any(ord(char)<32 for char in value) and len(value)<=500: changed.append(value)
    record={"contract":CONTRACT,"workspace_id":workspace_id,"revision":str(revision or "unknown")[:96],"files":clean,"directories":directories,"key_files":key_files,"recent_changed_files":list(dict.fromkeys(changed)),"refreshed_at":dt.datetime.now().isoformat(timespec="seconds")}
    target=_path(root); target.parent.mkdir(parents=True,exist_ok=True)
    try: current=json.loads(target.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError): current={"contract":"survey-tool.workspace-code-maps/v1","maps":[]}
    rows=[row for row in current.get("maps",[]) if isinstance(row,dict) and row.get("workspace_id")!=workspace_id]; rows.append(record)
    payload=json.dumps({"contract":"survey-tool.workspace-code-maps/v1","maps":rows},ensure_ascii=False,indent=2)+"\n"
    descriptor,name=tempfile.mkstemp(prefix="workspace-code-maps-",dir=target.parent)
    try:
        os.fchmod(descriptor,0o600)
        with os.fdopen(descriptor,"w",encoding="utf-8") as stream: stream.write(payload); stream.flush(); os.fsync(stream.fileno())
        os.replace(name,target)
    finally:
        if os.path.exists(name): os.unlink(name)
    return record


def workspace_code_map_summary(record: dict[str,Any]) -> str:
    if not record: return "尚无本地代码结构缓存；本次会话需先做有界结构检查。"
    directories=", ".join(map(str,record.get("directories",[])[:30])) or "（无）"
    keys=", ".join(map(str,record.get("key_files",[])[:30])) or "（无）"
    changed=", ".join(map(str,record.get("recent_changed_files",[])[:20])) or "（无记录）"
    return f"revision={str(record.get('revision') or 'unknown')[:96]}；顶层模块={directories}；关键文件={keys}；最近变更={changed}；缓存文件数={len(record.get('files') or [])}"
