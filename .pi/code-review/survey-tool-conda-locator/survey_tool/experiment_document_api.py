"""Read-only, experiment-scoped document search and bounded Markdown reading."""
from __future__ import annotations

from pathlib import PurePosixPath
import re

from survey_tool.experiment_catalog import collect_documents

CONTENT_BYTES = 512 * 1024


class ExperimentDirectoryError(ValueError):
    """Registered identity exists, but its independent directory is unavailable."""


def require_directory(root, experiment_id):
    if not re.fullmatch(r"E-\d+", experiment_id):
        raise ValueError("Experiment ID 无效")
    relative = PurePosixPath("shell/06_experiments") / experiment_id
    directory = root
    for part in relative.parts:
        directory = directory / part
        if directory.is_symlink():
            raise ExperimentDirectoryError(f"实验目录路径包含符号链接，拒绝跨边界读取：{relative}")
    if not directory.is_dir():
        raise ExperimentDirectoryError(f"实验独立目录缺失：{relative}；请核对目录位置，不会自动创建或移动目录。")
    return directory


def _registered_directory(root, experiment_id):
    import server
    rows = server.read_tool_json(root, "experiments.json", [])
    if not any(row.get("id") == experiment_id for row in rows):
        raise KeyError("Experiment 不存在")
    return require_directory(root, experiment_id)


def safe_relative(value, allow_empty=False):
    if not isinstance(value, str) or len(value) > 1024:
        raise ValueError("文档路径无效")
    if allow_empty and value in ("", "."):
        return ""
    path = PurePosixPath(value)
    if not value or path.is_absolute() or "\\" in value or ":" in value or "\x00" in value or any(part in {".."} or part.startswith(".") for part in path.parts):
        raise ValueError("只能使用本实验内的相对路径，禁止跨实验路径")
    if any(re.fullmatch(r"E-\d+", part, re.I) for part in path.parts):
        raise ValueError("不能读取嵌套的其他 Experiment")
    return path.as_posix()


def _catalog(root, experiment_id):
    directory = _registered_directory(root, experiment_id)
    return directory, collect_documents(directory, experiment_id)


def list_documents(root, experiment_id, query="", directory="", kind="all", sort="path", status="all"):
    if not isinstance(query, str) or len(query) > 300:
        raise ValueError("检索词最多 300 字符")
    prefix = safe_relative(directory, allow_empty=True)
    if kind not in {"all", "core", "run", "topic"} or sort not in {"path", "modified"} or status not in {"all", "current", "superseded", "draft", "archived", "unmarked"}:
        raise ValueError("无效的文档筛选或排序参数")
    _, catalog = _catalog(root, experiment_id)
    documents = catalog["documents"]
    directories = {""}
    for row in documents:
        parent = PurePosixPath(row["path"]).parent
        while str(parent) != ".":
            directories.add(parent.as_posix())
            parent = parent.parent
    needle = query.strip().casefold()
    matches = [row for row in documents
               if (not prefix or row["path"].startswith(prefix + "/"))
               and (kind == "all" or row["kind"] == kind)
               and (status == "all" or row["status"] == ("" if status == "unmarked" else status))
               and (not needle or any(needle in str(row[key]).casefold() for key in ("title", "path", "topic")))]
    if sort == "modified":
        matches.sort(key=lambda row: (row["generated"], -row["mtime_ns"], row["path"]))
    return {"experiment_id": experiment_id, "read_only": True, "root": f"shell/06_experiments/{experiment_id}",
            "documents": [{key: value for key, value in row.items() if key != "mtime_ns"} for row in matches],
            "directories": sorted(directories), "total": len(matches), "indexed_count": len(documents),
            "warnings": catalog["warnings"], "search_fields": ["title", "path", "topic"],
            "sort": sort, "recency_note": "文件修改时间不等于当前有效版本；最近修改排序将专题文档放在工具生成页之前。"}


def read_document(root, experiment_id, path):
    relative = safe_relative(path)
    directory, catalog = _catalog(root, experiment_id)
    row = next((row for row in catalog["documents"] if row["path"] == relative), None)
    if row is None:
        raise KeyError("文档不存在或不在本实验可检索范围内")
    target = directory
    for part in PurePosixPath(relative).parts:
        target = target / part
        if target.is_symlink():
            raise ValueError("文档路径包含符号链接，拒绝读取")
    with target.open("rb") as handle:
        raw = handle.read(CONTENT_BYTES + 1)
    if len(raw) > CONTENT_BYTES:
        raise ValueError(f"文档超过只读预览上限 {CONTENT_BYTES} 字节，请在 Obsidian 中读取原文件")
    return {"experiment_id": experiment_id, "read_only": True, "path": relative,
            "project_relative_path": f"shell/06_experiments/{experiment_id}/{relative}",
            "title": row["title"], "content": raw.decode("utf-8-sig", errors="replace")}
