"""Append-only configuration and prompt evidence shared by execution workers."""
import hashlib
import json
import subprocess
from pathlib import Path
from uuid import uuid4


def _json(value):
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"snapshot cannot serialize {type(value).__name__}")


def save_snapshot(config, config_path, action):
    """Create a new snapshot on every invocation, including resume."""
    payload = json.dumps(dict(config), ensure_ascii=False, indent=2, default=_json)
    directory = Path(config["work_dir"]) / "logs" / "config_snapshots" / f"{action}-{uuid4().hex}"
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "resolved.json").write_text(payload + "\n", encoding="utf-8")
    sources = {}
    for index, (path, content) in enumerate(getattr(config, "source_files", {}).items()):
        name = f"{index:02d}-{Path(path).name}"
        (directory / name).write_text(content, encoding="utf-8")
        sources[name] = {"path": path, "sha256": hashlib.sha256(content.encode()).hexdigest()}
    repository = Path(__file__).resolve().parents[1]
    git = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repository,
                         capture_output=True, text=True)
    hashes = {}
    for folder in ("iploc_szy", "tools"):
        for path in sorted((repository / folder).rglob("*.py")):
            hashes[str(path.relative_to(repository))] = hashlib.sha256(path.read_bytes()).hexdigest()
    (directory / "prompt_implementation.py").write_bytes(
        (repository / "iploc_szy/prompting/messages.py").read_bytes())
    metadata = {"entry_config": str(Path(config_path).resolve()),
                "git_head": git.stdout.strip() if git.returncode == 0 else None,
                "source_configs": sources, "code_sha256": hashes}
    (directory / "provenance.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[CONFIG_SNAPSHOT] {directory}", flush=True)
    return directory


def save_prompt_example(directory, sample):
    """Save constructed conversation without opening referenced images."""
    (directory / "prompt_example.json").write_text(
        json.dumps({"id": sample.get("id"), "messages": sample["messages"]},
                   ensure_ascii=False, indent=2, default=_json) + "\n", encoding="utf-8")
