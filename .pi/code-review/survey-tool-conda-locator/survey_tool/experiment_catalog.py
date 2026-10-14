"""Bounded, local-only document discovery for Obsidian Experiment navigation."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import PurePosixPath
import posixpath
import re
from urllib.parse import quote

CORE_DOCUMENTS = {
    "brief.md": "原始目标", "plan.md": "实验方案", "result.md": "结果与审计",
    "events.md": "事件时间线", "review.md": "审核意见", "mission.md": "Agent 操作规则",
}
STATUS_LABELS = {"current": "当前版本（显式标记）", "superseded": "已被替代", "draft": "草稿", "archived": "已归档"}
EXCLUDED_DIRS = {"__pycache__", "node_modules", "codespace", "research_tmp", "venv", "dataset", "datasets", "checkpoints"}
MAX_ENTRIES = 10000
MAX_DOCUMENTS = 1000
MAX_DEPTH = 8
HEADER_BYTES = 16384
RECENT_LIMIT = 10


def catalog_name(experiment_id):
    return f"{experiment_id}-documents.md"


def _cell(value):
    return str(value or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "&#124;").replace("[", "&#91;").replace("]", "&#93;").replace("\r", " ").replace("\n", " ")


def document_link(document):
    return f'[{_cell(document["title"])}]({quote(document["path"], safe="/")})'


def _scalar(value):
    """Read only flat optional YAML strings; do not pretend to parse general YAML."""
    value = value.strip()
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, str) else ""
        except ValueError:
            return ""
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    if value.startswith(("|", ">", "[", "{", "&", "*", "!")):
        return ""
    return value.split(" #", 1)[0].strip()


def _header(path):
    with path.open("rb") as handle:
        text = handle.read(HEADER_BYTES).decode("utf-8-sig", errors="replace")
    lines = text.splitlines()
    metadata = {}
    start = 0
    if lines and lines[0] == "---":
        end = next((i for i in range(1, len(lines)) if lines[i] == "---"), None)
        if end is not None:
            for line in lines[1:end]:
                match = re.fullmatch(r"(title|doc_topic|doc_status|superseded_by|survey_tool_generated):\s*(.*)", line)
                if match:
                    metadata[match[1]] = _scalar(match[2])
            start = end + 1
    heading = next((line[2:].strip() for line in lines[start:] if line.startswith("# ")), "")
    return metadata, metadata.get("title") or heading or path.stem


def collect_documents(directory, experiment_id):
    """Scan Markdown headers, never follow links or descend into excluded worktrees."""
    documents = []
    warnings = []
    if directory.name != experiment_id:
        return {"documents": documents, "warnings": ["目录名与 Experiment ID 不匹配，拒绝跨实验扫描。"]}
    if not directory.exists():
        return {"documents": documents, "warnings": warnings}
    if directory.is_symlink():
        return {"documents": documents, "warnings": ["实验目录是符号链接，未扫描。"]}
    pending = [(directory, 0)]
    visited = 0
    stop = False
    while pending and not stop:
        folder, depth = pending.pop()
        try:
            with os.scandir(folder) as entries:
                for entry in entries:
                    visited += 1
                    if visited > MAX_ENTRIES:
                        warnings.append(f"达到 {MAX_ENTRIES} 个目录项的扫描上限；目录不完整。")
                        stop = True
                        break
                    if entry.name.startswith(".") or entry.is_symlink():
                        continue
                    path = folder / entry.name
                    if entry.is_dir(follow_symlinks=False):
                        if re.fullmatch(r"E-\d+", entry.name, re.I):
                            warnings.append(f"跳过嵌套 Experiment：{path.relative_to(directory)}；每个 Experiment 必须独立，不收录其文档。")
                            continue
                        if entry.name in EXCLUDED_DIRS or entry.name.startswith("review_worktree"):
                            continue
                        if depth < MAX_DEPTH:
                            pending.append((path, depth + 1))
                        else:
                            warnings.append(f"目录深度超限，未扫描：{path.relative_to(directory)}")
                        continue
                    if not entry.is_file(follow_symlinks=False) or path.suffix.lower() != ".md":
                        continue
                    relative = path.relative_to(directory).as_posix()
                    if relative in {f"{experiment_id}.md", catalog_name(experiment_id)}:
                        continue
                    if len(documents) >= MAX_DOCUMENTS:
                        warnings.append(f"达到 {MAX_DOCUMENTS} 篇 Markdown 的扫描上限；目录不完整。")
                        stop = True
                        break
                    try:
                        metadata, title = _header(path)
                        stat = entry.stat(follow_symlinks=False)
                        modified = datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(timespec="seconds")
                    except (OSError, ValueError, OverflowError) as exc:
                        warnings.append(f"无法读取文档元数据：{relative}（{type(exc).__name__}）")
                        continue
                    kind = "core" if relative in CORE_DOCUMENTS else "run" if relative.startswith("runs/") else "topic"
                    status = metadata.get("doc_status", "")
                    if status and status not in STATUS_LABELS:
                        warnings.append(f"未知 doc_status：{relative}；不推断版本。")
                        status = ""
                    documents.append({"path": relative, "title": CORE_DOCUMENTS.get(relative, title),
                                      "kind": kind, "modified": modified, "mtime_ns": stat.st_mtime_ns,
                                      "generated": kind != "topic" or metadata.get("survey_tool_generated") == "true",
                                      "topic": metadata.get("doc_topic", ""), "status": status,
                                      "superseded_by": metadata.get("superseded_by", "")})
        except OSError as exc:
            warnings.append(f"无法扫描目录：{folder.relative_to(directory)}（{type(exc).__name__}）")
    documents.sort(key=lambda row: row["path"])
    return {"documents": documents, "warnings": warnings}


def recent_documents(catalog):
    # Never let regenerating an index, result table, or Run note dominate "recent".
    return sorted((row for row in catalog["documents"] if not row["generated"]),
                  key=lambda row: (-row["mtime_ns"], row["path"]))[:RECENT_LIMIT]


def render_navigation(catalog, experiment_id):
    target = ("- 文档目录同名文件冲突，未覆盖。请先备份并重命名冲突文件，再刷新索引。" if catalog.get("blocked") else
              f'- [打开 {experiment_id} 全文档目录]({catalog_name(experiment_id)})：按标题、路径和专题查找；包含子目录中的报告。')
    lines = ["## 找文档与最近修改", "", target,
             "> 以下按专题文件修改时间倒序排列，最多 10 篇；不是“当前有效版本”，也不是实际运行时间。文件复制可能改变修改时间。新增或编辑文档后需刷新索引。", "",
             "| 最近修改（UTC） | 专题文档 | 版本标记 |", "|---|---|---|"]
    for row in recent_documents(catalog):
        label = STATUS_LABELS.get(row["status"], "未标记")
        lines.append(f'| {row["modified"]} | {document_link(row)} · <code>{_cell(row["path"])}</code> | {label} |')
    if not recent_documents(catalog):
        lines.append("| — | 尚无可索引的专题文档 | 不推断版本 |")
    if catalog.get("blocked"):
        lines.extend("\n> " + _cell(warning) for warning in catalog["warnings"])
    elif catalog["warnings"]:
        lines.append("\n> 文档扫描有缺口；请查看全文档目录中的扫描提示。")
    return lines + [""]


def _replacement(row, documents):
    target = posixpath.normpath(row["superseded_by"])
    if target in {doc["path"] for doc in documents} and target != row["path"]:
        return f'[替代文档]({quote(target, safe="/")})'
    return "替代目标未找到或无效：" + _cell(row["superseded_by"])


def render_catalog(experiment_id, catalog, available_documents=()):
    documents = catalog["documents"]
    lines = ["---", "survey_tool_generated: true", "type: experiment-document-catalog",
             "aliases: " + json.dumps([f"{experiment_id} 文档目录"], ensure_ascii=False), "---",
             f"# {experiment_id} · 文档目录", "",
             f'- [返回 {experiment_id} 实验入口]({experiment_id}.md)',
             "> 本页是刷新时的文件快照。可在 Obsidian 当前笔记内搜索标题、路径或专题；不是实时索引。", "",
             "## 当前版本（仅按显式标记）", "",
             "> 只有 doc_status: current 的专题文档进入此区。工具不按文件名或修改时间选出“权威版本”。同一专题有多篇 current 时全部保留并提示冲突。", ""]
    current = [row for row in documents if row["kind"] == "topic" and row["status"] == "current"]
    topics = Counter(row["topic"] for row in current if row["topic"])
    for row in current:
        conflict = "；同一专题存在多个当前版本，请核对" if topics[row["topic"]] > 1 else ""
        lines.append(f'- {_cell(row["topic"] or "专题未标记")}：{document_link(row)} · <code>{_cell(row["path"])}</code>{conflict}')
    if not current:
        lines.append("（暂无显式标记的当前版本；请先看最近修改列表，不把它当作有效性判断。）")
    lines.extend(["", *render_navigation(catalog, experiment_id)])
    # The catalogue itself is not linked from its own navigation block.
    lines = [line for line in lines if not line.startswith(f'- [打开 {experiment_id} 全文档目录]')]
    lines.extend(["## 核心文档", "", "| 问题入口 | 文件 |", "|---|---|"])
    existing = {row["path"] for row in documents} | set(available_documents)
    for path, title in CORE_DOCUMENTS.items():
        target = document_link({"path": path, "title": title}) if path in existing else title + "（文件缺失）"
        lines.append(f'| {target} | <code>{path}</code> |')
    lines.extend(["", "## 专题文档（按目录排列）", "",
                  "> 文件标题取自 title 属性或一级标题；路径用于区分同名 report.md。版本标记只用于阅读导航，不代表科研审核或执行授权。", ""])
    topics_docs = [row for row in documents if row["kind"] == "topic"]
    groups = sorted({str(PurePosixPath(row["path"]).parent) for row in topics_docs})
    for group in groups:
        lines.extend([f'### {_cell(group if group != "." else "实验根目录")}', "",
                      "| 文档标题 / 专题 | 精确路径 | 文件修改（UTC） | 版本标记 / 替代入口 |", "|---|---|---|---|"])
        for row in topics_docs:
            if str(PurePosixPath(row["path"]).parent) != group:
                continue
            status = STATUS_LABELS.get(row["status"], "未标记")
            if row["superseded_by"]:
                status += "；" + _replacement(row, documents)
            topic = " · " + _cell(row["topic"]) if row["topic"] else ""
            lines.append(f'| {document_link(row)}{topic} | <code>{_cell(row["path"])}</code> | {row["modified"] if not row["generated"] else "工具生成；不参与最近修改排序"} | {status} |')
        lines.append("")
    if not topics_docs:
        lines.extend(["（暂无专题文档）", ""])
    lines.extend(["## Run 文档（精确路径）", ""])
    run_docs = [row for row in documents if row["kind"] == "run"]
    for row in run_docs:
        lines.append(f'- {document_link(row)} · <code>{_cell(row["path"])}</code>')
    if not run_docs:
        lines.append("（暂无 Run 文档；Run 登记信息见实验入口。）")
    lines.extend(["", "## 扫描范围与提示", "",
                  "- 仅扫描本实验内 Markdown 的标题和少量平面属性；不复制正文，不跟随符号链接。",
                  "- 排除隐藏目录、review_worktree*、research_tmp、codespace、依赖、缓存、数据集和 checkpoints。",
                  f'- 上限：{MAX_DEPTH} 层目录、{MAX_ENTRIES} 个目录项、{MAX_DOCUMENTS} 篇 Markdown；标题/属性只读取前 {HEADER_BYTES} 字节。',
                  "- 未展示的源码或临时资料仍在原位置；扫描结果不代表全部研究资料。",
                  *["- " + _cell(warning) for warning in catalog["warnings"]], ""])
    return "\n".join(lines)
