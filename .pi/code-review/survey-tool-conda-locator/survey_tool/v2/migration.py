"""Read-only migration inventory for legacy Survey Tool projects."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import re
import sqlite3
import uuid
from typing import Any

from .store import V2Store

SOURCE_SPECS = (
    ("project_state", "state.md", "markdown", "retain_canonical"),
    ("citations", "kernel/citations.md", "markdown", "index_only"),
    ("claims", "kernel/claims.md", "markdown_gate", "index_only"),
    ("review_log", "kernel/review_log.md", "append_only_markdown", "retain_canonical"),
    ("questions", "shell/01_questions", "markdown", "index_only"),
    ("comparisons_markdown", "shell/04_comparisons", "markdown", "index_only"),
    ("comparisons_registry", ".survey-tool/compares.json", "legacy_json", "defer_authority"),
    ("experiments", ".survey-tool/experiments.json", "legacy_json_authority", "defer_authority"),
    ("runs", ".survey-tool/runs.json", "legacy_json_authority", "defer_authority"),
    ("execution_outbox", ".survey-tool/execution-outbox.json", "legacy_json_authority", "defer_authority"),
    ("workspaces", ".survey-tool/workspaces.json", "legacy_json_authority", "defer_authority"),
    ("agent_routing", ".survey-tool/agent-routing.json", "legacy_json_authority", "defer_authority"),
)


def _sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _json_count(value: Any) -> int:
    if isinstance(value, list): return len(value)
    if isinstance(value, dict):
        for key in ("items", "objects", "experiments", "runs", "comparisons", "entries", "tasks"):
            if isinstance(value.get(key), list): return len(value[key])
        return len(value)
    return 0


def _file_record(path: pathlib.Path, relative: str) -> dict[str, Any]:
    record: dict[str, Any] = {"path": relative, "bytes": path.stat().st_size, "sha256": _sha256(path), "parse_status": "ok", "records": 1}
    if path.suffix == ".json":
        try: record["records"] = _json_count(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc: record.update(parse_status="invalid", error=f"{type(exc).__name__}: {str(exc)[:200]}", records=0)
    elif path.name == "citations.md": record["records"] = len(re.findall(r"^## \[[^]]+\]", path.read_text(encoding="utf-8", errors="replace"), re.M))
    elif path.name == "claims.md": record["records"] = len(re.findall(r"^##?\s+\[?C[\w.-]+", path.read_text(encoding="utf-8", errors="replace"), re.M | re.I))
    return record


def _question_identity(path: pathlib.Path, root: pathlib.Path) -> dict[str, Any]:
    text=path.read_text(encoding="utf-8"); header=text.split("---",2)[1] if text.startswith("---") and text.count("---")>=2 else ""
    def scalar(name: str, default=""):
        match=re.search(rf"^{re.escape(name)}:\s*(.*?)\s*$",header,re.M); return (match.group(1).strip().strip("'\"") if match else default)
    experiments=[]; block=re.search(r"^experiments:\s*\n((?:\s+-\s+.*\n?)*)",header,re.M)
    if block: experiments=[line.strip().removeprefix("-").strip().strip("'\"") for line in block.group(1).splitlines() if line.strip().startswith("-")]
    return {"id":scalar("id",path.stem),"type":"question","title":scalar("title",path.stem),"canonical_path":path.relative_to(root).as_posix(),"source_hash":_sha256(path),"experiments":experiments}


def build_identity_index_plan(project_root: pathlib.Path | str) -> dict[str, Any]:
    root=pathlib.Path(project_root).expanduser().resolve(); objects=[]; warnings=[]
    question_dir=root/"shell/01_questions"
    for path in sorted(question_dir.glob("Q-*.md")) if question_dir.is_dir() else []:
        try: objects.append(_question_identity(path,root))
        except Exception as exc: warnings.append({"kind":"question_parse_error","path":path.relative_to(root).as_posix(),"message":str(exc)[:200]})
    experiment_path=root/".survey-tool/experiments.json"
    if experiment_path.is_file():
        try:
            raw=json.loads(experiment_path.read_text(encoding="utf-8")); rows=raw.get("experiments",[]) if isinstance(raw,dict) else raw
            if not isinstance(rows,list): raise ValueError("experiments registry must contain a list")
            source_hash=_sha256(experiment_path)
            for item in rows:
                if isinstance(item,dict) and item.get("id"): objects.append({"id":str(item["id"]),"type":"experiment","title":str(item.get("title") or item["id"]),"canonical_path":"","source_hash":source_hash,"experiments":[]})
        except Exception as exc: warnings.append({"kind":"experiment_parse_error","path":".survey-tool/experiments.json","message":str(exc)[:200]})
    ids={item["id"] for item in objects}; relations=[]
    for item in objects:
        if item["type"]=="question":
            for target in item["experiments"]:
                if target in ids: relations.append({"from_object_id":item["id"],"relation_type":"tests","to_object_id":target})
                else: warnings.append({"kind":"missing_relation_target","path":item["canonical_path"],"message":f"Experiment {target} not found; relation skipped"})
    duplicate_ids=sorted({item["id"] for item in objects if sum(other["id"]==item["id"] for other in objects)>1})
    for object_id in duplicate_ids: warnings.append({"kind":"duplicate_identity","path":object_id,"message":"duplicate legacy identity blocks apply"})
    store=V2Store(root)
    if store.exists():
        with sqlite3.connect(f"file:{store.path}?mode=ro",uri=True) as conn:
            conn.row_factory=sqlite3.Row
            for item in objects:
                row=conn.execute("SELECT type,canonical_path FROM objects WHERE id=?",(item["id"],)).fetchone()
                if row and (row["type"]!=item["type"] or row["canonical_path"]!=item["canonical_path"]):
                    differences=[]
                    if row["type"]!=item["type"]: differences.append(f"type is {row['type']!r}, expected {item['type']!r}")
                    if row["canonical_path"]!=item["canonical_path"]: differences.append(f"canonical_path is {row['canonical_path']!r}, expected {item['canonical_path']!r}")
                    warnings.append({"kind":"existing_identity_conflict","path":item["id"],"message":"; ".join(differences)})
    return {"schema":"survey-tool.identity-index-plan/v1","will_write":True,"objects":objects,"relations":relations,"warnings":warnings,"blocked":bool(duplicate_ids or any(item["kind"].endswith("parse_error") or item["kind"]=="existing_identity_conflict" for item in warnings)),"summary":{"questions":sum(item["type"]=="question" for item in objects),"experiments":sum(item["type"]=="experiment" for item in objects),"relations":len(relations),"warnings":len(warnings)},"authority":{"question":"markdown","experiment":"legacy_json","sqlite":"identity_and_relation_index_only"}}


def identity_index_history(project_root: pathlib.Path | str) -> list[dict[str, Any]]:
    """Return persisted checkpoints without creating or upgrading the v2 store."""
    store=V2Store(project_root)
    if not store.exists(): return []
    with sqlite3.connect(f"file:{store.path}?mode=ro",uri=True) as conn:
        conn.row_factory=sqlite3.Row
        rows=conn.execute("""SELECT source_hash,status,details_json,created_at FROM migration_records
            WHERE migration_key=? ORDER BY created_at DESC""",("identity-index-v1",)).fetchall()
    history=[]
    for row in rows:
        try: details=json.loads(row["details_json"] or "{}")
        except json.JSONDecodeError: details={"record_error":"invalid persisted details"}
        history.append({"checkpoint_hash":row["source_hash"],"status":row["status"],"applied_at":row["created_at"],"details":details})
    return history


def apply_identity_index_migration(project_root: pathlib.Path | str, *, actor_id: str="") -> dict[str, Any]:
    root=pathlib.Path(project_root).expanduser().resolve(); store=V2Store(root)
    if not store.exists(): raise ValueError("v2 project store is not initialized")
    plan=build_identity_index_plan(root)
    if plan["blocked"]: raise ValueError("identity migration plan is blocked by source errors")
    project_id="PROJECT-"+hashlib.sha256(str(root).encode()).hexdigest()[:16]; created=0; existing=0; relations_created=0; now=__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(timespec="seconds")
    with store.transaction() as conn:
        for item in plan["objects"]:
            row=conn.execute("SELECT * FROM objects WHERE id=?",(item["id"],)).fetchone()
            if row:
                if row["type"]!=item["type"] or row["canonical_path"]!=item["canonical_path"]: raise ValueError(f"identity conflict for {item['id']}")
                existing+=1; continue
            conn.execute("""INSERT INTO objects(id,type,project_id,title,lifecycle_status,canonical_path,created_at,created_by_kind,created_by_id,updated_at,updated_by_kind,updated_by_id)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",(item["id"],item["type"],project_id,item["title"],"reference",item["canonical_path"],now,"migration",actor_id,now,"migration",actor_id))
            store._insert_event(conn,object_id=item["id"],kind="migration.identity_indexed",actor_kind="human",actor_id=actor_id,from_revision=None,to_revision=1,summary=f"Indexed legacy {item['type']} identity {item['id']}",details={"authority":"markdown" if item["type"]=="question" else "legacy_json","source_hash":item["source_hash"],"prose_copied":False})
            created+=1
        for relation in plan["relations"]:
            cursor=conn.execute("""INSERT OR IGNORE INTO object_relations(id,from_object_id,relation_type,to_object_id,metadata_json,created_at,created_by_kind,created_by_id)
                VALUES (?,?,?,?,?,?,?,?)""",("REL-"+uuid.uuid4().hex,relation["from_object_id"],relation["relation_type"],relation["to_object_id"],json.dumps({"authority":"legacy_frontmatter","inferred":False}),now,"migration",actor_id))
            relations_created+=cursor.rowcount
        checkpoint_hash="sha256:"+hashlib.sha256(json.dumps(plan["objects"],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        conn.execute("""INSERT INTO migration_records(id,migration_key,source_path,source_hash,status,details_json,created_at) VALUES (?,?,?,?,?,?,?)
            ON CONFLICT(migration_key,source_path) DO UPDATE SET source_hash=excluded.source_hash,status=excluded.status,details_json=excluded.details_json,created_at=excluded.created_at""",("MIG-"+uuid.uuid4().hex,"identity-index-v1","legacy-question-experiment",checkpoint_hash,"applied",json.dumps({"created":created,"existing":existing,"relations_created":relations_created,"authority_changed":False}),now))
    return {"schema":"survey-tool.migration-apply/v1","status":"applied","checkpoint_hash":checkpoint_hash,"created":created,"existing":existing,"relations_created":relations_created,"authority_changed":False,"prose_copied":False,"canonical_files_modified":False,"plan":plan}


def _citekey_from_title(title: str, date: str = "") -> str:
    t = re.sub(r"[^a-z0-9]+", "", (title or "").lower())[:10] or "paper"
    year = (re.search(r"(20\d\d|19\d\d)", date or "") or ["", ""])[1]
    return f"{t[:8]}{year}"


def _paper_title_from_name(name: str) -> str:
    t = re.sub(r"_\d{4}$", "", name)
    return t.replace("_", ": ", 1) if "_ " in t[:20] else t


def _frontmatter(path: pathlib.Path) -> str:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---") and text.count("---") >= 2:
        return text.split("---", 2)[1]
    return ""


def _frontmatter_scalar(header: str, name: str, default: str = "") -> str:
    match = re.search(rf"^{re.escape(name)}:[ \t]*(.*?)[ \t]*$", header, re.M)
    return (match.group(1).strip().strip("'\"") if match else default)


def _paper_index_rows(path: pathlib.Path) -> list[dict[str, Any]]:
    txt = path.read_text(encoding="utf-8")
    rows: list[dict[str, Any]] = []
    for m in re.finditer(r"^\|\s*(\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|", txt, re.M):
        num, title, date, venue, link, file = m.groups()
        if title.lower() == "title":
            continue
        rows.append({"num": int(num), "title": title.strip(), "date": date.strip(), "venue": venue.strip(), "link": link.strip(), "file": file.strip().strip("`"), "has_pdf": "⚠️" not in file})
    return rows


def _paper_identity_records(root: pathlib.Path) -> list[dict[str, Any]]:
    """Index canonical PDFs and no-PDF catalog rows as `paper` reference identities."""
    pdir = root / "papers"
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    if pdir.is_dir():
        for pdf in sorted(pdir.glob("*.pdf")):
            title = _paper_title_from_name(pdf.stem)
            date = pdf.stem[-4:] if re.search(r"_\d{4}$", pdf.stem) else ""
            citekey = _citekey_from_title(title, date)
            seen.add(citekey)
            records.append({
                "id": citekey, "type": "paper", "title": title,
                "canonical_path": pdf.relative_to(root).as_posix(),
                "source_hash": _sha256(pdf), "papers": [],
            })
    index_path = pdir / "INDEX.md"
    if index_path.is_file():
        index_hash = _sha256(index_path)
        for row in _paper_index_rows(index_path):
            if row["has_pdf"]:
                continue
            citekey = _citekey_from_title(row["title"], row["date"])
            if citekey in seen:
                continue
            seen.add(citekey)
            records.append({
                "id": citekey, "type": "paper", "title": row["title"],
                "canonical_path": "", "source_hash": index_hash, "papers": [],
            })
    return records


def _comparison_records(root: pathlib.Path) -> list[dict[str, Any]]:
    """Index the legacy comparison registry by stable id; prose stays Markdown."""
    path = root / ".survey-tool" / "compares.json"
    records: list[dict[str, Any]] = []
    if not path.is_file():
        return records
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data if isinstance(data, list) else []
    source_hash = _sha256(path)
    for item in rows:
        if not isinstance(item, dict):
            continue
        cid = str(item.get("id") or "").strip()
        if not cid:
            continue
        records.append({
            "id": cid, "type": "comparison",
            "title": str(item.get("name") or cid),
            "canonical_path": f"shell/04_comparisons/{cid}.md",
            "source_hash": source_hash,
            "papers": [str(x) for x in (item.get("papers") or []) if x],
        })
    return records


def _finding_records(root: pathlib.Path) -> list[dict[str, Any]]:
    """Index canonical finding Markdown frontmatter; prose stays Markdown."""
    fdir = root / "shell" / "04_comparisons" / "findings"
    records: list[dict[str, Any]] = []
    if not fdir.is_dir():
        return records
    for path in sorted(fdir.glob("F-*.md")):
        header = _frontmatter(path)
        fid = _frontmatter_scalar(header, "id", path.stem)
        title = _frontmatter_scalar(header, "title", path.stem)
        comparison = _frontmatter_scalar(header, "comparison", "")
        records.append({
            "id": fid, "type": "finding", "title": title[:200] or fid,
            "canonical_path": path.relative_to(root).as_posix(),
            "source_hash": _sha256(path), "comparison": comparison,
        })
    return records


def _claim_records(root: pathlib.Path) -> list[dict[str, Any]]:
    """Index kernel claim identity/status only; gate and prose stay kernel Markdown."""
    path = root / "kernel" / "claims.md"
    records: list[dict[str, Any]] = []
    if not path.is_file():
        return records
    text = path.read_text(encoding="utf-8")
    source_hash = _sha256(path)
    for m in re.finditer(r"^## (C\d+)\n(.*?)(?=\n^## |\Z)", text, re.M | re.S):
        cid = m.group(1); body = m.group(2)
        def field(key: str) -> str:
            mm = re.search(rf"^- {key}:[ \t]*(.*)$", body, re.M)
            return mm.group(1).strip() if mm else ""
        citekey = field("citekey")
        if not citekey:
            src_match = re.search(r"\[\[([^\]]+)\]\]", field("sources"))
            if src_match:
                citekey = src_match.group(1)
        if not citekey:
            citekey = field("source_ref").split(":", 1)[0].strip()
        claim_text = field("text")
        records.append({
            "id": cid, "type": "claim", "title": claim_text[:200] or cid,
            "canonical_path": "kernel/claims.md",
            "source_hash": source_hash, "citekey": citekey, "status": field("status"),
        })
    return records


def build_content_index_plan(project_root: pathlib.Path | str) -> dict[str, Any]:
    root = pathlib.Path(project_root).expanduser().resolve()
    objects: list[dict[str, Any]] = []
    warnings: list[dict[str, str]] = []
    for name, fn, err_path in (
        ("papers", _paper_identity_records, "papers"),
        ("comparisons", _comparison_records, ".survey-tool/compares.json"),
        ("findings", _finding_records, "shell/04_comparisons/findings"),
        ("claims", _claim_records, "kernel/claims.md"),
    ):
        try:
            objects.extend(fn(root))
        except Exception as exc:
            warnings.append({"kind": f"{name}_parse_error", "path": err_path, "message": str(exc)[:200]})
    ids = {item["id"]: item for item in objects}
    duplicate_ids = sorted({item["id"] for item in objects if sum(other["id"] == item["id"] for other in objects) > 1})
    for object_id in duplicate_ids:
        warnings.append({"kind": "duplicate_identity", "path": object_id, "message": "duplicate legacy identity blocks apply"})
    relations: list[dict[str, str]] = []
    for item in objects:
        if item["type"] == "comparison":
            for target in item.get("papers", []):
                if target in ids:
                    relations.append({"from_object_id": item["id"], "relation_type": "compares", "to_object_id": target})
                else:
                    warnings.append({"kind": "missing_relation_target", "path": item["id"], "message": f"paper {target} not found; relation skipped"})
        elif item["type"] == "finding":
            target = item.get("comparison", "")
            if target:
                if target in ids:
                    relations.append({"from_object_id": item["id"], "relation_type": "derived_from", "to_object_id": target})
                else:
                    warnings.append({"kind": "missing_relation_target", "path": item["id"], "message": f"comparison {target} not found; relation skipped"})
        elif item["type"] == "claim":
            target = item.get("citekey", "")
            if target:
                if target in ids:
                    relations.append({"from_object_id": item["id"], "relation_type": "derived_from", "to_object_id": target})
                else:
                    warnings.append({"kind": "missing_relation_target", "path": item["id"], "message": f"paper {target} not found; relation skipped"})
    store = V2Store(root)
    if store.exists():
        with sqlite3.connect(f"file:{store.path}?mode=ro", uri=True) as conn:
            conn.row_factory = sqlite3.Row
            for item in objects:
                row = conn.execute("SELECT type,canonical_path FROM objects WHERE id=?", (item["id"],)).fetchone()
                if row and (row["type"] != item["type"] or row["canonical_path"] != item["canonical_path"]):
                    differences = []
                    if row["type"] != item["type"]:
                        differences.append(f"type is {row['type']!r}, expected {item['type']!r}")
                    if row["canonical_path"] != item["canonical_path"]:
                        differences.append(f"canonical_path is {row['canonical_path']!r}, expected {item['canonical_path']!r}")
                    warnings.append({"kind": "existing_identity_conflict", "path": item["id"], "message": "; ".join(differences)})
    blocked = bool(duplicate_ids or any(item["kind"].endswith("parse_error") or item["kind"] == "existing_identity_conflict" for item in warnings))
    return {
        "schema": "survey-tool.content-index-plan/v1", "will_write": True,
        "objects": objects, "relations": relations, "warnings": warnings, "blocked": blocked,
        "summary": {
            "papers": sum(item["type"] == "paper" for item in objects),
            "comparisons": sum(item["type"] == "comparison" for item in objects),
            "findings": sum(item["type"] == "finding" for item in objects),
            "claims": sum(item["type"] == "claim" for item in objects),
            "relations": len(relations), "warnings": len(warnings),
        },
        "authority": {"paper": "canonical_files", "comparison": "markdown", "finding": "markdown", "claim": "kernel_gate", "sqlite": "identity_and_relation_index_only"},
    }


def content_index_history(project_root: pathlib.Path | str) -> list[dict[str, Any]]:
    store = V2Store(project_root)
    if not store.exists():
        return []
    with sqlite3.connect(f"file:{store.path}?mode=ro", uri=True) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""SELECT source_hash,status,details_json,created_at FROM migration_records
            WHERE migration_key=? ORDER BY created_at DESC""", ("content-index-v1",)).fetchall()
    history = []
    for row in rows:
        try:
            details = json.loads(row["details_json"] or "{}")
        except json.JSONDecodeError:
            details = {"record_error": "invalid persisted details"}
        history.append({"checkpoint_hash": row["source_hash"], "status": row["status"], "applied_at": row["created_at"], "details": details})
    return history


def apply_content_index_migration(project_root: pathlib.Path | str, *, actor_id: str = "") -> dict[str, Any]:
    root = pathlib.Path(project_root).expanduser().resolve()
    store = V2Store(root)
    if not store.exists():
        raise ValueError("v2 project store is not initialized")
    plan = build_content_index_plan(root)
    if plan["blocked"]:
        raise ValueError("content migration plan is blocked by source errors")
    project_id = "PROJECT-" + hashlib.sha256(str(root).encode()).hexdigest()[:16]
    created = 0; existing = 0; relations_created = 0
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    authority_by_type = {"paper": "canonical_files", "comparison": "markdown", "finding": "markdown", "claim": "kernel_gate"}
    with store.transaction() as conn:
        for item in plan["objects"]:
            row = conn.execute("SELECT type,canonical_path FROM objects WHERE id=?", (item["id"],)).fetchone()
            if row:
                if row["type"] != item["type"] or row["canonical_path"] != item["canonical_path"]:
                    raise ValueError(f"identity conflict for {item['id']}")
                existing += 1
                continue
            conn.execute("""INSERT INTO objects(id,type,project_id,title,lifecycle_status,canonical_path,created_at,created_by_kind,created_by_id,updated_at,updated_by_kind,updated_by_id)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", (item["id"], item["type"], project_id, item["title"], "reference", item["canonical_path"], now, "migration", actor_id, now, "migration", actor_id))
            details = {"authority": authority_by_type.get(item["type"], "markdown"), "source_hash": item["source_hash"], "prose_copied": False}
            if item["type"] == "claim":
                details["status_indexed"] = item.get("status", "")
            store._insert_event(conn, object_id=item["id"], kind="migration.content_indexed", actor_kind="human", actor_id=actor_id, from_revision=None, to_revision=1, summary=f"Indexed legacy {item['type']} identity {item['id']}", details=details)
            created += 1
        for relation in plan["relations"]:
            cursor = conn.execute("""INSERT OR IGNORE INTO object_relations(id,from_object_id,relation_type,to_object_id,metadata_json,created_at,created_by_kind,created_by_id)
                VALUES (?,?,?,?,?,?,?,?)""", ("REL-" + uuid.uuid4().hex, relation["from_object_id"], relation["relation_type"], relation["to_object_id"], json.dumps({"authority": "legacy_registry", "inferred": False}), now, "migration", actor_id))
            relations_created += cursor.rowcount
        checkpoint_hash = "sha256:" + hashlib.sha256(json.dumps(plan["objects"], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        conn.execute("""INSERT INTO migration_records(id,migration_key,source_path,source_hash,status,details_json,created_at) VALUES (?,?,?,?,?,?,?)
            ON CONFLICT(migration_key,source_path) DO UPDATE SET source_hash=excluded.source_hash,status=excluded.status,details_json=excluded.details_json,created_at=excluded.created_at""", ("MIG-" + uuid.uuid4().hex, "content-index-v1", "legacy-papers-comparisons-findings-claims", checkpoint_hash, "applied", json.dumps({"created": created, "existing": existing, "relations_created": relations_created, "authority_changed": False}), now))
    return {"schema": "survey-tool.migration-apply/v1", "status": "applied", "checkpoint_hash": checkpoint_hash, "created": created, "existing": existing, "relations_created": relations_created, "authority_changed": False, "prose_copied": False, "canonical_files_modified": False, "plan": plan}


def refresh_v2_index(
    project_root: pathlib.Path | str,
    *,
    actor_id: str = "",
    identity: bool = True,
    content: bool = True,
) -> dict[str, Any]:
    """Best-effort refresh of v2 indexes after an authoritative legacy write."""
    root = pathlib.Path(project_root).expanduser().resolve()
    if not V2Store(root).exists():
        return {"status": "skipped", "reason": "v2 store not initialized"}

    result: dict[str, Any] = {
        "status": "ok",
        "identity": {"status": "skipped", "reason": "disabled"},
        "content": {"status": "skipped", "reason": "disabled"},
        "warnings": [],
    }
    if identity:
        try:
            plan = build_identity_index_plan(root)
            if plan["blocked"]:
                result["warnings"].extend(plan["warnings"])
                result["identity"] = {"status": "blocked", "warnings": plan["warnings"]}
            else:
                result["identity"] = apply_identity_index_migration(root, actor_id=actor_id)
        except Exception as exc:
            warning = {"kind": "identity_refresh_error", "message": str(exc)[:200]}
            result["warnings"].append(warning)
            result["identity"] = {"status": "error", "warnings": [warning]}
    if content:
        try:
            plan = build_content_index_plan(root)
            if plan["blocked"]:
                result["warnings"].extend(plan["warnings"])
                result["content"] = {"status": "blocked", "warnings": plan["warnings"]}
            else:
                result["content"] = apply_content_index_migration(root, actor_id=actor_id)
        except Exception as exc:
            warning = {"kind": "content_refresh_error", "message": str(exc)[:200]}
            result["warnings"].append(warning)
            result["content"] = {"status": "error", "warnings": [warning]}
    return result


def build_migration_inventory(project_root: pathlib.Path | str) -> dict[str, Any]:
    root = pathlib.Path(project_root).expanduser().resolve()
    sources: list[dict[str, Any]] = []
    warnings: list[dict[str, str]] = []
    for name, relative, authority, action in SOURCE_SPECS:
        path = root / relative
        files = sorted(path.glob("*.md")) if path.is_dir() else [path] if path.is_file() else []
        records = [_file_record(file, file.relative_to(root).as_posix()) for file in files]
        source = {"name": name, "path": relative, "authority": authority, "proposed_action": action, "exists": bool(files), "files": records, "records": sum(item["records"] for item in records)}
        sources.append(source)
        for item in records:
            if item["parse_status"] != "ok": warnings.append({"kind": "parse_error", "path": item["path"], "message": item.get("error", "invalid source")})

    paper_files = sorted((root / "papers").glob("*.pdf")) if (root / "papers").is_dir() else []
    papers = [{"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": _sha256(path)} for path in paper_files]
    citation_source = next(source for source in sources if source["name"] == "citations")
    if citation_source["records"] != len(papers):
        warnings.append({"kind": "paper_citation_count_mismatch", "path": "papers", "message": f"{len(papers)} PDFs vs {citation_source['records']} citation entries; requires human reconciliation"})
    if (root / ".publish").exists():
        warnings.append({"kind": "excluded_mirror", "path": ".publish", "message": "publish mirror excluded from migration sources"})
    store = V2Store(root)
    return {
        "schema": "survey-tool.migration-inventory/v2",
        "mode": "dry-run",
        "project_root": str(root),
        "will_write": False,
        "v2_store": {"initialized": store.exists(), "schema_version": store.schema_version() if store.exists() else 0},
        "sources": sources,
        "papers": {"authority": "canonical_files", "records": len(papers), "files": papers, "proposed_action": "index_only"},
        "warnings": warnings,
        "summary": {"source_groups": len(sources), "existing_groups": sum(1 for source in sources if source["exists"]), "source_files": sum(len(source["files"]) for source in sources), "paper_pdfs": len(papers), "warnings": len(warnings)},
        "excluded": [".publish/", ".git/", "codespace/", ".pi/", "node_modules/", "experiment artifacts"],
    }
