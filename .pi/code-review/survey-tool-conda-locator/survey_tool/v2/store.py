"""SQLite-backed runtime state for Survey Tool 2.0.

Research prose remains canonical Markdown. This store owns transactional runtime
state such as identities, relations, jobs, inbox projections, and audit events.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import re
import secrets
import sqlite3
import uuid
from contextlib import contextmanager
from typing import Any, Iterator

from .capabilities import herdr_capability

SCHEMA_VERSION = 7
DB_RELATIVE_PATH = pathlib.Path(".survey-tool/survey-tool-v2.sqlite3")
OBJECT_TYPES = frozenset(
    {
        "paper",
        "paper_candidate",
        "seven_q",
        "comparison",
        "finding",
        "claim",
        "idea",
        "question",
        "workspace",
        "experiment",
        "run",
        "automation",
        "agent_session",
        "herdr_launch_request",
        "herdr_execution",
        "artifact",
    }
)
RELATION_TYPES = frozenset(
    {
        "belongs_to",
        "derived_from",
        "discusses",
        "compares",
        "supports",
        "contradicts",
        "tests",
        "produced_by",
        "uses_workspace",
        "implemented_by",
        "monitored_by",
        "supersedes",
    }
)
JOB_STATUSES = frozenset({"queued", "running", "succeeded", "failed", "cancelled"})
INBOX_STATUSES = frozenset({"open", "snoozed", "resolved", "dismissed"})
_ID_PART = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")

_MIGRATIONS = {
    1: """
    CREATE TABLE objects (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        project_id TEXT NOT NULL,
        title TEXT NOT NULL DEFAULT '',
        lifecycle_status TEXT NOT NULL DEFAULT 'active',
        canonical_path TEXT NOT NULL DEFAULT '',
        revision INTEGER NOT NULL DEFAULT 1 CHECK (revision >= 1),
        created_at TEXT NOT NULL,
        created_by_kind TEXT NOT NULL,
        created_by_id TEXT NOT NULL DEFAULT '',
        updated_at TEXT NOT NULL,
        updated_by_kind TEXT NOT NULL,
        updated_by_id TEXT NOT NULL DEFAULT ''
    );
    CREATE INDEX objects_type_status_idx ON objects(type, lifecycle_status);

    CREATE TABLE object_relations (
        id TEXT PRIMARY KEY,
        from_object_id TEXT NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
        relation_type TEXT NOT NULL,
        to_object_id TEXT NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
        metadata_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL,
        created_by_kind TEXT NOT NULL,
        created_by_id TEXT NOT NULL DEFAULT '',
        UNIQUE(from_object_id, relation_type, to_object_id)
    );
    CREATE INDEX relations_target_idx ON object_relations(to_object_id, relation_type);

    CREATE TABLE events (
        id TEXT PRIMARY KEY,
        object_id TEXT REFERENCES objects(id) ON DELETE SET NULL,
        kind TEXT NOT NULL,
        actor_kind TEXT NOT NULL,
        actor_id TEXT NOT NULL DEFAULT '',
        occurred_at TEXT NOT NULL,
        from_revision INTEGER,
        to_revision INTEGER,
        summary TEXT NOT NULL DEFAULT '',
        details_json TEXT NOT NULL DEFAULT '{}'
    );
    CREATE INDEX events_object_time_idx ON events(object_id, occurred_at);

    CREATE TABLE jobs (
        id TEXT PRIMARY KEY,
        kind TEXT NOT NULL,
        status TEXT NOT NULL,
        target_object_id TEXT REFERENCES objects(id) ON DELETE SET NULL,
        idempotency_key TEXT,
        request_json TEXT NOT NULL DEFAULT '{}',
        result_json TEXT NOT NULL DEFAULT '{}',
        progress REAL CHECK (progress IS NULL OR (progress >= 0 AND progress <= 1)),
        attempt INTEGER NOT NULL DEFAULT 0 CHECK (attempt >= 0),
        timeout_seconds INTEGER CHECK (timeout_seconds IS NULL OR timeout_seconds > 0),
        error_class TEXT NOT NULL DEFAULT '',
        error_message TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL,
        started_at TEXT,
        finished_at TEXT,
        revision INTEGER NOT NULL DEFAULT 1,
        UNIQUE(kind, idempotency_key)
    );
    CREATE INDEX jobs_status_created_idx ON jobs(status, created_at);

    CREATE TABLE inbox_items (
        id TEXT PRIMARY KEY,
        kind TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'open',
        target_object_id TEXT NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
        title TEXT NOT NULL DEFAULT '',
        reason TEXT NOT NULL DEFAULT '',
        due_at TEXT,
        created_at TEXT NOT NULL,
        resolved_at TEXT,
        revision INTEGER NOT NULL DEFAULT 1,
        UNIQUE(kind, target_object_id, status)
    );
    CREATE INDEX inbox_status_created_idx ON inbox_items(status, created_at);

    CREATE TABLE agent_sessions (
        id TEXT PRIMARY KEY,
        provider TEXT NOT NULL,
        status TEXT NOT NULL,
        object_id TEXT NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
        task_type TEXT NOT NULL,
        external_ref TEXT NOT NULL DEFAULT '',
        agent TEXT NOT NULL DEFAULT '',
        model TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL,
        last_seen_at TEXT,
        revision INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE automations (
        object_id TEXT PRIMARY KEY REFERENCES objects(id) ON DELETE CASCADE,
        automation_type TEXT NOT NULL,
        phase TEXT NOT NULL,
        budget_json TEXT NOT NULL DEFAULT '{}',
        approval_json TEXT NOT NULL DEFAULT '{}',
        started_at TEXT,
        deadline_at TEXT,
        stopped_at TEXT
    );

    CREATE TABLE automation_steps (
        id TEXT PRIMARY KEY,
        automation_object_id TEXT NOT NULL REFERENCES automations(object_id) ON DELETE CASCADE,
        sequence INTEGER NOT NULL CHECK (sequence >= 1),
        kind TEXT NOT NULL,
        status TEXT NOT NULL,
        job_id TEXT REFERENCES jobs(id) ON DELETE SET NULL,
        summary TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL,
        finished_at TEXT,
        UNIQUE(automation_object_id, sequence)
    );

    CREATE TABLE migration_records (
        id TEXT PRIMARY KEY,
        migration_key TEXT NOT NULL,
        source_path TEXT NOT NULL DEFAULT '',
        source_hash TEXT NOT NULL DEFAULT '',
        status TEXT NOT NULL,
        details_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL,
        UNIQUE(migration_key, source_path)
    );
    """,
    2: """
    CREATE TABLE paper_candidates (
        object_id TEXT PRIMARY KEY REFERENCES objects(id) ON DELETE CASCADE,
        citekey TEXT NOT NULL,
        authors_json TEXT NOT NULL DEFAULT '[]',
        year TEXT NOT NULL DEFAULT '',
        doi TEXT NOT NULL DEFAULT '',
        source_url TEXT NOT NULL,
        oa_url TEXT NOT NULL DEFAULT '',
        source TEXT NOT NULL DEFAULT 'manual',
        recommendation_reason TEXT NOT NULL DEFAULT '',
        verification_status TEXT NOT NULL DEFAULT 'unverified',
        acquisition_job_id TEXT REFERENCES jobs(id) ON DELETE SET NULL,
        UNIQUE(source_url),
        UNIQUE(citekey, source_url)
    );
    CREATE INDEX paper_candidates_verification_idx ON paper_candidates(verification_status);
    """,
    3: """
    ALTER TABLE jobs ADD COLUMN depends_on_job_id TEXT REFERENCES jobs(id) ON DELETE SET NULL;
    ALTER TABLE jobs ADD COLUMN lease_token TEXT NOT NULL DEFAULT '';
    ALTER TABLE jobs ADD COLUMN lease_owner TEXT NOT NULL DEFAULT '';
    ALTER TABLE jobs ADD COLUMN lease_expires_at TEXT;
    ALTER TABLE jobs ADD COLUMN last_heartbeat_at TEXT;
    CREATE INDEX jobs_dependency_idx ON jobs(depends_on_job_id);
    CREATE INDEX jobs_lease_idx ON jobs(status, lease_expires_at);
    """,
    4: """
    ALTER TABLE paper_candidates ADD COLUMN canonical_paper_path TEXT NOT NULL DEFAULT '';
    ALTER TABLE paper_candidates ADD COLUMN content_hash TEXT NOT NULL DEFAULT '';
    ALTER TABLE paper_candidates ADD COLUMN ingested_at TEXT;
    """,
    5: """
    CREATE UNIQUE INDEX agent_sessions_provider_ref_idx ON agent_sessions(provider, external_ref) WHERE external_ref != '';
    CREATE INDEX agent_sessions_object_status_idx ON agent_sessions(object_id, status);
    """,
    6: """
    CREATE TABLE herdr_launch_requests (
        object_id TEXT PRIMARY KEY REFERENCES objects(id) ON DELETE CASCADE,
        target_object_id TEXT NOT NULL REFERENCES objects(id) ON DELETE RESTRICT,
        agent_kind TEXT NOT NULL,
        task_type TEXT NOT NULL,
        task_summary TEXT NOT NULL,
        safe_config_json TEXT NOT NULL DEFAULT '{}',
        approved_at TEXT
    );
    CREATE INDEX herdr_launch_requests_target_idx ON herdr_launch_requests(target_object_id);
    """,
    7: """
    CREATE TABLE herdr_executions (
        object_id TEXT PRIMARY KEY REFERENCES objects(id) ON DELETE CASCADE,
        launch_request_object_id TEXT NOT NULL REFERENCES herdr_launch_requests(object_id) ON DELETE RESTRICT,
        target_object_id TEXT NOT NULL REFERENCES objects(id) ON DELETE RESTRICT,
        state TEXT NOT NULL CHECK (state IN ('prepared','authorized','claimed','starting','running','completed','failed','attention_required','revoked')),
        approved_request_revision INTEGER NOT NULL CHECK (approved_request_revision >= 1),
        approved_snapshot_hash TEXT NOT NULL,
        not_after TEXT NOT NULL,
        attempt INTEGER NOT NULL DEFAULT 0 CHECK (attempt >= 0),
        safe_runtime_json TEXT NOT NULL DEFAULT '{}',
        authorized_at TEXT,
        revoked_at TEXT,
        terminal_at TEXT,
        lease_token_hash TEXT NOT NULL DEFAULT '',
        lease_owner TEXT NOT NULL DEFAULT '',
        lease_expires_at TEXT,
        internal_agent_name TEXT NOT NULL DEFAULT '',
        session_fingerprint TEXT NOT NULL DEFAULT ''
    );
    CREATE INDEX herdr_executions_request_idx ON herdr_executions(launch_request_object_id, state);
    CREATE INDEX herdr_executions_state_deadline_idx ON herdr_executions(state, not_after);
    CREATE UNIQUE INDEX herdr_executions_one_active_idx ON herdr_executions(launch_request_object_id) WHERE terminal_at IS NULL;
    """
}


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def _require_enum(value: str, allowed: frozenset[str], label: str) -> str:
    value = str(value or "").strip()
    if value not in allowed:
        raise ValueError(f"invalid {label}: {value}")
    return value


def _require_id(value: str, label: str = "id") -> str:
    value = str(value or "").strip()
    if not _ID_PART.fullmatch(value):
        raise ValueError(f"invalid {label}: {value}")
    return value


def _json(value: Any, label: str) -> str:
    try:
        encoded = json.dumps(value if value is not None else {}, ensure_ascii=False, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be JSON serializable") from exc
    if len(encoded.encode("utf-8")) > 64 * 1024:
        raise ValueError(f"{label} exceeds 64 KiB")
    return encoded


def _decode_row(row: sqlite3.Row, json_fields: tuple[str, ...] = ()) -> dict[str, Any]:
    result = dict(row)
    for field in json_fields:
        if field in result:
            result[field.removesuffix("_json")] = json.loads(result.pop(field) or "{}")
    return result


class V2Store:
    """Project-local v2 runtime store.

    Constructing the store does not touch disk. `initialize()` is the explicit
    creation/migration boundary.
    """

    def __init__(self, project_root: pathlib.Path | str):
        self.project_root = pathlib.Path(project_root).expanduser().resolve()
        self.path = self.project_root / DB_RELATIVE_PATH

    def exists(self) -> bool:
        return self.path.is_file()

    def initialize(self) -> int:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)"
            )
            applied = {row[0] for row in conn.execute("SELECT version FROM schema_migrations")}
            unknown = [version for version in applied if version > SCHEMA_VERSION]
            if unknown:
                raise RuntimeError(f"database schema is newer than this application: {max(unknown)}")
            for version in sorted(_MIGRATIONS):
                if version not in applied:
                    conn.executescript(_MIGRATIONS[version])
                    conn.execute(
                        "INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?)",
                        (version, _now()),
                    )
            conn.commit()
        return self.schema_version()

    def schema_version(self) -> int:
        if not self.exists():
            return 0
        with self._connect(readonly=True) as conn:
            row = conn.execute("SELECT MAX(version) FROM schema_migrations").fetchone()
            return int(row[0] or 0)

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        self._require_initialized()
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                yield conn
            except Exception:
                conn.rollback()
                raise
            else:
                conn.commit()

    def create_object(
        self,
        *,
        object_id: str,
        object_type: str,
        project_id: str,
        title: str = "",
        lifecycle_status: str = "active",
        canonical_path: str = "",
        actor_kind: str = "human",
        actor_id: str = "",
    ) -> dict[str, Any]:
        object_id = _require_id(object_id, "object_id")
        object_type = _require_enum(object_type, OBJECT_TYPES, "object_type")
        project_id = _require_id(project_id, "project_id")
        timestamp = _now()
        with self.transaction() as conn:
            conn.execute(
                """INSERT INTO objects(
                    id,type,project_id,title,lifecycle_status,canonical_path,
                    created_at,created_by_kind,created_by_id,updated_at,updated_by_kind,updated_by_id
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    object_id,
                    object_type,
                    project_id,
                    str(title),
                    str(lifecycle_status),
                    str(canonical_path),
                    timestamp,
                    str(actor_kind),
                    str(actor_id),
                    timestamp,
                    str(actor_kind),
                    str(actor_id),
                ),
            )
            self._insert_event(
                conn,
                object_id=object_id,
                kind=f"{object_type}.created",
                actor_kind=actor_kind,
                actor_id=actor_id,
                from_revision=None,
                to_revision=1,
                summary=f"Created {object_type} {object_id}",
            )
        return self.get_object(object_id)

    def get_object(self, object_id: str) -> dict[str, Any]:
        self._require_initialized()
        with self._connect(readonly=True) as conn:
            row = conn.execute("SELECT * FROM objects WHERE id=?", (_require_id(object_id),)).fetchone()
        if row is None:
            raise KeyError(f"object not found: {object_id}")
        return _decode_row(row)

    def list_objects(self, object_type: str = "", lifecycle_status: str = "") -> list[dict[str, Any]]:
        self._require_initialized()
        clauses: list[str] = []
        values: list[str] = []
        if object_type:
            clauses.append("type=?")
            values.append(_require_enum(object_type, OBJECT_TYPES, "object_type"))
        if lifecycle_status:
            clauses.append("lifecycle_status=?")
            values.append(str(lifecycle_status))
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect(readonly=True) as conn:
            rows = conn.execute(f"SELECT * FROM objects{where} ORDER BY created_at, id", values).fetchall()
        return [_decode_row(row) for row in rows]

    def update_object(
        self,
        object_id: str,
        *,
        expected_revision: int,
        fields: dict[str, Any],
        actor_kind: str = "human",
        actor_id: str = "",
    ) -> dict[str, Any]:
        allowed = {"title", "lifecycle_status", "canonical_path"}
        unknown = set(fields) - allowed
        if unknown:
            raise ValueError(f"unsupported object fields: {', '.join(sorted(unknown))}")
        if not fields:
            return self.get_object(object_id)
        assignments = [f"{key}=?" for key in fields]
        values = [str(fields[key]) for key in fields]
        next_revision = int(expected_revision) + 1
        with self.transaction() as conn:
            cursor = conn.execute(
                f"""UPDATE objects SET {', '.join(assignments)}, revision=?, updated_at=?,
                    updated_by_kind=?, updated_by_id=? WHERE id=? AND revision=?""",
                values
                + [next_revision, _now(), str(actor_kind), str(actor_id), _require_id(object_id), expected_revision],
            )
            if cursor.rowcount != 1:
                existing = conn.execute("SELECT revision FROM objects WHERE id=?", (object_id,)).fetchone()
                if existing is None:
                    raise KeyError(f"object not found: {object_id}")
                raise ValueError(f"revision conflict: expected {expected_revision}, actual {existing[0]}")
            self._insert_event(
                conn,
                object_id=object_id,
                kind="object.updated",
                actor_kind=actor_kind,
                actor_id=actor_id,
                from_revision=expected_revision,
                to_revision=next_revision,
                summary=f"Updated {object_id}",
                details={"fields": sorted(fields)},
            )
        return self.get_object(object_id)

    def add_relation(
        self,
        *,
        from_object_id: str,
        relation_type: str,
        to_object_id: str,
        metadata: dict[str, Any] | None = None,
        actor_kind: str = "human",
        actor_id: str = "",
    ) -> dict[str, Any]:
        relation_type = _require_enum(relation_type, RELATION_TYPES, "relation_type")
        relation_id = _new_id("REL")
        with self.transaction() as conn:
            conn.execute(
                """INSERT INTO object_relations(
                    id,from_object_id,relation_type,to_object_id,metadata_json,
                    created_at,created_by_kind,created_by_id
                ) VALUES (?,?,?,?,?,?,?,?)""",
                (
                    relation_id,
                    _require_id(from_object_id, "from_object_id"),
                    relation_type,
                    _require_id(to_object_id, "to_object_id"),
                    _json(metadata, "relation metadata"),
                    _now(),
                    str(actor_kind),
                    str(actor_id),
                ),
            )
            self._insert_event(
                conn,
                object_id=from_object_id,
                kind="object.relation.added",
                actor_kind=actor_kind,
                actor_id=actor_id,
                from_revision=None,
                to_revision=None,
                summary=f"Added {relation_type} relation",
                details={"relation_id": relation_id, "to_object_id": to_object_id},
            )
        with self._connect(readonly=True) as conn:
            row = conn.execute("SELECT * FROM object_relations WHERE id=?", (relation_id,)).fetchone()
        return _decode_row(row, ("metadata_json",))

    def delete_relation(self, relation_id: str, *, expected_from_object_id: str = "", actor_kind: str = "human", actor_id: str = "") -> dict[str, Any]:
        relation_id=_require_id(relation_id,"relation_id")
        with self.transaction() as conn:
            row=conn.execute("SELECT * FROM object_relations WHERE id=?",(relation_id,)).fetchone()
            if row is None: raise KeyError(f"relation not found: {relation_id}")
            if expected_from_object_id and row["from_object_id"]!=_require_id(expected_from_object_id,"expected_from_object_id"): raise ValueError("relation does not belong to expected source object")
            conn.execute("DELETE FROM object_relations WHERE id=?",(relation_id,))
            self._insert_event(conn,object_id=row["from_object_id"],kind="object.relation.removed",actor_kind=actor_kind,actor_id=actor_id,from_revision=None,to_revision=None,summary=f"Removed {row['relation_type']} relation",details={"relation_id":relation_id,"to_object_id":row["to_object_id"]})
        return _decode_row(row,("metadata_json",))

    def ensure_reference_relation(self, *, from_object_id: str, relation_type: str, to_object_id: str, target_type: str, project_id: str, target_title: str = "", target_canonical_path: str = "", metadata: dict[str, Any] | None = None, actor_kind: str = "human", actor_id: str = "") -> dict[str, Any]:
        relation_type=_require_enum(relation_type,RELATION_TYPES,"relation_type"); target_type=_require_enum(target_type,OBJECT_TYPES,"target_type"); relation_id=_new_id("REL"); timestamp=_now()
        with self.transaction() as conn:
            target=conn.execute("SELECT * FROM objects WHERE id=?",(_require_id(to_object_id,"to_object_id"),)).fetchone()
            if target is None:
                conn.execute("""INSERT INTO objects(id,type,project_id,title,lifecycle_status,canonical_path,created_at,created_by_kind,created_by_id,updated_at,updated_by_kind,updated_by_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",(to_object_id,target_type,_require_id(project_id,"project_id"),str(target_title),"reference",str(target_canonical_path),timestamp,actor_kind,actor_id,timestamp,actor_kind,actor_id))
                self._insert_event(conn,object_id=to_object_id,kind="object.reference_indexed",actor_kind=actor_kind,actor_id=actor_id,from_revision=None,to_revision=1,summary=f"Indexed {target_type} reference {to_object_id}",details={"authority":(metadata or {}).get("authority","")})
            elif target["type"]!=target_type: raise ValueError("indexed target type conflict")
            existing=conn.execute("SELECT * FROM object_relations WHERE from_object_id=? AND relation_type=? AND to_object_id=?",(_require_id(from_object_id,"from_object_id"),relation_type,to_object_id)).fetchone()
            if existing is not None: return _decode_row(existing,("metadata_json",))
            conn.execute("""INSERT INTO object_relations(id,from_object_id,relation_type,to_object_id,metadata_json,created_at,created_by_kind,created_by_id) VALUES (?,?,?,?,?,?,?,?)""",(relation_id,from_object_id,relation_type,to_object_id,_json(metadata,"relation metadata"),timestamp,actor_kind,actor_id))
            self._insert_event(conn,object_id=from_object_id,kind="object.relation.added",actor_kind=actor_kind,actor_id=actor_id,from_revision=None,to_revision=None,summary=f"Added {relation_type} relation",details={"relation_id":relation_id,"to_object_id":to_object_id})
            row=conn.execute("SELECT * FROM object_relations WHERE id=?",(relation_id,)).fetchone()
        return _decode_row(row,("metadata_json",))

    def list_relations(self, *, from_object_id: str = "", to_object_id: str = "") -> list[dict[str, Any]]:
        self._require_initialized()
        clauses: list[str] = []
        values: list[str] = []
        if from_object_id:
            clauses.append("from_object_id=?")
            values.append(_require_id(from_object_id, "from_object_id"))
        if to_object_id:
            clauses.append("to_object_id=?")
            values.append(_require_id(to_object_id, "to_object_id"))
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect(readonly=True) as conn:
            rows = conn.execute(f"SELECT * FROM object_relations{where} ORDER BY created_at, id", values).fetchall()
        return [_decode_row(row, ("metadata_json",)) for row in rows]

    def create_paper_candidate(
        self,
        *,
        object_id: str,
        project_id: str,
        citekey: str,
        title: str,
        source_url: str,
        authors: list[str] | None = None,
        year: str = "",
        doi: str = "",
        oa_url: str = "",
        source: str = "manual",
        recommendation_reason: str = "",
        actor_kind: str = "human",
        actor_id: str = "",
    ) -> dict[str, Any]:
        if not str(source_url).startswith(("https://", "http://")):
            raise ValueError("candidate source_url must be http(s)")
        with self.transaction() as conn:
            if source == "zotero-local":
                existing = conn.execute(
                    "SELECT object_id FROM paper_candidates WHERE source=? AND source_url=? ORDER BY object_id LIMIT 1",
                    (source, str(source_url)),
                ).fetchone()
                if existing is not None:
                    return self.get_paper_candidate(existing["object_id"])
            timestamp = _now()
            conn.execute(
                """INSERT INTO objects(
                    id,type,project_id,title,lifecycle_status,canonical_path,
                    created_at,created_by_kind,created_by_id,updated_at,updated_by_kind,updated_by_id
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    _require_id(object_id, "object_id"), "paper_candidate", _require_id(project_id, "project_id"),
                    str(title), "proposed", "", timestamp, str(actor_kind), str(actor_id),
                    timestamp, str(actor_kind), str(actor_id),
                ),
            )
            conn.execute(
                """INSERT INTO paper_candidates(
                    object_id,citekey,authors_json,year,doi,source_url,oa_url,source,
                    recommendation_reason,verification_status
                ) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    object_id, _require_id(citekey, "citekey"), _json(authors or [], "candidate authors"),
                    str(year), str(doi), str(source_url), str(oa_url or ""), str(source),
                    str(recommendation_reason)[:4000], "unverified",
                ),
            )
            self._insert_event(
                conn, object_id=object_id, kind="paper_candidate.created", actor_kind=actor_kind,
                actor_id=actor_id, from_revision=None, to_revision=1,
                summary=f"Created paper candidate {object_id}", details={"source": source},
            )
        return self.get_paper_candidate(object_id)

    def get_paper_candidate(self, object_id: str) -> dict[str, Any]:
        self._require_initialized()
        with self._connect(readonly=True) as conn:
            row = conn.execute(
                """SELECT o.*,p.citekey,p.authors_json,p.year,p.doi,p.source_url,p.oa_url,p.source,
                    p.recommendation_reason,p.verification_status,p.acquisition_job_id,
                    p.canonical_paper_path,p.content_hash,p.ingested_at
                    FROM objects o JOIN paper_candidates p ON p.object_id=o.id WHERE o.id=?""",
                (_require_id(object_id, "object_id"),),
            ).fetchone()
        if row is None:
            raise KeyError(f"paper candidate not found: {object_id}")
        return _decode_row(row, ("authors_json",))

    def list_paper_candidates(self, lifecycle_status: str = "") -> list[dict[str, Any]]:
        self._require_initialized()
        where = " WHERE o.lifecycle_status=?" if lifecycle_status else ""
        values = (str(lifecycle_status),) if lifecycle_status else ()
        with self._connect(readonly=True) as conn:
            rows = conn.execute(
                """SELECT o.*,p.citekey,p.authors_json,p.year,p.doi,p.source_url,p.oa_url,p.source,
                    p.recommendation_reason,p.verification_status,p.acquisition_job_id,
                    p.canonical_paper_path,p.content_hash,p.ingested_at
                    FROM objects o JOIN paper_candidates p ON p.object_id=o.id""" + where + " ORDER BY o.created_at,o.id",
                values,
            ).fetchall()
        return [_decode_row(row, ("authors_json",)) for row in rows]

    def update_paper_candidate_status(
        self,
        object_id: str,
        *,
        expected_revision: int,
        lifecycle_status: str,
        actor_kind: str = "human",
        actor_id: str = "",
    ) -> dict[str, Any]:
        allowed = {"proposed", "accepted", "dismissed", "hidden", "expired"}
        if lifecycle_status not in allowed:
            raise ValueError(f"invalid paper candidate status: {lifecycle_status}")
        self.update_object(
            object_id, expected_revision=expected_revision,
            fields={"lifecycle_status": lifecycle_status}, actor_kind=actor_kind, actor_id=actor_id,
        )
        return self.get_paper_candidate(object_id)

    def create_candidate_acquisition_pipeline(
        self,
        object_id: str,
        *,
        expected_revision: int,
        actor_id: str = "",
        download_timeout_seconds: int = 300,
        mineru_timeout_seconds: int = 1800,
    ) -> dict[str, Any]:
        object_id = _require_id(object_id, "object_id")
        with self.transaction() as conn:
            row = conn.execute(
                """SELECT o.revision,o.lifecycle_status,p.oa_url,p.source,p.source_url,p.citekey,p.acquisition_job_id
                    FROM objects o JOIN paper_candidates p ON p.object_id=o.id WHERE o.id=?""",
                (object_id,),
            ).fetchone()
            if row is None:
                raise KeyError(f"paper candidate not found: {object_id}")
            if row["revision"] != int(expected_revision):
                raise ValueError(f"revision conflict: expected {expected_revision}, actual {row['revision']}")
            local_match = re.fullmatch(r"https://www\.zotero\.org/items/(\d+)",str(row["source_url"] or "")) if row["source"]=="zotero-local" else None
            if row["source"]=="zotero-local" and not local_match:
                raise ValueError("candidate has no valid Zotero item identity")
            if row["source"]!="zotero-local" and not str(row["oa_url"] or "").startswith(("https://", "http://")):
                raise ValueError("candidate has no verified OA PDF URL")
            if row["acquisition_job_id"]:
                download = conn.execute("SELECT * FROM jobs WHERE id=?", (row["acquisition_job_id"],)).fetchone()
                mineru = conn.execute("SELECT * FROM jobs WHERE depends_on_job_id=? ORDER BY created_at LIMIT 1", (row["acquisition_job_id"],)).fetchone()
                return {"candidate": self.get_paper_candidate(object_id), "download_job": _decode_row(download, ("request_json", "result_json")), "mineru_job": _decode_row(mineru, ("request_json", "result_json")) if mineru else None}
            timestamp = _now(); download_id = _new_id("JOB"); mineru_id = _new_id("JOB")
            download_kind="zotero_copy" if local_match else "paper_download"
            download_request = {"candidate_id": object_id, "citekey": row["citekey"], "destination": "staging"}
            if local_match: download_request["item_id"]=int(local_match.group(1))
            else: download_request["url"]=row["oa_url"]
            conn.execute(
                """INSERT INTO jobs(id,kind,status,target_object_id,idempotency_key,request_json,created_at,timeout_seconds)
                    VALUES (?,?,?,?,?,?,?,?)""",
                (download_id, download_kind, "queued", object_id, f"{object_id}:download", _json(download_request, "download request"), timestamp, download_timeout_seconds),
            )
            conn.execute(
                """INSERT INTO jobs(id,kind,status,target_object_id,idempotency_key,request_json,created_at,timeout_seconds,depends_on_job_id)
                    VALUES (?,?,?,?,?,?,?,?,?)""",
                (mineru_id, "mineru", "queued", object_id, f"{object_id}:mineru", _json({"candidate_id": object_id, "source_job_id": download_id, "destination": "staging"}, "mineru request"), timestamp, mineru_timeout_seconds, download_id),
            )
            conn.execute("UPDATE paper_candidates SET acquisition_job_id=? WHERE object_id=?", (download_id, object_id))
            conn.execute(
                """UPDATE objects SET lifecycle_status='accepted',revision=revision+1,updated_at=?,updated_by_kind='human',updated_by_id=?
                    WHERE id=? AND revision=?""",
                (timestamp, str(actor_id), object_id, expected_revision),
            )
            self._insert_event(
                conn, object_id=object_id, kind="paper_candidate.acquisition_requested", actor_kind="human", actor_id=actor_id,
                from_revision=expected_revision, to_revision=expected_revision + 1, summary=f"Queued staged acquisition for {object_id}",
                details={"download_job_id": download_id, "mineru_job_id": mineru_id, "canonical_write": False},
            )
            candidate_row = conn.execute(
                """SELECT o.*,p.citekey,p.authors_json,p.year,p.doi,p.source_url,p.oa_url,p.source,
                    p.recommendation_reason,p.verification_status,p.acquisition_job_id,
                    p.canonical_paper_path,p.content_hash,p.ingested_at
                    FROM objects o JOIN paper_candidates p ON p.object_id=o.id WHERE o.id=?""", (object_id,),
            ).fetchone()
            download = conn.execute("SELECT * FROM jobs WHERE id=?", (download_id,)).fetchone()
            mineru = conn.execute("SELECT * FROM jobs WHERE id=?", (mineru_id,)).fetchone()
        return {"candidate": _decode_row(candidate_row, ("authors_json",)), "download_job": _decode_row(download, ("request_json", "result_json")), "mineru_job": _decode_row(mineru, ("request_json", "result_json"))}

    def _index_ingested_paper(self, conn: sqlite3.Connection, object_id: str, actor_id: str) -> bool:
        row = conn.execute(
            "SELECT o.project_id,o.title,p.citekey,p.verification_status,p.canonical_paper_path "
            "FROM objects o JOIN paper_candidates p ON p.object_id=o.id WHERE o.id=?", (object_id,),
        ).fetchone()
        if row is None or row["verification_status"] != "ingested" or not row["canonical_paper_path"]:
            raise ValueError("paper reference requires an ingested candidate")
        existing = conn.execute("SELECT type,canonical_path FROM objects WHERE id=?", (row["citekey"],)).fetchone()
        if existing:
            if existing["type"] != "paper" or existing["canonical_path"] != row["canonical_paper_path"]:
                raise ValueError(f"paper reference identity conflict: {row['citekey']}")
            return False
        timestamp = _now()
        conn.execute(
            "INSERT INTO objects(id,type,project_id,title,lifecycle_status,canonical_path,created_at,created_by_kind,created_by_id,updated_at,updated_by_kind,updated_by_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (row["citekey"], "paper", row["project_id"], row["title"], "reference", row["canonical_paper_path"],
             timestamp, "human", actor_id, timestamp, "human", actor_id),
        )
        self._insert_event(conn, object_id=row["citekey"], kind="paper.reference_indexed", actor_kind="human", actor_id=actor_id,
                           from_revision=None, to_revision=1, summary="Indexed ingested paper reference",
                           details={"candidate_id":object_id})
        return True

    def index_ingested_papers(self, *, actor_id: str = "") -> dict[str, int]:
        """Explicit repair for earlier ingests; does not modify research files."""
        with self.transaction() as conn:
            rows = conn.execute("SELECT object_id FROM paper_candidates WHERE verification_status='ingested'").fetchall()
            added = sum(self._index_ingested_paper(conn, row["object_id"], actor_id) for row in rows)
        return {"indexed":added, "already_indexed":len(rows)-added}

    def mark_candidate_ingested(
        self,
        object_id: str,
        *,
        expected_revision: int,
        canonical_paper_path: str,
        content_hash: str,
        actor_id: str = "",
    ) -> dict[str, Any]:
        if not str(content_hash).startswith("sha256:"):
            raise ValueError("content_hash must be sha256")
        timestamp = _now()
        with self.transaction() as conn:
            cursor = conn.execute(
                """UPDATE objects SET lifecycle_status='ingested',revision=revision+1,canonical_path=?,
                    updated_at=?,updated_by_kind='human',updated_by_id=? WHERE id=? AND revision=?""",
                (str(canonical_paper_path), timestamp, str(actor_id), _require_id(object_id, "object_id"), int(expected_revision)),
            )
            if cursor.rowcount != 1:
                row = conn.execute("SELECT revision FROM objects WHERE id=?", (object_id,)).fetchone()
                actual = row[0] if row else "missing"
                raise ValueError(f"revision conflict: expected {expected_revision}, actual {actual}")
            conn.execute(
                """UPDATE paper_candidates SET verification_status='ingested',canonical_paper_path=?,content_hash=?,ingested_at=?
                    WHERE object_id=?""",
                (str(canonical_paper_path), str(content_hash), timestamp, object_id),
            )
            self._insert_event(
                conn, object_id=object_id, kind="paper_candidate.ingested", actor_kind="human", actor_id=actor_id,
                from_revision=expected_revision, to_revision=expected_revision + 1,
                summary=f"Ingested staged candidate {object_id}",
                details={"canonical_paper_path": canonical_paper_path, "content_hash": content_hash},
            )
            self._index_ingested_paper(conn, object_id, actor_id)
        return self.get_paper_candidate(object_id)

    def attach_candidate_job(self, object_id: str, job_id: str) -> dict[str, Any]:
        with self.transaction() as conn:
            cursor = conn.execute(
                "UPDATE paper_candidates SET acquisition_job_id=? WHERE object_id=?",
                (_require_id(job_id, "job_id"), _require_id(object_id, "object_id")),
            )
            if cursor.rowcount != 1:
                raise KeyError(f"paper candidate not found: {object_id}")
        return self.get_paper_candidate(object_id)

    def create_job(
        self,
        *,
        kind: str,
        target_object_id: str | None = None,
        idempotency_key: str | None = None,
        request: dict[str, Any] | None = None,
        timeout_seconds: int | None = None,
        depends_on_job_id: str | None = None,
    ) -> dict[str, Any]:
        kind = _require_id(kind, "job kind")
        if idempotency_key is not None and not str(idempotency_key).strip():
            raise ValueError("idempotency_key cannot be blank")
        job_id = _new_id("JOB")
        with self.transaction() as conn:
            if idempotency_key is not None:
                existing = conn.execute(
                    "SELECT * FROM jobs WHERE kind=? AND idempotency_key=?", (kind, str(idempotency_key))
                ).fetchone()
                if existing is not None:
                    return _decode_row(existing, ("request_json", "result_json"))
            conn.execute(
                """INSERT INTO jobs(
                    id,kind,status,target_object_id,idempotency_key,request_json,
                    created_at,timeout_seconds,depends_on_job_id
                ) VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    job_id,
                    kind,
                    "queued",
                    _require_id(target_object_id, "target_object_id") if target_object_id else None,
                    str(idempotency_key) if idempotency_key is not None else None,
                    _json(request, "job request"),
                    _now(),
                    timeout_seconds,
                    _require_id(depends_on_job_id, "depends_on_job_id") if depends_on_job_id else None,
                ),
            )
        return self.get_job(job_id)

    def list_jobs(self, *, status: str = "", target_object_id: str = "") -> list[dict[str, Any]]:
        self._require_initialized()
        clauses: list[str] = []
        values: list[Any] = []
        if status:
            clauses.append("status=?"); values.append(_require_enum(status, JOB_STATUSES, "job status"))
        if target_object_id:
            clauses.append("target_object_id=?"); values.append(_require_id(target_object_id, "target_object_id"))
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with self._connect(readonly=True) as conn:
            rows = conn.execute(f"SELECT * FROM jobs{where} ORDER BY created_at,id", values).fetchall()
        return [_decode_row(row, ("request_json", "result_json")) for row in rows]

    def claim_next_job(self, *, worker_id: str, kinds: list[str] | None = None, lease_seconds: int = 60, target_object_id: str = "") -> dict[str, Any] | None:
        worker_id = _require_id(worker_id, "worker_id")
        if not 5 <= int(lease_seconds) <= 3600:
            raise ValueError("lease_seconds must be between 5 and 3600")
        kinds = [_require_id(kind, "job kind") for kind in (kinds or [])]
        now = dt.datetime.now(dt.timezone.utc)
        expires = (now + dt.timedelta(seconds=int(lease_seconds))).isoformat(timespec="seconds")
        token = uuid.uuid4().hex
        with self.transaction() as conn:
            filters = ["j.status='queued'", "(j.depends_on_job_id IS NULL OR d.status='succeeded')"]
            values: list[Any] = []
            if kinds:
                filters.append(f"j.kind IN ({','.join('?' for _ in kinds)})"); values.extend(kinds)
            if target_object_id:
                filters.append("j.target_object_id=?"); values.append(_require_id(target_object_id,"target_object_id"))
            row = conn.execute(
                "SELECT j.id FROM jobs j LEFT JOIN jobs d ON d.id=j.depends_on_job_id WHERE "
                + " AND ".join(filters) + " ORDER BY j.created_at,j.id LIMIT 1", values,
            ).fetchone()
            if row is None:
                return None
            cursor = conn.execute(
                """UPDATE jobs SET status='running',started_at=COALESCE(started_at,?),attempt=attempt+1,
                    lease_token=?,lease_owner=?,lease_expires_at=?,last_heartbeat_at=?,revision=revision+1
                    WHERE id=? AND status='queued'""",
                (now.isoformat(timespec="seconds"), token, worker_id, expires, now.isoformat(timespec="seconds"), row[0]),
            )
            if cursor.rowcount != 1:
                return None
            claimed = conn.execute("SELECT * FROM jobs WHERE id=?", (row[0],)).fetchone()
        return _decode_row(claimed, ("request_json", "result_json"))

    def heartbeat_job(self, job_id: str, *, lease_token: str, lease_seconds: int = 60, progress: float | None = None) -> dict[str, Any]:
        if progress is not None and not 0 <= float(progress) <= 1:
            raise ValueError("progress must be between 0 and 1")
        now = dt.datetime.now(dt.timezone.utc)
        expires = (now + dt.timedelta(seconds=int(lease_seconds))).isoformat(timespec="seconds")
        with self.transaction() as conn:
            cursor = conn.execute(
                """UPDATE jobs SET lease_expires_at=?,last_heartbeat_at=?,progress=COALESCE(?,progress),revision=revision+1
                    WHERE id=? AND status='running' AND lease_token=?""",
                (expires, now.isoformat(timespec="seconds"), progress, _require_id(job_id, "job_id"), str(lease_token)),
            )
            if cursor.rowcount != 1:
                raise ValueError("job lease mismatch or job is not running")
        return self.get_job(job_id)

    def finish_claimed_job(self, job_id: str, *, lease_token: str, succeeded: bool, result: dict[str, Any] | None = None, error_class: str = "", error_message: str = "") -> dict[str, Any]:
        now = _now(); status = "succeeded" if succeeded else "failed"
        with self.transaction() as conn:
            cursor = conn.execute(
                """UPDATE jobs SET status=?,progress=?,result_json=?,error_class=?,error_message=?,finished_at=?,
                    lease_token='',lease_owner='',lease_expires_at=NULL,last_heartbeat_at=?,revision=revision+1
                    WHERE id=? AND status='running' AND lease_token=?""",
                (status, 1 if succeeded else None, _json(result, "job result"), str(error_class), str(error_message)[:2000], now, now, _require_id(job_id, "job_id"), str(lease_token)),
            )
            if cursor.rowcount != 1:
                raise ValueError("job lease mismatch or job is not running")
        return self.get_job(job_id)

    def recover_expired_jobs(self, *, now: str | None = None) -> int:
        timestamp = str(now or _now())
        with self.transaction() as conn:
            cursor = conn.execute(
                """UPDATE jobs SET status='queued',lease_token='',lease_owner='',lease_expires_at=NULL,
                    last_heartbeat_at=NULL,error_class='LeaseExpired',error_message='worker lease expired; requeued',revision=revision+1
                    WHERE status='running' AND lease_expires_at IS NOT NULL AND lease_expires_at<?""",
                (timestamp,),
            )
            return int(cursor.rowcount)

    def get_job(self, job_id: str) -> dict[str, Any]:
        self._require_initialized()
        with self._connect(readonly=True) as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id=?", (_require_id(job_id, "job_id"),)).fetchone()
        if row is None:
            raise KeyError(f"job not found: {job_id}")
        return _decode_row(row, ("request_json", "result_json"))

    def transition_job(
        self,
        job_id: str,
        *,
        expected_revision: int,
        status: str,
        progress: float | None = None,
        result: dict[str, Any] | None = None,
        error_class: str = "",
        error_message: str = "",
    ) -> dict[str, Any]:
        status = _require_enum(status, JOB_STATUSES, "job status")
        if progress is not None and not 0 <= float(progress) <= 1:
            raise ValueError("progress must be between 0 and 1")
        now = _now()
        started_at = now if status == "running" else None
        finished_at = now if status in {"succeeded", "failed", "cancelled"} else None
        with self.transaction() as conn:
            current = conn.execute("SELECT status FROM jobs WHERE id=?", (_require_id(job_id, "job_id"),)).fetchone()
            if current is None:
                raise KeyError(f"job not found: {job_id}")
            allowed = {
                "queued": {"running", "cancelled"},
                "running": {"succeeded", "failed", "cancelled"},
                "failed": {"queued"},
                "succeeded": set(),
                "cancelled": set(),
            }
            if status not in allowed[current[0]]:
                raise ValueError(f"invalid job transition: {current[0]} -> {status}")
            cursor = conn.execute(
                """UPDATE jobs SET status=?, progress=?, result_json=?, error_class=?, error_message=?,
                    started_at=COALESCE(started_at,?), finished_at=?, attempt=attempt+?, revision=revision+1
                    WHERE id=? AND revision=?""",
                (
                    status,
                    progress,
                    _json(result, "job result"),
                    str(error_class),
                    str(error_message)[:2000],
                    started_at,
                    finished_at,
                    1 if status == "running" else 0,
                    job_id,
                    expected_revision,
                ),
            )
            if cursor.rowcount != 1:
                actual = conn.execute("SELECT revision FROM jobs WHERE id=?", (job_id,)).fetchone()[0]
                raise ValueError(f"revision conflict: expected {expected_revision}, actual {actual}")
        return self.get_job(job_id)

    def retry_failed_job(self, job_id: str, *, expected_revision: int, reason: str, actor_id: str = "") -> dict[str, Any]:
        if not str(reason).strip(): raise ValueError("job retry reason is required")
        job_id = _require_id(job_id, "job_id"); now = _now()
        with self.transaction() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
            if row is None: raise KeyError(f"job not found: {job_id}")
            if row["revision"] != int(expected_revision): raise ValueError(f"revision conflict: expected {expected_revision}, actual {row['revision']}")
            if row["status"] != "failed": raise ValueError(f"only failed jobs can be retried: {row['status']}")
            dependency = conn.execute("SELECT status FROM jobs WHERE id=?", (row["depends_on_job_id"],)).fetchone() if row["depends_on_job_id"] else None
            if dependency and dependency["status"] != "succeeded": raise ValueError(f"job dependency is not succeeded: {dependency['status']}")
            conn.execute("""UPDATE jobs SET status='queued',progress=NULL,result_json='{}',error_class='',error_message='',finished_at=NULL,
                lease_token='',lease_owner='',lease_expires_at=NULL,last_heartbeat_at=NULL,revision=revision+1 WHERE id=?""", (job_id,))
            if row["target_object_id"]:
                self._insert_event(conn,object_id=row["target_object_id"],kind="job.retry_requested",actor_kind="human",actor_id=actor_id,from_revision=None,to_revision=None,summary=f"Retry requested for {job_id}",details={"job_id":job_id,"kind":row["kind"],"reason":str(reason)[:1000],"worker_started":False})
        return self.get_job(job_id)

    def cancel_queued_job(self, job_id: str, *, expected_revision: int, reason: str, actor_id: str = "") -> list[dict[str, Any]]:
        if not str(reason).strip(): raise ValueError("job cancellation reason is required")
        job_id = _require_id(job_id, "job_id"); now = _now()
        with self.transaction() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
            if row is None: raise KeyError(f"job not found: {job_id}")
            if row["revision"] != int(expected_revision): raise ValueError(f"revision conflict: expected {expected_revision}, actual {row['revision']}")
            if row["status"] != "queued": raise ValueError(f"only queued jobs can be cancelled: {row['status']}")
            dependent_rows = conn.execute("""WITH RECURSIVE descendants(id) AS (
                SELECT id FROM jobs WHERE depends_on_job_id=? AND status='queued'
                UNION ALL SELECT j.id FROM jobs j JOIN descendants d ON j.depends_on_job_id=d.id WHERE j.status='queued'
            ) SELECT id FROM descendants""", (job_id,)).fetchall()
            ids = [job_id] + [item["id"] for item in dependent_rows]
            conn.execute(f"UPDATE jobs SET status='cancelled',finished_at=?,error_class='HumanCancelled',error_message=?,revision=revision+1 WHERE id IN ({','.join('?' for _ in ids)})", [now, str(reason)[:2000], *ids])
            if row["target_object_id"]:
                self._insert_event(conn,object_id=row["target_object_id"],kind="job.cancelled",actor_kind="human",actor_id=actor_id,from_revision=None,to_revision=None,summary=f"Cancelled queued job {job_id}",details={"job_ids":ids,"reason":str(reason)[:1000],"running_process_stopped":False})
        return [self.get_job(item) for item in ids]

    def bind_agent_session(
        self,
        *,
        session_id: str,
        provider: str,
        object_id: str,
        task_type: str,
        external_ref: str,
        status: str = "live",
        agent: str = "",
        model: str = "",
    ) -> dict[str, Any]:
        allowed_statuses = frozenset({"requested", "live", "paused", "stale", "completed", "failed"})
        allowed_tasks = frozenset({"discussion", "research", "implementation", "monitoring", "analysis"})
        session_id = _require_id(session_id, "session_id")
        provider = _require_id(provider, "provider")
        status = _require_enum(status, allowed_statuses, "agent session status")
        task_type = _require_enum(task_type, allowed_tasks, "agent task_type")
        external_ref = str(external_ref or "").strip()
        if not external_ref or len(external_ref) > 2048:
            raise ValueError("external_ref is required and must be at most 2048 characters")
        forbidden = ("sk-", "api_key", "authorization:", "bearer ", "prompt", "messages")
        if any(token in external_ref.lower() for token in forbidden):
            raise ValueError("external_ref contains forbidden sensitive content")
        now = _now()
        with self.transaction() as conn:
            existing = conn.execute("SELECT * FROM agent_sessions WHERE provider=? AND external_ref=?", (provider, external_ref)).fetchone()
            if existing is not None:
                if existing["object_id"] != _require_id(object_id, "object_id"):
                    raise ValueError("agent session is already bound to another object")
                conn.execute(
                    """UPDATE agent_sessions SET status=?,task_type=?,agent=?,model=?,last_seen_at=?,revision=revision+1
                        WHERE id=?""", (status, task_type, str(agent)[:120], str(model)[:200], now, existing["id"]),
                )
                self._insert_event(conn,object_id=object_id,kind="agent_session.binding_refreshed",actor_kind="human",actor_id="",from_revision=None,to_revision=None,summary=f"Refreshed agent session binding {existing['id']}",details={"session_index_id":existing["id"],"provider":provider,"messages_copied":False,"prompt_copied":False})
                refreshed = conn.execute("SELECT * FROM agent_sessions WHERE id=?", (existing["id"],)).fetchone()
                return dict(refreshed)
            conn.execute(
                """INSERT INTO agent_sessions(id,provider,status,object_id,task_type,external_ref,agent,model,created_at,last_seen_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (session_id, provider, status, _require_id(object_id, "object_id"), task_type, external_ref, str(agent)[:120], str(model)[:200], now, now),
            )
            self._insert_event(conn,object_id=object_id,kind="agent_session.bound",actor_kind="human",actor_id="",from_revision=None,to_revision=None,summary=f"Bound agent session index {session_id}",details={"session_index_id":session_id,"provider":provider,"task_type":task_type,"messages_copied":False,"prompt_copied":False})
        return self.get_agent_session(session_id)

    def get_agent_session(self, session_id: str) -> dict[str, Any]:
        self._require_initialized()
        with self._connect(readonly=True) as conn:
            row = conn.execute("SELECT * FROM agent_sessions WHERE id=?", (_require_id(session_id, "session_id"),)).fetchone()
        if row is None:
            raise KeyError(f"agent session not found: {session_id}")
        return dict(row)

    def list_agent_sessions(self, *, object_id: str = "", status: str = "") -> list[dict[str, Any]]:
        self._require_initialized(); clauses=[]; values=[]
        if object_id: clauses.append("object_id=?"); values.append(_require_id(object_id, "object_id"))
        if status: clauses.append("status=?"); values.append(str(status))
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with self._connect(readonly=True) as conn:
            rows = conn.execute(f"SELECT * FROM agent_sessions{where} ORDER BY last_seen_at DESC,id", values).fetchall()
        return [dict(row) for row in rows]

    def update_agent_session_status(self, session_id: str, *, expected_revision: int, status: str) -> dict[str, Any]:
        allowed = frozenset({"requested", "live", "paused", "stale", "completed", "failed"})
        status = _require_enum(status, allowed, "agent session status")
        with self.transaction() as conn:
            cursor = conn.execute(
                "UPDATE agent_sessions SET status=?,last_seen_at=?,revision=revision+1 WHERE id=? AND revision=?",
                (status, _now(), _require_id(session_id, "session_id"), int(expected_revision)),
            )
            if cursor.rowcount != 1:
                row = conn.execute("SELECT revision FROM agent_sessions WHERE id=?", (session_id,)).fetchone()
                raise ValueError(f"revision conflict: expected {expected_revision}, actual {row[0] if row else 'missing'}")
        return self.get_agent_session(session_id)

    @staticmethod
    def _validate_launch_config(config: dict[str, Any]) -> dict[str, Any]:
        config = dict(config or {})
        unknown = set(config) - {"reasoning_effort", "max_turns", "topology", "reference_ids"}
        if unknown:
            raise ValueError(f"unsupported launch configuration: {', '.join(sorted(unknown))}")
        effort = _require_enum(config.get("reasoning_effort", "medium"), frozenset({"low", "medium", "high", "xhigh"}), "reasoning_effort")
        max_turns = int(config.get("max_turns", 5))
        if not 1 <= max_turns <= 20:
            raise ValueError("max_turns must be between 1 and 20")
        result = {"reasoning_effort": effort, "max_turns": max_turns}
        if "topology" in config:
            result["topology"] = _require_enum(
                config["topology"], frozenset({"new_tab", "split"}), "Herdr topology"
            )
        if "reference_ids" in config:
            reference_ids=config["reference_ids"]
            if not isinstance(reference_ids,list) or len(reference_ids)>12 or any(not isinstance(item,str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,159}",item) for item in reference_ids):
                raise ValueError("reference_ids must contain at most 12 safe object IDs")
            result["reference_ids"]=list(dict.fromkeys(reference_ids))
        return result

    def create_herdr_launch_request(
        self, *, object_id: str, project_id: str, target_object_id: str,
        agent_kind: str, task_type: str, task_summary: str,
        safe_config: dict[str, Any] | None = None, actor_id: str = "",
    ) -> dict[str, Any]:
        object_id = _require_id(object_id, "launch_request_id")
        project_id = _require_id(project_id, "project_id")
        target_object_id = _require_id(target_object_id, "target_object_id")
        agent_kind = _require_enum(agent_kind, frozenset({"pi", "codex"}), "agent_kind")
        task_type = _require_enum(task_type, frozenset({"discussion", "research", "implementation", "run_implementation", "monitoring", "analysis"}), "agent task_type")
        summary = " ".join(str(task_summary or "").split())
        if not summary or len(summary) > 500:
            raise ValueError("task_summary is required and must be at most 500 characters")
        # Keep ordinary domain language such as “token 生命周期” usable. Reject
        # credential-shaped values, not the words themselves: schemes, explicit
        # assignments, and common secret-bearing fields with a value.
        if re.search(r"(?i)(?:bearer\s+[A-Za-z0-9._~+/=-]{12,}|(?:api[_-]?key|password|secret|access[_-]?token|lease[_-]?token)\s*[:=]\s*\S+)", summary):
            raise ValueError("task_summary contains forbidden sensitive content")
        config = self._validate_launch_config(safe_config or {})
        now = _now()
        with self.transaction() as conn:
            target = conn.execute("SELECT type FROM objects WHERE id=?", (target_object_id,)).fetchone()
            if target is None: raise KeyError(f"launch target not found: {target_object_id}")
            if target["type"] not in {"automation", "question", "experiment", "run"}:
                raise ValueError(f"unsupported launch target type: {target['type']}")
            if task_type == "run_implementation" and target["type"] != "run":
                raise ValueError("run_implementation launch requires a Run target")
            conn.execute(
                """INSERT INTO objects(id,type,project_id,title,lifecycle_status,canonical_path,revision,created_at,created_by_kind,created_by_id,updated_at,updated_by_kind,updated_by_id)
                    VALUES (?, 'herdr_launch_request', ?, ?, 'draft', '', 1, ?, 'human', ?, ?, 'human', ?)""",
                (object_id, project_id, summary, now, str(actor_id), now, str(actor_id)),
            )
            conn.execute(
                """INSERT INTO herdr_launch_requests(object_id,target_object_id,agent_kind,task_type,task_summary,safe_config_json)
                    VALUES (?,?,?,?,?,?)""",
                (object_id, target_object_id, agent_kind, task_type, summary, _json(config, "safe launch configuration")),
            )
            self._insert_event(conn, object_id=object_id, kind="herdr_launch_request.created", actor_kind="human", actor_id=actor_id,
                from_revision=None, to_revision=1, summary=f"Created Herdr launch request {object_id}",
                details={"target_object_id": target_object_id, "agent_kind": agent_kind, "task_type": task_type, "execution_started": False})
        return self.get_herdr_launch_request(object_id)

    def get_herdr_launch_request(self, object_id: str) -> dict[str, Any]:
        self._require_initialized()
        with self._connect(readonly=True) as conn:
            row = conn.execute(
                """SELECT o.*,r.target_object_id,r.agent_kind,r.task_type,r.task_summary,r.safe_config_json,r.approved_at
                    FROM objects o JOIN herdr_launch_requests r ON r.object_id=o.id WHERE o.id=?""",
                (_require_id(object_id, "launch_request_id"),),
            ).fetchone()
        if row is None: raise KeyError(f"Herdr launch request not found: {object_id}")
        return _decode_row(row, ("safe_config_json",))

    def list_herdr_launch_requests(self) -> list[dict[str, Any]]:
        self._require_initialized()
        with self._connect(readonly=True) as conn:
            rows = conn.execute(
                """SELECT o.*,r.target_object_id,r.agent_kind,r.task_type,r.task_summary,r.safe_config_json,r.approved_at
                    FROM objects o JOIN herdr_launch_requests r ON r.object_id=o.id ORDER BY o.created_at,o.id"""
            ).fetchall()
        return [_decode_row(row, ("safe_config_json",)) for row in rows]

    def transition_herdr_launch_request(self, object_id: str, *, expected_revision: int, status: str, actor_id: str = "") -> dict[str, Any]:
        allowed = {"draft": {"awaiting_approval", "cancelled"}, "awaiting_approval": {"approved", "cancelled"}, "approved": set(), "cancelled": set()}
        status = _require_enum(status, frozenset(allowed), "Herdr launch request status")
        object_id = _require_id(object_id, "launch_request_id"); now = _now()
        with self.transaction() as conn:
            row = conn.execute("SELECT revision,lifecycle_status FROM objects WHERE id=? AND type='herdr_launch_request'", (object_id,)).fetchone()
            if row is None: raise KeyError(f"Herdr launch request not found: {object_id}")
            if row["revision"] != int(expected_revision): raise ValueError(f"revision conflict: expected {expected_revision}, actual {row['revision']}")
            previous = row["lifecycle_status"]
            if status not in allowed.get(previous, set()): raise ValueError(f"invalid Herdr launch request transition: {previous} -> {status}")
            conn.execute("UPDATE objects SET lifecycle_status=?,revision=revision+1,updated_at=?,updated_by_kind='human',updated_by_id=? WHERE id=?", (status, now, str(actor_id), object_id))
            if status == "approved": conn.execute("UPDATE herdr_launch_requests SET approved_at=? WHERE object_id=?", (now, object_id))
            self._insert_event(conn, object_id=object_id, kind="herdr_launch_request.transitioned", actor_kind="human", actor_id=actor_id,
                from_revision=expected_revision, to_revision=expected_revision+1, summary=f"Herdr launch request {object_id}: {previous} -> {status}",
                details={"execution_started": False})
        return self.get_herdr_launch_request(object_id)

    @staticmethod
    def _approved_launch_snapshot(row: sqlite3.Row) -> tuple[dict[str, Any], str]:
        request_id = row["request_id"] if "request_id" in row.keys() else row["id"]
        request_revision = row["request_revision"] if "request_revision" in row.keys() else row["revision"]
        snapshot = {
            "schema": "survey-tool.herdr-approved-launch/v1",
            "request_id": request_id,
            "request_revision": request_revision,
            "target_object_id": row["target_object_id"],
            "agent_kind": row["agent_kind"],
            "task_type": row["task_type"],
            "task_summary": row["task_summary"],
            "safe_config": json.loads(row["safe_config_json"] or "{}"),
        }
        encoded = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return snapshot, "sha256:" + hashlib.sha256(encoded).hexdigest()

    def authorize_herdr_execution(
        self, *, execution_id: str, project_id: str, launch_request_id: str,
        expected_request_revision: int, capability: dict[str, Any],
        ttl_seconds: int = 300, actor_id: str = "",
    ) -> dict[str, Any]:
        execution_id = _require_id(execution_id, "execution_id")
        project_id = _require_id(project_id, "project_id")
        launch_request_id = _require_id(launch_request_id, "launch_request_id")
        ttl_seconds = int(ttl_seconds)
        if not 60 <= ttl_seconds <= 900: raise ValueError("authorization ttl_seconds must be between 60 and 900")
        now = _now()
        not_after = (dt.datetime.fromisoformat(now) + dt.timedelta(seconds=ttl_seconds)).isoformat(timespec="seconds")
        safe_runtime = {"execution_started": False, "herdr_invoked": False, "phase": "record_only"}
        with self.transaction() as conn:
            request = conn.execute(
                """SELECT o.id,o.revision,o.lifecycle_status,r.target_object_id,r.agent_kind,r.task_type,r.task_summary,r.safe_config_json
                    FROM objects o JOIN herdr_launch_requests r ON r.object_id=o.id WHERE o.id=?""",
                (launch_request_id,),
            ).fetchone()
            if request is None: raise KeyError(f"Herdr launch request not found: {launch_request_id}")
            support_key = "pi_supported" if request["agent_kind"] == "pi" else "codex_supported"
            if not all(capability.get(key) is True for key in ("managed", "cli_available", support_key)):
                raise ValueError("Herdr capability preflight is unavailable")
            if request["revision"] != int(expected_request_revision): raise ValueError(f"revision conflict: expected {expected_request_revision}, actual {request['revision']}")
            if request["lifecycle_status"] != "approved": raise ValueError("Herdr launch request must be approved before authorization")
            target = conn.execute("SELECT lifecycle_status FROM objects WHERE id=?", (request["target_object_id"],)).fetchone()
            if target is None: raise KeyError(f"launch target not found: {request['target_object_id']}")
            if target["lifecycle_status"] == "archived": raise ValueError("archived launch target cannot be authorized")
            active = conn.execute("SELECT object_id FROM herdr_executions WHERE launch_request_object_id=? AND terminal_at IS NULL", (launch_request_id,)).fetchone()
            if active is not None: raise ValueError(f"active Herdr execution already exists for request: {active['object_id']}")
            _, snapshot_hash = self._approved_launch_snapshot(request)
            conn.execute(
                """INSERT INTO objects(id,type,project_id,title,lifecycle_status,canonical_path,revision,created_at,created_by_kind,created_by_id,updated_at,updated_by_kind,updated_by_id)
                    VALUES (?, 'herdr_execution', ?, ?, 'authorized', '', 1, ?, 'human', ?, ?, 'human', ?)""",
                (execution_id, project_id, f"Execution authorization for {launch_request_id}", now, str(actor_id), now, str(actor_id)),
            )
            conn.execute(
                """INSERT INTO herdr_executions(object_id,launch_request_object_id,target_object_id,state,approved_request_revision,approved_snapshot_hash,not_after,attempt,safe_runtime_json,authorized_at)
                    VALUES (?,?,?,'authorized',?,?,?,?,?,?)""",
                (execution_id, launch_request_id, request["target_object_id"], request["revision"], snapshot_hash, not_after, 0, _json(safe_runtime, "safe runtime"), now),
            )
            self._insert_event(conn, object_id=execution_id, kind="herdr_execution.authorized", actor_kind="human", actor_id=actor_id,
                from_revision=None, to_revision=1, summary=f"Authorized Herdr execution {execution_id}",
                details={"launch_request_id": launch_request_id, "target_object_id": request["target_object_id"], "approved_request_revision": request["revision"], "not_after": not_after, "execution_started": False, "herdr_invoked": False})
        return self.get_herdr_execution(execution_id)

    def get_herdr_execution(self, execution_id: str) -> dict[str, Any]:
        self._require_initialized()
        with self._connect(readonly=True) as conn:
            row = conn.execute(
                """SELECT o.*,e.launch_request_object_id,e.target_object_id,e.state,e.approved_request_revision,e.approved_snapshot_hash,e.not_after,e.attempt,e.safe_runtime_json,e.authorized_at,e.revoked_at,e.terminal_at,e.lease_token_hash,e.lease_owner,e.lease_expires_at,e.internal_agent_name,e.session_fingerprint
                    FROM objects o JOIN herdr_executions e ON e.object_id=o.id WHERE o.id=?""",
                (_require_id(execution_id, "execution_id"),),
            ).fetchone()
        if row is None: raise KeyError(f"Herdr execution not found: {execution_id}")
        return _decode_row(row, ("safe_runtime_json",))

    def list_herdr_executions(self) -> list[dict[str, Any]]:
        self._require_initialized()
        with self._connect(readonly=True) as conn:
            rows = conn.execute(
                """SELECT o.*,e.launch_request_object_id,e.target_object_id,e.state,e.approved_request_revision,e.approved_snapshot_hash,e.not_after,e.attempt,e.safe_runtime_json,e.authorized_at,e.revoked_at,e.terminal_at,e.lease_token_hash,e.lease_owner,e.lease_expires_at,e.internal_agent_name,e.session_fingerprint
                    FROM objects o JOIN herdr_executions e ON e.object_id=o.id ORDER BY o.created_at,o.id"""
            ).fetchall()
        return [_decode_row(row, ("safe_runtime_json",)) for row in rows]

    def revoke_herdr_execution(self, execution_id: str, *, expected_revision: int, actor_id: str = "") -> dict[str, Any]:
        execution_id = _require_id(execution_id, "execution_id"); now = _now()
        with self.transaction() as conn:
            row = conn.execute("SELECT o.revision,e.state FROM objects o JOIN herdr_executions e ON e.object_id=o.id WHERE o.id=?", (execution_id,)).fetchone()
            if row is None: raise KeyError(f"Herdr execution not found: {execution_id}")
            if row["revision"] != int(expected_revision): raise ValueError(f"revision conflict: expected {expected_revision}, actual {row['revision']}")
            if row["state"] not in {"prepared", "authorized"}: raise ValueError(f"Herdr execution cannot be revoked after claim/start: {row['state']}")
            conn.execute("UPDATE objects SET lifecycle_status='revoked',revision=revision+1,updated_at=?,updated_by_kind='human',updated_by_id=? WHERE id=?", (now, str(actor_id), execution_id))
            conn.execute("UPDATE herdr_executions SET state='revoked',revoked_at=?,terminal_at=? WHERE object_id=?", (now, now, execution_id))
            self._insert_event(conn, object_id=execution_id, kind="herdr_execution.revoked", actor_kind="human", actor_id=actor_id,
                from_revision=expected_revision, to_revision=expected_revision+1, summary=f"Revoked Herdr execution {execution_id}",
                details={"execution_started": False, "herdr_invoked": False})
        return self.get_herdr_execution(execution_id)

    @staticmethod
    def _execution_now(now: dt.datetime | None = None) -> dt.datetime:
        value = now or dt.datetime.now(dt.timezone.utc)
        if value.tzinfo is None: value = value.replace(tzinfo=dt.timezone.utc)
        return value.astimezone(dt.timezone.utc)

    @staticmethod
    def _validate_execution_runtime(runtime: dict[str, Any] | None, *, phase: str) -> dict[str, Any]:
        runtime = dict(runtime or {})
        allowed = {"checks", "duration_ms", "error_class", "error_summary", "human_review_required"}
        unknown = set(runtime) - allowed
        if unknown: raise ValueError(f"unsupported execution runtime fields: {', '.join(sorted(unknown))}")
        check_names = {"environment_managed", "cli_available", "pi_supported", "codex_supported", "authorization_current", "request_snapshot_current", "target_available", "concurrency_available"}
        checks = dict(runtime.get("checks") or {})
        if set(checks) - check_names or any(type(value) is not bool for value in checks.values()):
            raise ValueError("execution runtime checks must be allowlisted booleans")
        duration_ms = int(runtime.get("duration_ms") or 0)
        if not 0 <= duration_ms <= 300_000: raise ValueError("execution runtime duration_ms is out of bounds")
        error_class = str(runtime.get("error_class") or "")
        error_summary = " ".join(str(runtime.get("error_summary") or "").split())
        if len(error_class) > 120 or len(error_summary) > 500: raise ValueError("execution runtime error summary is too long")
        return {"phase": phase, "execution_started": False, "herdr_invoked": False, "checks": checks,
                "duration_ms": duration_ms, "error_class": error_class, "error_summary": error_summary,
                "human_review_required": bool(runtime.get("human_review_required", False))}

    @staticmethod
    def _require_execution_lease(row: sqlite3.Row, *, lease_token: str, owner: str, now: dt.datetime) -> None:
        supplied_hash = hashlib.sha256(str(lease_token or "").encode("utf-8")).hexdigest()
        if row["lease_owner"] != owner or not secrets.compare_digest(str(row["lease_token_hash"] or ""), supplied_hash):
            raise ValueError("execution lease token or owner mismatch")
        deadline = dt.datetime.fromisoformat(str(row["lease_expires_at"] or "")) if row["lease_expires_at"] else None
        if deadline is None or deadline <= now: raise ValueError("execution lease has expired")

    def claim_herdr_execution(
        self, execution_id: str, *, expected_revision: int, owner: str,
        capability: dict[str, Any], lease_seconds: int = 60,
        now: dt.datetime | None = None,
    ) -> dict[str, Any]:
        execution_id = _require_id(execution_id, "execution_id"); owner = _require_id(owner, "lease owner")
        lease_seconds = int(lease_seconds)
        if not 15 <= lease_seconds <= 300: raise ValueError("execution lease_seconds must be between 15 and 300")
        instant = self._execution_now(now); timestamp = instant.isoformat(timespec="seconds")
        lease_expires = (instant + dt.timedelta(seconds=lease_seconds)).isoformat(timespec="seconds")
        raw_token = secrets.token_urlsafe(32); token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        with self.transaction() as conn:
            row = conn.execute(
                """SELECT o.revision,e.*,ro.id request_id,ro.revision request_revision,ro.lifecycle_status request_status,
                    r.target_object_id request_target_object_id,r.agent_kind,r.task_type,r.task_summary,r.safe_config_json,
                    target.lifecycle_status target_status
                    FROM objects o JOIN herdr_executions e ON e.object_id=o.id
                    JOIN objects ro ON ro.id=e.launch_request_object_id JOIN herdr_launch_requests r ON r.object_id=ro.id
                    JOIN objects target ON target.id=e.target_object_id WHERE o.id=?""", (execution_id,),
            ).fetchone()
            if row is None: raise KeyError(f"Herdr execution not found: {execution_id}")
            support_key = "pi_supported" if row["agent_kind"] == "pi" else "codex_supported"
            if not all(capability.get(key) is True for key in ("managed", "cli_available", support_key)):
                raise ValueError("Herdr capability preflight is unavailable")
            if row["revision"] != int(expected_revision): raise ValueError(f"revision conflict: expected {expected_revision}, actual {row['revision']}")
            if row["state"] != "authorized": raise ValueError(f"Herdr execution is not authorized: {row['state']}")
            if dt.datetime.fromisoformat(row["not_after"]) <= instant: raise ValueError("Herdr execution authorization has expired")
            if row["request_status"] != "approved" or row["request_revision"] != row["approved_request_revision"]:
                raise ValueError("approved Launch Request revision/status changed")
            _, current_hash = self._approved_launch_snapshot(row)
            if not secrets.compare_digest(current_hash, row["approved_snapshot_hash"]): raise ValueError("approved Launch Request snapshot changed")
            if row["request_target_object_id"] != row["target_object_id"] or row["target_status"] == "archived":
                raise ValueError("execution target is missing, changed, or archived")
            # A pre-start claim owns no Herdr resource. If its short lease has
            # expired, safely return it to authorized before applying the
            # project-wide concurrency limit. starting/running are deliberately
            # never reclaimed here because ownership may be ambiguous.
            expired_claims = conn.execute(
                """SELECT e.object_id,o.revision,e.lease_expires_at FROM herdr_executions e
                    JOIN objects o ON o.id=e.object_id
                    WHERE e.object_id!=? AND e.state='claimed' AND e.lease_expires_at IS NOT NULL""",
                (execution_id,),
            ).fetchall()
            for stale in expired_claims:
                deadline = dt.datetime.fromisoformat(str(stale["lease_expires_at"]))
                if deadline > instant:
                    continue
                conn.execute("UPDATE objects SET lifecycle_status='authorized',revision=revision+1,updated_at=?,updated_by_kind='system',updated_by_id='' WHERE id=?", (timestamp, stale["object_id"]))
                conn.execute("UPDATE herdr_executions SET state='authorized',lease_token_hash='',lease_owner='',lease_expires_at=NULL,safe_runtime_json=? WHERE object_id=?", (_json({"phase":"lease_recovered","execution_started":False,"herdr_invoked":False,"ownership_observation":"absent"}, "safe runtime"), stale["object_id"]))
                self._insert_event(conn, object_id=stale["object_id"], kind="herdr_execution.lease_recovered", actor_kind="system", actor_id="", from_revision=stale["revision"], to_revision=stale["revision"]+1, summary=f"Recovered expired pre-start Herdr lease {stale['object_id']}", details={"result_state":"authorized","execution_started":False,"herdr_invoked":False})
            concurrent = conn.execute("SELECT object_id FROM herdr_executions WHERE object_id!=? AND state IN ('claimed','starting','running')", (execution_id,)).fetchone()
            if concurrent is not None: raise ValueError("project Herdr execution concurrency limit reached")
            conn.execute("UPDATE objects SET lifecycle_status='claimed',revision=revision+1,updated_at=?,updated_by_kind='system',updated_by_id='' WHERE id=?", (timestamp, execution_id))
            conn.execute("UPDATE herdr_executions SET state='claimed',attempt=attempt+1,lease_token_hash=?,lease_owner=?,lease_expires_at=?,safe_runtime_json=? WHERE object_id=?",
                (token_hash, owner, lease_expires, _json({"phase":"preflight_claimed","execution_started":False,"herdr_invoked":False}, "safe runtime"), execution_id))
            self._insert_event(conn, object_id=execution_id, kind="herdr_execution.claimed", actor_kind="system", actor_id="",
                from_revision=expected_revision, to_revision=expected_revision+1, summary=f"Claimed Herdr execution {execution_id} for read-only preflight",
                details={"lease_expires_at":lease_expires,"attempt":row["attempt"]+1,"execution_started":False,"herdr_invoked":False})
        return {"execution": self.get_herdr_execution(execution_id), "lease_token": raw_token}

    def heartbeat_herdr_execution(self, execution_id: str, *, lease_token: str, owner: str, lease_seconds: int = 60, now: dt.datetime | None = None) -> dict[str, Any]:
        execution_id = _require_id(execution_id, "execution_id"); owner = _require_id(owner, "lease owner")
        lease_seconds = int(lease_seconds)
        if not 15 <= lease_seconds <= 300: raise ValueError("execution lease_seconds must be between 15 and 300")
        instant=self._execution_now(now); timestamp=instant.isoformat(timespec="seconds"); deadline=(instant+dt.timedelta(seconds=lease_seconds)).isoformat(timespec="seconds")
        with self.transaction() as conn:
            row=conn.execute("SELECT o.revision,e.* FROM objects o JOIN herdr_executions e ON e.object_id=o.id WHERE o.id=?",(execution_id,)).fetchone()
            if row is None: raise KeyError(f"Herdr execution not found: {execution_id}")
            if row["state"]!="claimed": raise ValueError(f"Herdr execution is not claimed: {row['state']}")
            self._require_execution_lease(row,lease_token=lease_token,owner=owner,now=instant)
            conn.execute("UPDATE objects SET revision=revision+1,updated_at=?,updated_by_kind='system',updated_by_id='' WHERE id=?",(timestamp,execution_id))
            conn.execute("UPDATE herdr_executions SET lease_expires_at=? WHERE object_id=?",(deadline,execution_id))
            self._insert_event(conn,object_id=execution_id,kind="herdr_execution.heartbeat",actor_kind="system",actor_id="",from_revision=row["revision"],to_revision=row["revision"]+1,summary=f"Renewed preflight lease for {execution_id}",details={"lease_expires_at":deadline,"execution_started":False,"herdr_invoked":False})
        return self.get_herdr_execution(execution_id)

    def finish_herdr_preflight(
        self, execution_id: str, *, lease_token: str, owner: str,
        status: str, runtime: dict[str, Any] | None = None,
        now: dt.datetime | None = None,
    ) -> dict[str, Any]:
        status=_require_enum(status,frozenset({"completed","failed","attention_required"}),"preflight finish status")
        execution_id=_require_id(execution_id,"execution_id"); owner=_require_id(owner,"lease owner")
        instant=self._execution_now(now); timestamp=instant.isoformat(timespec="seconds")
        safe=self._validate_execution_runtime(runtime,phase="preflight_completed" if status=="completed" else "preflight_failed" if status=="failed" else "attention_required")
        with self.transaction() as conn:
            row=conn.execute("SELECT o.revision,e.* FROM objects o JOIN herdr_executions e ON e.object_id=o.id WHERE o.id=?",(execution_id,)).fetchone()
            if row is None: raise KeyError(f"Herdr execution not found: {execution_id}")
            if row["state"]!="claimed": raise ValueError(f"Herdr execution is not claimed: {row['state']}")
            self._require_execution_lease(row,lease_token=lease_token,owner=owner,now=instant)
            conn.execute("UPDATE objects SET lifecycle_status=?,revision=revision+1,updated_at=?,updated_by_kind='system',updated_by_id='' WHERE id=?",(status,timestamp,execution_id))
            conn.execute("UPDATE herdr_executions SET state=?,safe_runtime_json=?,terminal_at=?,lease_token_hash='',lease_owner='',lease_expires_at=NULL WHERE object_id=?",(status,_json(safe,"safe runtime"),timestamp,execution_id))
            self._insert_event(conn,object_id=execution_id,kind=f"herdr_execution.{status}",actor_kind="system",actor_id="",from_revision=row["revision"],to_revision=row["revision"]+1,summary=f"Finished read-only preflight for {execution_id}: {status}",details={"execution_started":False,"herdr_invoked":False,"phase":safe["phase"]})
        return self.get_herdr_execution(execution_id)

    def record_owned_agent_started(self, execution_id: str, *, lease_token: str, owner: str, internal_agent_name: str, lease_seconds: int = 300, now: dt.datetime | None = None) -> dict[str, Any]:
        execution_id=_require_id(execution_id,"execution_id"); owner=_require_id(owner,"lease owner")
        internal_agent_name=str(internal_agent_name or "")
        if not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}",internal_agent_name): raise ValueError("invalid internal agent name")
        lease_seconds=int(lease_seconds)
        if not 15 <= lease_seconds <= 300: raise ValueError("execution lease_seconds must be between 15 and 300")
        instant=self._execution_now(now); timestamp=instant.isoformat(timespec="seconds")
        lease_expires=(instant+dt.timedelta(seconds=lease_seconds)).isoformat(timespec="seconds")
        safe={"phase":"owned_agent_started","execution_started":True,"herdr_invoked":True,"ownership_attested":True,"prompt_submitted":False}
        with self.transaction() as conn:
            row=conn.execute("SELECT o.revision,e.* FROM objects o JOIN herdr_executions e ON e.object_id=o.id WHERE o.id=?",(execution_id,)).fetchone()
            if row is None: raise KeyError(f"Herdr execution not found: {execution_id}")
            if row["state"]!="claimed": raise ValueError(f"Herdr execution is not claimed: {row['state']}")
            self._require_execution_lease(row,lease_token=lease_token,owner=owner,now=instant)
            conn.execute("UPDATE objects SET lifecycle_status='running',revision=revision+1,updated_at=?,updated_by_kind='system',updated_by_id='' WHERE id=?",(timestamp,execution_id))
            conn.execute("UPDATE herdr_executions SET state='running',internal_agent_name=?,safe_runtime_json=?,lease_expires_at=? WHERE object_id=?",(internal_agent_name,_json(safe,"safe runtime"),lease_expires,execution_id))
            self._insert_event(conn,object_id=execution_id,kind="herdr_execution.ownership_attested",actor_kind="system",actor_id="",from_revision=row["revision"],to_revision=row["revision"]+1,summary=f"Established private ownership for Herdr execution {execution_id}",details={"state":"running","execution_started":True,"herdr_invoked":True,"prompt_submitted":False})
        return self.get_herdr_execution(execution_id)

    def finish_owned_prompt(self, execution_id: str, *, lease_token: str, owner: str,
                            status: str, prompt_submitted: bool,
                            prompt_settled: bool, now: dt.datetime | None = None) -> dict[str, Any]:
        status=_require_enum(status,frozenset({"completed","failed","attention_required"}),"owned prompt finish status")
        execution_id=_require_id(execution_id,"execution_id"); owner=_require_id(owner,"lease owner")
        instant=self._execution_now(now); timestamp=instant.isoformat(timespec="seconds")
        safe={"phase":"owned_prompt_completed" if status=="completed" else "owned_prompt_attention" if status=="attention_required" else "owned_prompt_failed",
              "execution_started":True,"herdr_invoked":True,"ownership_attested":True,
              "prompt_submitted":bool(prompt_submitted),"prompt_settled":bool(prompt_settled),
              "human_review_required":status!="completed"}
        with self.transaction() as conn:
            row=conn.execute("SELECT o.revision,e.* FROM objects o JOIN herdr_executions e ON e.object_id=o.id WHERE o.id=?",(execution_id,)).fetchone()
            if row is None: raise KeyError(f"Herdr execution not found: {execution_id}")
            if row["state"]!="running": raise ValueError(f"Herdr execution is not running: {row['state']}")
            self._require_execution_lease(row,lease_token=lease_token,owner=owner,now=instant)
            conn.execute("UPDATE objects SET lifecycle_status=?,revision=revision+1,updated_at=?,updated_by_kind='system',updated_by_id='' WHERE id=?",(status,timestamp,execution_id))
            conn.execute("UPDATE herdr_executions SET state=?,safe_runtime_json=?,terminal_at=?,lease_token_hash='',lease_owner='',lease_expires_at=NULL WHERE object_id=?",(status,_json(safe,"safe runtime"),timestamp,execution_id))
            self._insert_event(conn,object_id=execution_id,kind=f"herdr_execution.prompt_{status}",actor_kind="system",actor_id="",from_revision=row["revision"],to_revision=row["revision"]+1,summary=f"Finished owned Herdr prompt for {execution_id}: {status}",details={"prompt_submitted":bool(prompt_submitted),"prompt_settled":bool(prompt_settled),"human_review_required":status!="completed"})
        return self.get_herdr_execution(execution_id)

    def mark_owned_start_attention(self, execution_id: str, *, lease_token: str, owner: str, split_succeeded: bool, now: dt.datetime | None = None) -> dict[str, Any]:
        execution_id=_require_id(execution_id,"execution_id"); owner=_require_id(owner,"lease owner")
        instant=self._execution_now(now); timestamp=instant.isoformat(timespec="seconds")
        safe={"phase":"owned_start_attention","execution_started":False,"herdr_invoked":True,"split_succeeded":bool(split_succeeded),"ownership_attested":False,"prompt_submitted":False,"human_review_required":True}
        with self.transaction() as conn:
            row=conn.execute("SELECT o.revision,e.* FROM objects o JOIN herdr_executions e ON e.object_id=o.id WHERE o.id=?",(execution_id,)).fetchone()
            if row is None: raise KeyError(f"Herdr execution not found: {execution_id}")
            if row["state"]!="claimed": raise ValueError(f"Herdr execution is not claimed: {row['state']}")
            self._require_execution_lease(row,lease_token=lease_token,owner=owner,now=instant)
            conn.execute("UPDATE objects SET lifecycle_status='attention_required',revision=revision+1,updated_at=?,updated_by_kind='system',updated_by_id='' WHERE id=?",(timestamp,execution_id))
            conn.execute("UPDATE herdr_executions SET state='attention_required',safe_runtime_json=?,terminal_at=?,lease_token_hash='',lease_owner='',lease_expires_at=NULL WHERE object_id=?",(_json(safe,"safe runtime"),timestamp,execution_id))
            self._insert_event(conn,object_id=execution_id,kind="herdr_execution.attention_required",actor_kind="system",actor_id="",from_revision=row["revision"],to_revision=row["revision"]+1,summary=f"Owned Agent start requires human attention for {execution_id}",details={"split_succeeded":bool(split_succeeded),"ownership_attested":False,"prompt_submitted":False})
        return self.get_herdr_execution(execution_id)

    def reconcile_expired_herdr_execution(self, execution_id: str, *, expected_revision: int, ownership_observation: str, now: dt.datetime | None = None) -> dict[str, Any]:
        observation=_require_enum(ownership_observation,frozenset({"absent","live","ambiguous"}),"ownership observation")
        execution_id=_require_id(execution_id,"execution_id"); instant=self._execution_now(now); timestamp=instant.isoformat(timespec="seconds")
        next_state="authorized" if observation=="absent" else "attention_required"
        with self.transaction() as conn:
            row=conn.execute("SELECT o.revision,e.* FROM objects o JOIN herdr_executions e ON e.object_id=o.id WHERE o.id=?",(execution_id,)).fetchone()
            if row is None: raise KeyError(f"Herdr execution not found: {execution_id}")
            if row["revision"]!=int(expected_revision): raise ValueError(f"revision conflict: expected {expected_revision}, actual {row['revision']}")
            if row["state"]!="claimed": raise ValueError(f"Herdr execution is not claimed: {row['state']}")
            deadline=dt.datetime.fromisoformat(str(row["lease_expires_at"] or "")) if row["lease_expires_at"] else None
            if deadline is None or deadline>instant: raise ValueError("execution lease is not expired")
            terminal=timestamp if next_state=="attention_required" else None
            safe={"phase":"lease_reconciled","execution_started":False,"herdr_invoked":False,"ownership_observation":observation,"human_review_required":next_state=="attention_required"}
            conn.execute("UPDATE objects SET lifecycle_status=?,revision=revision+1,updated_at=?,updated_by_kind='system',updated_by_id='' WHERE id=?",(next_state,timestamp,execution_id))
            conn.execute("UPDATE herdr_executions SET state=?,safe_runtime_json=?,terminal_at=?,lease_token_hash='',lease_owner='',lease_expires_at=NULL WHERE object_id=?",(next_state,_json(safe,"safe runtime"),terminal,execution_id))
            self._insert_event(conn,object_id=execution_id,kind="herdr_execution.lease_reconciled",actor_kind="system",actor_id="",from_revision=expected_revision,to_revision=expected_revision+1,summary=f"Reconciled expired preflight lease for {execution_id}: {observation}",details={"ownership_observation":observation,"result_state":next_state,"execution_started":False,"herdr_invoked":False})
        return self.get_herdr_execution(execution_id)

    def create_automation(
        self,
        *,
        object_id: str,
        project_id: str,
        title: str,
        automation_type: str,
        target_type: str,
        target_id: str,
        budget: dict[str, Any],
        actor_id: str = "",
    ) -> dict[str, Any]:
        automation_type = _require_enum(automation_type, frozenset({"research", "experiment", "hybrid"}), "automation_type")
        target_type = _require_enum(target_type, frozenset({"question", "experiment"}), "automation target_type")
        normalized = self._validate_automation_budget(budget)
        normalized.update({"target_type": target_type, "target_id": _require_id(target_id, "target_id")})
        self.create_object(object_id=object_id, object_type="automation", project_id=project_id, title=title, lifecycle_status="draft", actor_kind="human", actor_id=actor_id)
        try:
            with self.transaction() as conn:
                conn.execute(
                    """INSERT INTO automations(object_id,automation_type,phase,budget_json,approval_json)
                        VALUES (?,?,?,?,?)""",
                    (object_id, automation_type, "intake", _json(normalized, "automation budget"), _json({}, "automation approval")),
                )
        except Exception:
            with self.transaction() as conn: conn.execute("DELETE FROM objects WHERE id=?", (object_id,))
            raise
        return self.get_automation(object_id)

    @staticmethod
    def _validate_automation_budget(budget: dict[str, Any]) -> dict[str, Any]:
        limits = {"duration_minutes": (5, 1440), "max_rounds": (1, 100), "interval_minutes": (1, 240)}
        result: dict[str, Any] = {}
        for key, (minimum, maximum) in limits.items():
            value = int((budget or {}).get(key) or 0)
            if not minimum <= value <= maximum:
                raise ValueError(f"{key} must be between {minimum} and {maximum}")
            result[key] = value
        return result

    def get_automation(self, object_id: str) -> dict[str, Any]:
        self._require_initialized()
        with self._connect(readonly=True) as conn:
            row = conn.execute(
                """SELECT o.*,a.automation_type,a.phase,a.budget_json,a.approval_json,a.started_at,a.deadline_at,a.stopped_at
                    FROM objects o JOIN automations a ON a.object_id=o.id WHERE o.id=?""", (_require_id(object_id, "object_id"),),
            ).fetchone()
        if row is None: raise KeyError(f"automation not found: {object_id}")
        return _decode_row(row, ("budget_json", "approval_json"))

    def list_automations(self) -> list[dict[str, Any]]:
        self._require_initialized()
        with self._connect(readonly=True) as conn:
            rows = conn.execute(
                """SELECT o.*,a.automation_type,a.phase,a.budget_json,a.approval_json,a.started_at,a.deadline_at,a.stopped_at
                    FROM objects o JOIN automations a ON a.object_id=o.id ORDER BY o.created_at,o.id"""
            ).fetchall()
        return [_decode_row(row, ("budget_json", "approval_json")) for row in rows]

    def transition_automation(
        self,
        object_id: str,
        *,
        expected_revision: int,
        status: str,
        phase: str | None = None,
        approval: dict[str, Any] | None = None,
        actor_id: str = "",
    ) -> dict[str, Any]:
        statuses = {"draft", "awaiting_approval", "active", "paused", "checkpoint", "completed", "completed_with_warnings", "failed", "cancelled"}
        phases = {"intake", "research", "research_review", "experiment_planning", "experiment_execution", "synthesis"}
        if status not in statuses: raise ValueError(f"invalid automation status: {status}")
        if phase is not None and phase not in phases: raise ValueError(f"invalid automation phase: {phase}")
        allowed = {
            "draft": {"awaiting_approval", "cancelled"}, "awaiting_approval": {"active", "cancelled"},
            "active": {"paused", "checkpoint", "completed", "completed_with_warnings", "failed", "cancelled"},
            "paused": {"active", "cancelled"}, "checkpoint": {"active", "completed", "completed_with_warnings", "cancelled"},
            "completed": set(), "completed_with_warnings": set(), "failed": set(), "cancelled": set(),
        }
        now = _now()
        with self.transaction() as conn:
            row = conn.execute(
                """SELECT o.revision,o.lifecycle_status,a.automation_type,a.phase,a.budget_json,a.approval_json,a.deadline_at
                    FROM objects o JOIN automations a ON a.object_id=o.id WHERE o.id=?""", (_require_id(object_id, "object_id"),),
            ).fetchone()
            if row is None: raise KeyError(f"automation not found: {object_id}")
            if row["revision"] != int(expected_revision): raise ValueError(f"revision conflict: expected {expected_revision}, actual {row['revision']}")
            if status not in allowed.get(row["lifecycle_status"], set()): raise ValueError(f"invalid automation transition: {row['lifecycle_status']} -> {status}")
            next_phase = phase or row["phase"]
            approval_data = json.loads(row["approval_json"] or "{}")
            if approval: approval_data.update(approval)
            if status == "active" and row["lifecycle_status"] in {"awaiting_approval", "checkpoint"} and not approval_data.get("approved_by"):
                raise ValueError("human approval is required to activate automation")
            if row["automation_type"] == "hybrid" and next_phase in {"experiment_planning", "experiment_execution"} and not approval_data.get("experiment_phase_approved_by"):
                raise ValueError("hybrid experiment phase requires separate human approval")
            conn.execute(
                """UPDATE objects SET lifecycle_status=?,revision=revision+1,updated_at=?,updated_by_kind='human',updated_by_id=? WHERE id=?""",
                (status, now, str(actor_id), object_id),
            )
            deadline = row["deadline_at"]
            if status == "active" and not deadline:
                duration = int(json.loads(row["budget_json"])["duration_minutes"])
                deadline = (dt.datetime.fromisoformat(now) + dt.timedelta(minutes=duration)).isoformat(timespec="seconds")
            conn.execute(
                """UPDATE automations SET phase=?,approval_json=?,deadline_at=?,started_at=CASE WHEN ?='active' THEN COALESCE(started_at,?) ELSE started_at END,
                    stopped_at=CASE WHEN ? IN ('completed','completed_with_warnings','failed','cancelled') THEN ? ELSE stopped_at END WHERE object_id=?""",
                (next_phase, _json(approval_data, "automation approval"), deadline, status, now, status, now, object_id),
            )
            self._insert_event(conn, object_id=object_id, kind="automation.transitioned", actor_kind="human", actor_id=actor_id,
                from_revision=expected_revision, to_revision=expected_revision+1, summary=f"Automation {object_id}: {row['lifecycle_status']} -> {status}", details={"phase": next_phase})
        return self.get_automation(object_id)

    def archive_impact(self, object_ids: list[str]) -> list[dict[str, Any]]:
        self._require_initialized()
        ids=[_require_id(item,"object_id") for item in object_ids]
        if not ids: return []
        with self._connect(readonly=True) as conn:
            output=[]
            for object_id in ids:
                row=conn.execute("SELECT * FROM objects WHERE id=?",(object_id,)).fetchone()
                if row is None: raise KeyError(f"object not found: {object_id}")
                jobs=conn.execute("SELECT status,COUNT(*) count FROM jobs WHERE target_object_id=? GROUP BY status",(object_id,)).fetchall()
                relations=conn.execute("SELECT COUNT(*) FROM object_relations WHERE from_object_id=? OR to_object_id=?",(object_id,object_id)).fetchone()[0]
                sessions=conn.execute("SELECT COUNT(*) FROM agent_sessions WHERE object_id=?",(object_id,)).fetchone()[0]
                blockers=[]
                if row["type"] not in {"paper_candidate","automation"}: blockers.append("only native paper_candidate and automation objects can be archived")
                if row["type"]=="automation" and row["lifecycle_status"] in {"awaiting_approval","active","paused","checkpoint"}: blockers.append(f"automation must be draft or terminal before archival: {row['lifecycle_status']}")
                active_jobs=sum(item["count"] for item in jobs if item["status"] in {"queued","running"})
                if active_jobs: blockers.append(f"object has {active_jobs} queued/running jobs")
                output.append({"id":object_id,"type":row["type"],"title":row["title"],"lifecycle_status":row["lifecycle_status"],"revision":row["revision"],"canonical_path":row["canonical_path"],"jobs":{item["status"]:item["count"] for item in jobs},"relations":relations,"agent_sessions":sessions,"blockers":blockers,"hard_delete":False,"canonical_files_deleted":False,"staging_deleted":False})
        return output

    def archive_objects(
        self,
        items: list[dict[str, Any]],
        *,
        reason: str,
        actor_id: str = "",
        restore: bool = False,
    ) -> list[dict[str, Any]]:
        if not str(reason).strip(): raise ValueError("archive reason is required")
        if not items or len(items) > 100: raise ValueError("archive batch must contain 1 to 100 objects")
        normalized = [(_require_id(item.get("id", ""), "object_id"), int(item.get("expected_revision") or 0)) for item in items]
        if len({item[0] for item in normalized}) != len(normalized): raise ValueError("archive batch contains duplicate objects")
        timestamp = _now(); output=[]
        impacts={item["id"]:item for item in self.archive_impact([item[0] for item in normalized])}
        with self.transaction() as conn:
            rows = {row["id"]: row for row in conn.execute(f"SELECT * FROM objects WHERE id IN ({','.join('?' for _ in normalized)})", [item[0] for item in normalized]).fetchall()}
            for object_id, expected_revision in normalized:
                row = rows.get(object_id)
                if row is None: raise KeyError(f"object not found: {object_id}")
                if row["revision"] != expected_revision: raise ValueError(f"revision conflict for {object_id}: expected {expected_revision}, actual {row['revision']}")
                if restore and row["lifecycle_status"] != "archived": raise ValueError(f"object is not archived: {object_id}")
                if not restore and row["lifecycle_status"] == "archived": raise ValueError(f"object is already archived: {object_id}")
                if not restore and impacts[object_id]["blockers"]: raise ValueError(f"archive blocked for {object_id}: {'; '.join(impacts[object_id]['blockers'])}")
                if restore and row["type"] not in {"paper_candidate","automation"}: raise ValueError(f"restore is unsupported for object type: {row['type']}")
            for object_id, expected_revision in normalized:
                row=rows[object_id]
                previous_status=row["lifecycle_status"]
                if restore:
                    event=conn.execute("SELECT details_json FROM events WHERE object_id=? AND kind='object.archived' ORDER BY rowid DESC LIMIT 1",(object_id,)).fetchone()
                    details=json.loads(event["details_json"] or "{}") if event else {}
                    next_status=str(details.get("previous_status") or ("proposed" if row["type"]=="paper_candidate" else "draft"))
                else: next_status="archived"
                conn.execute("UPDATE objects SET lifecycle_status=?,revision=revision+1,updated_at=?,updated_by_kind='human',updated_by_id=? WHERE id=?", (next_status,timestamp,str(actor_id),object_id))
                self._insert_event(conn,object_id=object_id,kind="object.restored" if restore else "object.archived",actor_kind="human",actor_id=actor_id,from_revision=expected_revision,to_revision=expected_revision+1,summary=f"{'Restored' if restore else 'Archived'} {object_id}",details={"reason":str(reason)[:1000],"previous_status":previous_status if not restore else "archived","restored_status":next_status if restore else "","hard_delete":False,"canonical_files_deleted":False,"staging_deleted":False,"impact":impacts[object_id]})
                output.append({"id":object_id,"type":row["type"],"lifecycle_status":next_status,"revision":expected_revision+1})
        return output

    def create_inbox_item(
        self,
        *,
        kind: str,
        target_object_id: str,
        title: str,
        reason: str = "",
        due_at: str | None = None,
    ) -> dict[str, Any]:
        item_id = _new_id("INBOX")
        with self.transaction() as conn:
            existing = conn.execute(
                "SELECT * FROM inbox_items WHERE kind=? AND target_object_id=? AND status='open'",
                (_require_id(kind, "inbox kind"), _require_id(target_object_id, "target_object_id")),
            ).fetchone()
            if existing is not None:
                return _decode_row(existing)
            conn.execute(
                """INSERT INTO inbox_items(
                    id,kind,status,target_object_id,title,reason,due_at,created_at
                ) VALUES (?,?,?,?,?,?,?,?)""",
                (item_id, kind, "open", target_object_id, str(title), str(reason), due_at, _now()),
            )
        return self.list_inbox()[0] if len(self.list_inbox()) == 1 else next(
            item for item in self.list_inbox() if item["id"] == item_id
        )

    def list_inbox(self, status: str = "open") -> list[dict[str, Any]]:
        self._require_initialized()
        values: tuple[Any, ...] = ()
        where = ""
        if status:
            where = " WHERE status=?"
            values = (_require_enum(status, INBOX_STATUSES, "inbox status"),)
        with self._connect(readonly=True) as conn:
            rows = conn.execute(f"SELECT * FROM inbox_items{where} ORDER BY created_at, id", values).fetchall()
        return [_decode_row(row) for row in rows]

    def list_events(self, object_id: str = "") -> list[dict[str, Any]]:
        self._require_initialized()
        where = " WHERE object_id=?" if object_id else ""
        values = (_require_id(object_id, "object_id"),) if object_id else ()
        with self._connect(readonly=True) as conn:
            rows = conn.execute(f"SELECT * FROM events{where} ORDER BY rowid", values).fetchall()
        return [_decode_row(row, ("details_json",)) for row in rows]

    def _insert_event(
        self,
        conn: sqlite3.Connection,
        *,
        object_id: str | None,
        kind: str,
        actor_kind: str,
        actor_id: str,
        from_revision: int | None,
        to_revision: int | None,
        summary: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        conn.execute(
            """INSERT INTO events(
                id,object_id,kind,actor_kind,actor_id,occurred_at,from_revision,to_revision,summary,details_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                _new_id("EV"),
                object_id,
                _require_id(kind, "event kind"),
                str(actor_kind),
                str(actor_id),
                _now(),
                from_revision,
                to_revision,
                str(summary)[:1000],
                _json(details, "event details"),
            ),
        )

    def _require_initialized(self) -> None:
        if not self.exists():
            raise RuntimeError("v2 store is not initialized")

    @contextmanager
    def _connect(self, readonly: bool = False) -> Iterator[sqlite3.Connection]:
        if readonly:
            conn = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True, timeout=5)
        else:
            conn = sqlite3.connect(self.path, timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        if not readonly:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=FULL")
        try:
            yield conn
        finally:
            conn.close()


def v2_capabilities(project_root: pathlib.Path | str | None = None) -> dict[str, Any]:
    try:
        herdr = herdr_capability()
    except Exception:
        herdr = {
            "managed": False,
            "cli_available": False,
            "codex_supported": False,
            "probe_status": "unavailable",
            "access": "discovery_only",
        }
    result: dict[str, Any] = {
        "schema": "survey-tool.capabilities/v2",
        "api_version": 2,
        "storage_schema_version": SCHEMA_VERSION,
        "features": {
            "objects": "foundation",
            "relations": "foundation",
            "events": "foundation",
            "jobs": "foundation",
            "inbox": "foundation",
            "paper_candidates": "foundation",
            "automation": "foundation",
            "agent_sessions": "foundation",
            "legacy_experiment_authority": "json",
            "research_prose_authority": "markdown",
        },
        "herdr": herdr,
    }
    if project_root is not None:
        store = V2Store(project_root)
        result["project_store"] = {
            "initialized": store.exists(),
            "schema_version": store.schema_version(),
            "relative_path": str(DB_RELATIVE_PATH),
        }
    return result
