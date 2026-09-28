"""Timestamped named-run preparation and append-only lineage indexing."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

SCHEMA = "iploc-szy.named-run/v1"
INDEX_SCHEMA = "iploc-szy.run-index-event/v1"
_SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _validated_name(value: Any, label: str) -> str:
    text = str(value or "")
    if not _SAFE_NAME.fullmatch(text):
        raise ValueError(
            f"{label} must match {_SAFE_NAME.pattern!r}, got {text!r}"
        )
    return text


def _checkpoint(path_value: Any, *, require_trainer_state: bool = True) -> Optional[Path]:
    if path_value in (None, "", "None"):
        return None
    path = Path(str(path_value)).resolve()
    adapter = path / "adapter" / "adapter_model.safetensors"
    trainer_state = path / "trainer_state.pt"
    if not path.is_dir() or not adapter.is_file() or (
        require_trainer_state and not trainer_state.is_file()
    ):
        requirement = (
            "adapter/adapter_model.safetensors and trainer_state.pt"
            if require_trainer_state
            else "adapter/adapter_model.safetensors"
        )
        raise FileNotFoundError(f"checkpoint must contain {requirement}: {path}")
    return path


def _load_manifest(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != SCHEMA:
        raise ValueError(f"unsupported named-run manifest schema in {path}")
    return payload


def _parent_from_checkpoint(
    checkpoint: Optional[Path], experiment_dir: Path
) -> Dict[str, Any]:
    if checkpoint is None:
        return {
            "run_id": None,
            "run_dir": None,
            "checkpoint_dir": None,
            "root_run_id": None,
            "root_run_dir": None,
            "generation": 0,
            "ancestors": [],
            "legacy": False,
        }
    if not _inside(checkpoint, experiment_dir):
        raise ValueError(
            f"parent checkpoint must stay inside {experiment_dir}: {checkpoint}"
        )
    manifest_path = None
    for directory in (checkpoint, *checkpoint.parents):
        candidate = directory / "run_manifest.json"
        if candidate.is_file():
            manifest_path = candidate
            break
        if directory == experiment_dir:
            break
    if manifest_path is not None:
        parent = _load_manifest(manifest_path)
        parent_id = str(parent["run_id"])
        ancestors = list(parent.get("lineage", {}).get("ancestors", [])) + [
            parent_id
        ]
        return {
            "run_id": parent_id,
            "run_dir": str(manifest_path.parent),
            "checkpoint_dir": str(checkpoint),
            "root_run_id": parent.get("lineage", {}).get("root_run_id")
            or parent_id,
            "root_run_dir": parent.get("lineage", {}).get("root_run_dir")
            or (
                parent["work_dir"]
                if int(parent.get("lineage", {}).get("generation", 0)) == 0
                else None
            ),
            "generation": int(parent.get("lineage", {}).get("generation", 0)) + 1,
            "ancestors": ancestors,
            "legacy": False,
        }
    if checkpoint.parent.name == "checkpoints":
        run_dir = checkpoint.parent.parent
    elif (checkpoint / "metrics.json").is_file():
        # A completed run publishes its final adapter directly under work_dir.
        # Read-only child actions may use that adapter even though no resumable
        # trainer state is written beside it.
        run_dir = checkpoint
    else:
        raise ValueError(
            "legacy checkpoint must have <run_dir>/checkpoints/<checkpoint> "
            "layout or be a completed run work_dir with metrics.json"
        )
    return {
        "run_id": run_dir.name,
        "run_dir": str(run_dir),
        "checkpoint_dir": str(checkpoint),
        "root_run_id": run_dir.name,
        "root_run_dir": str(run_dir),
        "generation": 1,
        "ancestors": [run_dir.name],
        "legacy": True,
    }


def _append_jsonl(path: Path, lock_path: Path, row: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(row), ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def _atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(dict(payload), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _index_event(
    experiment_dir: Path,
    manifest: Mapping[str, Any],
    event: str,
    status: str,
    details: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    row = {
        "schema": INDEX_SCHEMA,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "status": status,
        "experiment_id": manifest["experiment_id"],
        "run_id": manifest["run_id"],
        "run_name": manifest["run_name"],
        "run_kind": manifest["run_kind"],
        "work_dir": manifest["work_dir"],
        "parent_run_id": manifest["lineage"]["parent_run_id"],
        "parent_checkpoint": manifest["lineage"]["parent_checkpoint"],
        "root_run_id": manifest["lineage"]["root_run_id"],
        "generation": manifest["lineage"]["generation"],
        "details": dict(details or {}),
    }
    _append_jsonl(
        experiment_dir / "run_index.jsonl",
        experiment_dir / ".run_index.lock",
        row,
    )
    return row


def _index_legacy_parent(
    experiment_dir: Path, experiment_id: str, parent: Mapping[str, Any]
) -> None:
    """Make a pre-existing root visible without creating a manifest for it."""
    row = {
        "schema": INDEX_SCHEMA,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "event": "legacy_parent_observed",
        "status": "legacy",
        "experiment_id": experiment_id,
        "run_id": parent["run_id"],
        "run_name": parent["run_id"],
        "run_kind": "legacy-root",
        "work_dir": parent["run_dir"],
        "parent_run_id": None,
        "parent_checkpoint": None,
        "root_run_id": parent["run_id"],
        "generation": 0,
        "details": {"observed_from_checkpoint": parent["checkpoint_dir"]},
    }
    _append_jsonl(
        experiment_dir / "run_index.jsonl",
        experiment_dir / ".run_index.lock",
        row,
    )


def prepare_named_run(
    config: Mapping[str, Any],
    config_path: Path,
    cfg_options: Iterable[str] = (),
) -> Dict[str, Any]:
    named = dict(config.get("named_run") or {})
    if not named:
        raise ValueError("config has no named_run section")
    experiment_id = _validated_name(named.get("experiment_id"), "experiment_id")
    run_name = _validated_name(named.get("run_name"), "run_name")
    run_kind = _validated_name(named.get("run_kind"), "run_kind")
    experiment_root = Path(str(named["experiment_root"])).resolve()
    experiment_dir = (experiment_root / experiment_id).resolve()
    if not _inside(experiment_dir, experiment_root):
        raise ValueError("experiment directory escapes experiment_root")
    experiment_dir.mkdir(parents=True, exist_ok=True)
    mode = str(named.get("mode", "new"))
    runner_config = config.get("runner") or {}
    runner_initialize = runner_config.get("initialize_from")
    runner_resume = runner_config.get("resume_from")
    branch = dict(config.get("branch") or {})
    action = str(branch.get("action", "train"))

    if mode == "new":
        timestamp_value = named.get("timestamp", "auto")
        timestamp = utc_timestamp() if timestamp_value == "auto" else _validated_name(
            timestamp_value, "timestamp"
        )
        run_id = f"{timestamp}--{run_name}"
        parent_value = named.get("parent_checkpoint")
        if parent_value in (None, "", "None"):
            parent_value = runner_initialize
        elif runner_initialize not in (None, "", "None") and Path(
            str(parent_value)
        ).resolve() != Path(str(runner_initialize)).resolve():
            raise ValueError(
                "named_run.parent_checkpoint conflicts with runner.initialize_from"
            )
        if runner_resume not in (None, "", "None"):
            raise ValueError("new branch must not set runner.resume_from")
        resume_checkpoint = _checkpoint(
            parent_value, require_trainer_state=action == "train"
        )
        if bool(named.get("require_parent_checkpoint", False)) and resume_checkpoint is None:
            raise ValueError(
                "this run config requires named_run.parent_checkpoint (or "
                "runner.resume_from)"
            )
        parent = _parent_from_checkpoint(resume_checkpoint, experiment_dir)
        if resume_checkpoint is None:
            work_dir = (experiment_dir / run_id).resolve()
            root_run_dir = work_dir
        else:
            if not parent["root_run_dir"]:
                raise ValueError("parent manifest has no resolvable root_run_dir")
            root_run_dir = Path(str(parent["root_run_dir"])).resolve()
            work_dir = (root_run_dir / "branches" / run_id).resolve()
        if not _inside(work_dir, experiment_dir):
            raise ValueError("resolved work_dir escapes the selected experiment")
        if work_dir.exists():
            raise FileExistsError(f"named-run directory already exists: {work_dir}")
        work_dir.parent.mkdir(parents=True, exist_ok=True)
        work_dir.mkdir(parents=False, exist_ok=False)
        created_at = datetime.now(timezone.utc).isoformat()
        root_run_id = parent["root_run_id"] or run_id
        manifest = {
            "schema": SCHEMA,
            "status": "prepared",
            "experiment_id": experiment_id,
            "run_id": run_id,
            "run_name": run_name,
            "run_kind": run_kind,
            "created_at_utc": created_at,
            "updated_at_utc": created_at,
            "experiment_dir": str(experiment_dir),
            "work_dir": str(work_dir),
            "lineage": {
                "parent_run_id": parent["run_id"],
                "parent_run_dir": parent["run_dir"],
                "parent_checkpoint": parent["checkpoint_dir"],
                "parent_is_legacy": parent["legacy"],
                "root_run_id": root_run_id,
                "root_run_dir": str(root_run_dir),
                "generation": parent["generation"],
                "ancestors": parent["ancestors"],
            },
            "source": {
                "config_path": str(config_path.resolve()),
                "config_sha256": sha256(config_path.resolve()),
                "parent_config_path": branch.get("resolved_parent_config"),
                "parent_config_sha256": (
                    sha256(Path(str(branch["resolved_parent_config"])))
                    if branch.get("resolved_parent_config")
                    else None
                ),
                "cfg_options": list(cfg_options),
            },
            "action": action,
            "tags": list(named.get("tags") or []),
            "notes": str(named.get("notes") or ""),
            "artifacts": {
                "log": str(work_dir / "logs" / f"{action}.log"),
                "checkpoints": str(work_dir / "checkpoints"),
                "head_screening": str(work_dir / "head_screening"),
                "metrics": str(work_dir / "metrics.json"),
                "evaluation_metrics": str(
                    work_dir / "evaluation" / "metrics.json"
                ),
                "predictions": str(
                    work_dir / "evaluation" / "predictions.jsonl"
                ),
            },
        }
        _atomic_json(work_dir / "run_manifest.json", manifest)
        if parent["legacy"]:
            _index_legacy_parent(experiment_dir, experiment_id, parent)
        event = _index_event(experiment_dir, manifest, "run_prepared", "prepared")
        _append_jsonl(
            work_dir / "events.jsonl",
            work_dir / ".events.lock",
            event,
        )
    elif mode == "resume":
        work_dir = Path(str(named.get("run_dir") or "")).resolve()
        if not _inside(work_dir, experiment_dir):
            raise ValueError("resume run_dir must stay inside the selected experiment")
        manifest_path = work_dir / "run_manifest.json"
        if not manifest_path.is_file():
            raise FileNotFoundError(f"missing named-run manifest: {manifest_path}")
        manifest = _load_manifest(manifest_path)
        if manifest["experiment_id"] != experiment_id:
            raise ValueError("resume experiment_id does not match run manifest")
        run_id = str(manifest["run_id"])
        checkpoint_value = named.get("resume_checkpoint")
        if checkpoint_value in (None, "", "None"):
            checkpoint_value = runner_resume
        resume_checkpoint = _checkpoint(checkpoint_value)
        if resume_checkpoint is None:
            raise ValueError("resume mode requires resume_checkpoint")
        expected_checkpoint_root = work_dir / "checkpoints"
        if not _inside(resume_checkpoint, expected_checkpoint_root):
            raise ValueError(
                "resuming from another run is a new branch: set mode='new' and "
                "use parent_checkpoint instead"
            )
        event = _index_event(experiment_dir, manifest, "run_resumed", "prepared")
        _append_jsonl(
            work_dir / "events.jsonl",
            work_dir / ".events.lock",
            event,
        )
    else:
        raise ValueError("named_run.mode must be 'new' or 'resume'")

    return {
        "run_id": run_id,
        "work_dir": str(work_dir),
        "resume_checkpoint": str(resume_checkpoint) if resume_checkpoint else None,
        "manifest": manifest,
    }


def validate_prepared_run(config: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    named = dict(config.get("named_run") or {})
    if not named:
        return None
    resolved_id = named.get("resolved_run_id")
    if not resolved_id:
        raise RuntimeError(
            "named_run config must be launched through tools/train_named_ddp4.sh"
        )
    work_dir = Path(str(config["work_dir"])).resolve()
    manifest_path = work_dir / "run_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"prepared run manifest is missing: {manifest_path}")
    manifest = _load_manifest(manifest_path)
    if manifest["run_id"] != resolved_id or Path(manifest["work_dir"]) != work_dir:
        raise RuntimeError("resolved named-run identity does not match its manifest")
    resolved_resume = named.get("resolved_resume_checkpoint")
    if resolved_resume in (None, "", "None", "-"):
        expected_resume = None
    else:
        expected_resume = Path(str(resolved_resume)).resolve()
    action = str((config.get("branch") or {}).get("action", "train"))
    mode = str(named.get("mode", "new"))
    if action == "train":
        runner = config.get("runner") or {}
        actual_checkpoint = (
            runner.get("resume_from")
            if mode == "resume"
            else runner.get("initialize_from")
        )
    else:
        actual_checkpoint = named.get("parent_checkpoint")
    actual_checkpoint = (
        None
        if actual_checkpoint in (None, "", "None")
        else Path(str(actual_checkpoint)).resolve()
    )
    if expected_resume != actual_checkpoint:
        field = "resume_from" if mode == "resume" else "initialize_from"
        raise RuntimeError(
            f"runner.{field} does not match named-run lineage checkpoint"
        )
    return manifest


def mark_run_event(
    config: Mapping[str, Any],
    event: str,
    status: str,
    details: Optional[Mapping[str, Any]] = None,
) -> None:
    manifest = validate_prepared_run(config)
    if manifest is None:
        return
    work_dir = Path(manifest["work_dir"])
    experiment_dir = Path(str(manifest["experiment_dir"]))
    manifest["status"] = status
    manifest["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    _atomic_json(work_dir / "run_manifest.json", manifest)
    row = _index_event(experiment_dir, manifest, event, status, details)
    _append_jsonl(work_dir / "events.jsonl", work_dir / ".events.lock", row)


def latest_index_rows(experiment_dir: Path) -> Dict[str, Dict[str, Any]]:
    path = Path(experiment_dir) / "run_index.jsonl"
    latest: Dict[str, Dict[str, Any]] = {}
    if not path.is_file():
        return latest
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            latest[str(row["run_id"])] = row
    return latest
