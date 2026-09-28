"""Compose one branch/action config on top of a selectable parent config."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping

from .config import Config

BRANCH_ACTIONS = ("train", "evaluate", "head_screen", "attention_intervene")
SOURCE_KINDS = ("base_model", "checkpoint")


def _parent_path(config_path: Path, value: Any) -> Path:
    if not value:
        raise ValueError("branch.parent_config is required")
    path = Path(str(value))
    if not path.is_absolute():
        relative_to_template = (config_path.parent / path).resolve()
        relative_to_cwd = path.resolve()
        path = (
            relative_to_template
            if relative_to_template.is_file()
            else relative_to_cwd
        )
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(f"parent config does not exist: {path}")
    return path


def _with_periodic_head_screening(config: Config) -> None:
    if "head_screening" not in config:
        raise ValueError("periodic head screening requires head_screening config")
    runner = dict(config.get("runner") or {})
    hooks = [
        deepcopy(hook)
        for hook in runner.get("hooks", [])
        if hook.get("type") != "HeadScreeningHook"
    ]
    hooks.append(
        {
            "type": "HeadScreeningHook",
            **deepcopy(dict(config["head_screening"])),
        }
    )
    runner["hooks"] = hooks
    config["runner"] = runner


def _apply_source_profile(specification: Config, branch: dict[str, Any]) -> None:
    """Resolve one named parent source into named-run lineage settings."""
    source_name = branch.get("source")
    if source_name in (None, "", "None"):
        return
    profiles = branch.get("source_profiles")
    if not isinstance(profiles, Mapping):
        raise ValueError("branch.source_profiles must be a mapping")
    if source_name not in profiles:
        choices = ", ".join(map(str, profiles))
        raise ValueError(
            f"unknown branch.source {source_name!r}; available profiles: {choices}"
        )
    profile = deepcopy(dict(profiles[source_name]))
    kind = str(profile.pop("kind", "checkpoint"))
    if kind not in SOURCE_KINDS:
        raise ValueError(
            f"branch source kind must be one of {SOURCE_KINDS}, got {kind!r}"
        )
    checkpoint = profile.pop("parent_checkpoint", None)
    if kind == "base_model":
        if checkpoint not in (None, "", "None"):
            raise ValueError("base_model source must not set parent_checkpoint")
        checkpoint = None
        require_checkpoint = False
    else:
        if checkpoint in (None, "", "None"):
            raise ValueError("checkpoint source requires parent_checkpoint")
        require_checkpoint = True

    allowed = {"experiment_id"}
    unknown = set(profile) - allowed
    if unknown:
        raise ValueError(f"unsupported branch source fields: {sorted(unknown)}")
    named = deepcopy(dict(specification.get("named_run") or {}))
    named.update(profile)
    named["parent_checkpoint"] = checkpoint
    named["require_parent_checkpoint"] = require_checkpoint
    specification["named_run"] = named
    branch["resolved_source"] = str(source_name)
    branch["resolved_source_kind"] = kind


def load_experiment_config(
    path: Any,
    options: Iterable[str] = (),
) -> Config:
    """Load a normal config or compose a branch template with its parent.

    Branch-template command-line overrides address the template itself.  Put
    changes to the executable parent config below ``runtime``, for example
    ``runtime.runner.optimizer.lr=1e-5``.
    """
    config_path = Path(path).resolve()
    specification = Config.fromfile(config_path).merge_options(options)
    if "branch" not in specification:
        return specification

    branch = deepcopy(dict(specification["branch"]))
    _apply_source_profile(specification, branch)
    action = str(branch.get("action", "train"))
    if action not in BRANCH_ACTIONS:
        raise ValueError(
            f"branch.action must be one of {BRANCH_ACTIONS}, got {action!r}"
        )
    parent_path = _parent_path(config_path, branch.get("parent_config"))
    parent = Config.fromfile(parent_path)
    runtime = deepcopy(dict(specification.get("runtime") or {}))
    composed = Config(Config._merge(parent, runtime))
    composed.source_files = {**parent.source_files, **specification.source_files}

    branch["action"] = action
    branch["resolved_parent_config"] = str(parent_path)
    branch["nproc_per_node"] = int(branch.get("nproc_per_node", 4))
    if branch["nproc_per_node"] <= 0:
        raise ValueError("branch.nproc_per_node must be positive")
    composed["branch"] = branch
    for section in (
        "named_run",
        "evaluation",
        "head_screening",
        "teacher_precompute",
        "attention_intervention",
    ):
        if section in specification:
            composed[section] = deepcopy(specification[section])
    if "named_run" in composed:
        named = dict(composed["named_run"])
        for field in ("run_name", "run_kind"):
            if field in named:
                named[field] = str(named[field]).replace("{action}", action)
        composed["named_run"] = named

    named = dict(composed.get("named_run") or {})
    if action != "train" and str(named.get("mode", "new")) != "new":
        raise ValueError("evaluate/head_screen actions must use named_run.mode='new'")
    mode = str(named.get("mode", "new"))
    checkpoint = (
        named.get("resume_checkpoint")
        if mode == "resume"
        else named.get("parent_checkpoint")
    )
    if action == "train":
        runner = dict(composed.get("runner") or {})
        runner["initialize_from"] = None
        runner["resume_from"] = None
        if checkpoint not in (None, "", "None"):
            key = "resume_from" if mode == "resume" else "initialize_from"
            runner[key] = checkpoint
        composed["runner"] = runner
        if bool(branch.get("periodic_head_screening", False)):
            _with_periodic_head_screening(composed)
    elif "runner" in composed:
        # Evaluation/screening load adapter weights only.  They must not restore
        # optimizer/scheduler state or accidentally continue training.
        composed["runner"] = {
            **dict(composed["runner"]),
            "resume_from": None,
        }
    return composed


def branch_summary(config: Mapping[str, Any]) -> Mapping[str, Any]:
    branch = dict(config.get("branch") or {})
    return {
        "action": branch.get("action", "train"),
        "nproc_per_node": int(branch.get("nproc_per_node", 4)),
        "parent_config": branch.get("resolved_parent_config"),
        "source": branch.get("resolved_source"),
        "source_kind": branch.get("resolved_source_kind"),
        "periodic_head_screening": bool(
            branch.get("periodic_head_screening", False)
        ),
    }
