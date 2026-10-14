"""Recoverable Survey Tool 2.0 worker for staged paper acquisition.

This worker owns only ephemeral/staged artifacts. It never calls ingest.py and
never writes papers/, kernel/citations.md, or research prose.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import pathlib
import re
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import urllib.parse
import urllib.request
from typing import Any, Callable
import uuid

from .store import V2Store

MAX_PDF_BYTES = 100 * 1024 * 1024
STAGING_RELATIVE_PATH = pathlib.Path(".survey-tool/staging")


def _safe_public_url(url: str) -> str:
    parsed = urllib.parse.urlparse(str(url))
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("download URL must be http(s)")
    for info in socket.getaddrinfo(parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80)):
        address = ipaddress.ip_address(info[4][0])
        if not address.is_global:
            raise ValueError("download URL resolves to a non-public address")
    return parsed.geturl()


def _staging_path(root: pathlib.Path, candidate_id: str, filename: str) -> pathlib.Path:
    base = (root / STAGING_RELATIVE_PATH / candidate_id).resolve()
    path = (base / filename).resolve()
    if base != path.parent:
        raise ValueError("invalid staging path")
    base.mkdir(parents=True, exist_ok=True)
    return path


def execute_download(root: pathlib.Path, job: dict[str, Any], *, opener: Callable[..., Any] = urllib.request.urlopen) -> dict[str, Any]:
    request = job["request"]
    url = _safe_public_url(request.get("url", ""))
    citekey = str(request.get("citekey") or "paper")
    candidate_id = str(request.get("candidate_id") or job.get("target_object_id") or "candidate")
    destination = _staging_path(root, candidate_id, f"{citekey}.pdf")
    req = urllib.request.Request(url, headers={"User-Agent": "survey-tool/2.0 staged-acquisition"})
    temporary: pathlib.Path | None = None
    try:
        with opener(req, timeout=60) as response:
            final_url = _safe_public_url(response.geturl())
            declared = int(response.headers.get("Content-Length") or 0)
            if declared > MAX_PDF_BYTES:
                raise ValueError("PDF exceeds 100 MiB limit")
            with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".download-", delete=False) as handle:
                temporary = pathlib.Path(handle.name)
                total = 0; first = b""
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    if not first:
                        first = chunk[:4]
                    total += len(chunk)
                    if total > MAX_PDF_BYTES:
                        raise ValueError("PDF exceeds 100 MiB limit")
                    handle.write(chunk)
            if first != b"%PDF":
                raise ValueError("download did not return a PDF")
            temporary.replace(destination); temporary = None
            return {"staged_pdf": str(destination.relative_to(root)), "bytes": total, "final_url": final_url, "canonical_write": False}
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)

def execute_zotero_copy(root:pathlib.Path,job:dict[str,Any],*,resolver:Callable[...,Any]|None=None)->dict[str,Any]:
    if resolver is None:
        from survey_tool.integrations import zotero_item_pdf
        resolver=zotero_item_pdf
    item_id=job.get("request",{}).get("item_id")
    if isinstance(item_id,bool) or not isinstance(item_id,int): raise ValueError("Zotero item_id must be an integer")
    resolved=resolver(root,item_id); source=pathlib.Path(resolved["path"])
    if not source.is_file() or source.suffix.lower()!=".pdf": raise ValueError("Zotero attachment is not a PDF file")
    size=source.stat().st_size
    if size>MAX_PDF_BYTES: raise ValueError("PDF exceeds 100 MiB limit")
    with source.open("rb") as handle:
        if handle.read(4)!=b"%PDF": raise ValueError("Zotero attachment is not a PDF")
    candidate_id=str(job.get("request",{}).get("candidate_id") or job.get("target_object_id") or "candidate")
    citekey=str(job.get("request",{}).get("citekey") or "paper")
    destination=_staging_path(root,candidate_id,f"{citekey}.pdf"); temporary=None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent,prefix=".zotero-copy-",delete=False) as handle:
            temporary=pathlib.Path(handle.name)
            copied=0
            with source.open("rb") as src:
                while True:
                    chunk=src.read(1024*1024)
                    if not chunk: break
                    copied+=len(chunk)
                    if copied>MAX_PDF_BYTES: raise ValueError("PDF exceeds 100 MiB limit")
                    handle.write(chunk)
        temporary.replace(destination); temporary=None
        return {"staged_pdf":str(destination.relative_to(root)),"bytes":size,"canonical_write":False}
    finally:
        if temporary is not None: temporary.unlink(missing_ok=True)


def _mineru_binary() -> str:
    found = shutil.which("mineru")
    if found:
        return found
    candidates = [
        pathlib.Path.home() / "miniforge3" / "envs" / "mineru" / "bin" / "mineru",
        pathlib.Path.home() / "miniconda3" / "envs" / "mineru" / "bin" / "mineru",
        pathlib.Path.home() / "anaconda3" / "envs" / "mineru" / "bin" / "mineru",
        pathlib.Path.home() / ".local" / "bin" / "mineru",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return "mineru"


def execute_mineru(root: pathlib.Path, store: V2Store, job: dict[str, Any], *, runner: Callable[..., Any] = subprocess.run) -> dict[str, Any]:
    source_id = str(job["request"].get("source_job_id") or job.get("depends_on_job_id") or "")
    source = store.get_job(source_id)
    relative_pdf = pathlib.Path(str(source["result"].get("staged_pdf") or ""))
    staging = (root / STAGING_RELATIVE_PATH).resolve()
    pdf = (root / relative_pdf).resolve()
    if staging not in pdf.parents or not pdf.is_file():
        raise ValueError("staged PDF is missing or outside staging")
    candidate_id = str(job["request"].get("candidate_id") or job.get("target_object_id") or "candidate")
    output = _staging_path(root, candidate_id, "mineru")
    output.mkdir(parents=True, exist_ok=True)
    binary = _mineru_binary()
    backend = os.environ.get("MINERU_BACKEND", "pipeline")
    completed = runner([binary, "-p", str(pdf), "-o", str(output), "-m", "auto", "-b", backend], cwd=str(root), capture_output=True, text=True, timeout=job.get("timeout_seconds") or 1800)
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout or "MinerU failed")[-2000:])
    markdown = sorted(output.rglob("*.md"))
    if not markdown:
        raise RuntimeError("MinerU completed without a Markdown artifact")
    return {"staged_mineru_dir": str(output.relative_to(root)), "markdown": str(markdown[0].relative_to(root)), "canonical_write": False}


def run_once(root: pathlib.Path, worker_id: str, *, recover:bool=True, target_object_id:str="") -> dict[str, Any]:
    store = V2Store(root)
    if not store.exists():
        return {"status": "not_initialized"}
    if recover: store.recover_expired_jobs()
    job = store.claim_next_job(worker_id=worker_id, kinds=["paper_download", "zotero_copy", "mineru"], lease_seconds=3600,target_object_id=target_object_id)
    if job is None:
        return {"status": "idle"}
    token = job["lease_token"]
    try:
        result = execute_download(root, job) if job["kind"] == "paper_download" else execute_zotero_copy(root,job) if job["kind"]=="zotero_copy" else execute_mineru(root, store, job)
        finished = store.finish_claimed_job(job["id"], lease_token=token, succeeded=True, result=result)
    except Exception as exc:
        finished = store.finish_claimed_job(job["id"], lease_token=token, succeeded=False, error_class=type(exc).__name__, error_message=str(exc))
    return {"status": finished["status"], "job": finished}

_LOCAL_WORKERS:dict[str,threading.Thread]={}
_LOCAL_WORKERS_LOCK=threading.Lock()
def start_local_worker(root:pathlib.Path,*,target_object_id:str="",max_jobs:int=2,runner:Callable[...,dict[str,Any]]|None=None)->dict[str,Any]:
    root=pathlib.Path(root).resolve(); key=str(root); max_jobs=int(max_jobs)
    if not 1<=max_jobs<=4: raise ValueError("max_jobs must be between 1 and 4")
    if target_object_id and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}",target_object_id): raise ValueError("invalid target_object_id")
    worker_id=f"local-{uuid.uuid4().hex[:12]}"; run=runner or run_once
    def drain():
        try:
            for _ in range(max_jobs):
                try: result=run(root,worker_id,recover=False,target_object_id=target_object_id)
                except Exception: break
                if result.get("status") in {"idle","not_initialized"}: break
        finally:
            with _LOCAL_WORKERS_LOCK:
                if _LOCAL_WORKERS.get(key) is threading.current_thread(): _LOCAL_WORKERS.pop(key,None)
    with _LOCAL_WORKERS_LOCK:
        current=_LOCAL_WORKERS.get(key)
        if current and current.is_alive(): return {"worker_started":False,"already_running":True,"worker_id":current.name}
        thread=threading.Thread(target=drain,name=worker_id,daemon=True); _LOCAL_WORKERS[key]=thread; thread.start()
    return {"worker_started":True,"already_running":False,"worker_id":worker_id}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one recoverable Survey Tool 2.0 staged job")
    parser.add_argument("--project", required=True)
    parser.add_argument("--worker-id", default="local-worker")
    parser.add_argument("--once", action="store_true", help="process at most one job and exit")
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    args = parser.parse_args()
    root = pathlib.Path(args.project).expanduser().resolve()
    if args.once:
        print(json.dumps(run_once(root, args.worker_id), ensure_ascii=False)); return
    if not 0.2 <= args.poll_seconds <= 60:
        raise SystemExit("--poll-seconds must be between 0.2 and 60")
    try:
        while True:
            result = run_once(root, args.worker_id)
            print(json.dumps(result, ensure_ascii=False), flush=True)
            if result["status"] in {"idle", "not_initialized"}: time.sleep(args.poll_seconds)
    except KeyboardInterrupt:
        print(json.dumps({"status": "stopped"}), flush=True)


if __name__ == "__main__":
    main()
