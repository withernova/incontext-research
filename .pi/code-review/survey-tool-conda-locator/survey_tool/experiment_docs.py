"""Readable derived Experiment pages. Never infer research findings or execution times."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
import re
from urllib.parse import quote

from survey_tool.experiment_catalog import (
    catalog_name, collect_documents, render_catalog, render_navigation,
)


def cell(value):
    """Keep arbitrary registry text inside one Markdown table cell."""
    return str(value if value is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "&#124;").replace("[", "&#91;").replace("]", "&#93;").replace("\r", " ").replace("\n", "<br>")


def prose(value, empty):
    if value is None or value == "" or value == [] or value == {}:
        return empty
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value)
    if isinstance(value, dict):
        return "```json\n" + json.dumps(value, ensure_ascii=False, indent=2) + "\n```"
    return str(value)


def link(label, path):
    return f"[{cell(label)}]({quote(str(path), safe='/')})"


def time_key(value):
    """Normalize explicit offsets; old timezone-free records keep wall-clock order."""
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def recorded_at(record):
    return next((value for value in (record.get("updated"), record.get("created")) if time_key(value) is not None), "")


def snapshot_time(exp, runs):
    values = [recorded_at(row) for row in [exp, *runs]]
    valid = [value for value in values if time_key(value) is not None]
    return max(valid, key=time_key) if valid else "未登记"


def ordered_runs(runs):
    # Missing/invalid timestamps come last, not at an invented historical date.
    return sorted(runs, key=lambda row: (time_key(row.get("created")) is None,
                  time_key(row.get("created")) or datetime.max, str(row.get("id", ""))))


def run_link(run):
    path = "runs/"
    if run.get("group_id"):
        path += str(run["group_id"]) + "/"
    return link(run.get("id", ""), path + str(run.get("id", "")) + ".md")


def render_experiment_index(exp, runs, directory, free_notes="", available_documents=(), catalog=None):
    """One entry point, with current summary, recorded chronology and local navigation."""
    catalog = collect_documents(directory, exp["id"]) if catalog is None else catalog
    counts = Counter(str(run.get("status") or "未登记") for run in runs)
    lines = ["---", "survey_tool_generated: true", "type: experiment-index", "---",
             f'# {exp["id"]} · {exp.get("title", "")}', "",
             "> 本页是生成的阅读入口，不是实时监控，也不授予执行权限。",
             f'> 记录截至：{snapshot_time(exp, runs)}；登记时间不等于实际运行时间。', "",
             "## 先读这一页", "", "### 研究什么", exp.get("objective") or "（目标尚未登记）", "",
             "### 已有结论", exp.get("result_summary") or "（Experiment 级结果摘要尚未登记；请查结果页和专题文档，不代表没有实验结果。）", "",
             "### 还缺什么", prose(exp.get("open_questions"), "（开放问题尚未登记；不表示问题已全部解决。）"), "",
             "### 当前记录", f'- 状态：{exp.get("status") or "未登记"}；阶段：{exp.get("workflow_stage") or "未登记"}',
             f'- Run：{len(runs)}；' + ("、".join(f"{status} {n}" for status, n in sorted(counts.items())) or "尚无登记"),
             f'- 结论限制：{exp.get("limitations") or "尚未登记"}', "",
             *render_navigation(catalog, exp["id"]),
             "## 按问题找文档", "", "| 想了解什么 | 文档 |", "|---|---|"]
    for question, filename, label in (
        ("用户最初要求什么", "brief.md", "原始目标"),
        ("为什么做、如何比较", "plan.md", "实验方案"),
        ("有哪些结果、证据和结论边界", "result.md", "结果与审计"),
        ("何时改了什么、为什么改", "events.md", "事件时间线"),
        ("有哪些审核意见", "review.md", "审核记录"),
        ("Agent 应遵守什么操作规则", "mission.md", "Agent 操作规则"),
    ):
        target = link(label, filename) if filename in available_documents or (directory / filename).is_file() else f"{label}（文件缺失）"
        lines.append(f"| {question} | {target} |")
    lines.extend(["", "## Run 登记时间线", "",
                  "> 按创建记录时间从早到晚；未知时间置后。带时区的记录按 UTC 排序；旧记录无时区时仅按原始钟面时间排列，不推断时区。完整操作历史见事件时间线。",
                  "", "| 创建记录时间 | Run / 本轮名称 | 当前状态 | 最近记录更新 |", "|---|---|---|---|"])
    for run in ordered_runs(runs):
        lines.append(f'| {cell(run.get("created") or "未登记")} | {run_link(run)} · {cell(run.get("variant", ""))} | {cell(run.get("status") or "未登记")}{"（已归档）" if run.get("archived_at") else ""} | {cell(run.get("updated") or "未登记")} |')
    if not runs:
        lines.append("| — | 尚无登记 Run | — | — |")
    lines.extend(["", "## 自由笔记（Obsidian）", "", free_notes or "本节可手写阅读提示；工具更新会保留本节。", ""])
    return "\n".join(str(line) for line in lines)


def refresh_experiment_docs(root, experiment_id, dry_run=False):
    """Explicit, scoped refresh. Preview does not create directories or lock files."""
    import server

    def render():
        data = server.experiment_data(root)
        exp = next((row for row in data["experiments"] if row.get("id") == experiment_id), None)
        if exp is None:
            raise ValueError(f"Experiment 不存在：{experiment_id}")
        runs = [row for row in data["runs"] if row.get("experiment_id") == experiment_id]
        from survey_tool.experiment_document_api import require_directory
        directory = require_directory(root, experiment_id)
        catalog = collect_documents(directory, experiment_id)
        check_catalog_target(directory, experiment_id)
        pages = {str((directory / catalog_name(experiment_id)).relative_to(root)):
                 render_catalog(experiment_id, catalog, available_documents=("result.md",))}
        for filename, heading in ((f"{experiment_id}.md", "自由笔记（Obsidian）"), ("result.md", "详细审计正文（canonical）")):
            target = directory / filename
            old = target.read_text(encoding="utf-8") if target.exists() else ""
            section = re.search(r"^## " + re.escape(heading) + r"\n(.*)\Z", old, re.M | re.S)
            preserved = section.group(1).strip() if section else ""
            text = render_experiment_index(exp, runs, directory, preserved, available_documents=("result.md",), catalog=catalog) if filename != "result.md" else render_experiment_result(exp, runs, preserved)
            pages[str(target.relative_to(root))] = text
        return pages

    if dry_run:
        return {"experiment_id": experiment_id, "writes": False, "pages": render()}
    with server.tool_state_transaction(root):
        pages = render()
        for relative, text in pages.items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
    return {"experiment_id": experiment_id, "writes": True, "paths": list(pages)}


def check_catalog_target(directory, experiment_id):
    """Never replace an unrelated existing note or follow a catalogue symlink."""
    target = directory / catalog_name(experiment_id)
    if directory.is_symlink():
        raise ValueError(f"实验目录是符号链接，拒绝写入文档目录：{directory.name}")
    if target.is_symlink():
        raise ValueError(f"文档目录目标是符号链接，拒绝覆盖：{target.name}")
    if target.exists():
        if not target.is_file():
            raise ValueError(f"文档目录目标不是普通文件，拒绝覆盖：{target.name}")
        with target.open("rb") as handle:
            header = handle.read(512).decode("utf-8", errors="replace")
        if not header.startswith("---\nsurvey_tool_generated: true\ntype: experiment-document-catalog\n"):
            raise ValueError(f"文档目录同名文件不是工具生成页，拒绝覆盖：{target.name}")


def save_experiment_index(directory, exp, runs):
    """Refresh the generated address/catalogue pages; preserve entry human notes."""
    catalog = collect_documents(directory, exp["id"])
    try:
        check_catalog_target(directory, exp["id"])
    except (ValueError, OSError) as exc:
        # Optional navigation must not fail a persisted Run/Experiment update.
        catalog["blocked"] = True
        catalog["warnings"].append(str(exc))
    target = directory / f'{exp["id"]}.md'
    old = target.read_text(encoding="utf-8") if target.exists() else ""
    notes = re.search(r"^## 自由笔记（Obsidian）\n(.*)\Z", old, re.M | re.S)
    target.write_text(render_experiment_index(exp, runs, directory, notes.group(1).strip() if notes else "", catalog=catalog), encoding="utf-8")
    if not catalog.get("blocked"):
        (directory / catalog_name(exp["id"])).write_text(render_catalog(exp["id"], catalog), encoding="utf-8")


def render_experiment_result(exp, runs, detailed):
    definitions = {row.get("id"): row for row in exp.get("metric_definitions", [])}
    lines = [f'# {exp["id"]} · 实验结果', "",
             f'> 记录截至：{snapshot_time(exp, runs)}。记录更新不等于实际运行完成；程序完成也不等于科研结论成立。', "",
             "## 结果摘要（survey-tool 管理）", exp.get("result_summary") or "（Experiment 级摘要待登记；以下保留已登记 Run 的结果。）", "",
             "## 对 Claims 的影响（survey-tool 管理）", exp.get("claim_verdict") or "（待人工判断；不会自动提升 Claim）", "",
             "## 局限性（survey-tool 管理）", exp.get("limitations") or "（待补充）", "",
             "## 运行汇总（survey-tool 管理）", ""]
    groups = exp.get("run_groups", [])
    known = {group.get("id") for group in groups}
    grouped = [(group, [run for run in runs if run.get("group_id") == group.get("id")]) for group in groups]
    ungrouped = [run for run in runs if run.get("group_id") not in known]
    if ungrouped:
        grouped.append(({"id": "legacy", "name": "历史未分组"}, ungrouped))
    for group, items in grouped:
        if not items:
            continue
        lines.extend([f'### {group.get("name", group.get("id"))} (`{group.get("id")}`)', "",
                      "| Run / 名称 | Seed | 当前状态 | 最近记录更新 | 已登记数值 |", "|---|---|---|---|---|"])
        for run in ordered_runs(items):
            summaries = []
            for field, label in (("key_results", "关键结果"), ("metric_observations", "指标观测")):
                for obs in run.get(field) or []:
                    definition = definitions.get(obs.get("metric_id"), {})
                    summaries.append(f'{label}：{definition.get("name", obs.get("metric_id", ""))}={obs.get("value", "")} {definition.get("unit", "")}')
            lines.append(f'| {run_link(run)} · {cell(run.get("variant", ""))} | {cell(run.get("seed", ""))} | {cell(run.get("status", ""))}{"（已归档）" if run.get("archived_at") else ""} | {cell(run.get("updated") or "未登记")} | {cell("；".join(summaries) or "尚无已登记数值；不表示没有产物")} |')
        lines.append("")
    if not runs:
        lines.extend(["（尚无 Run）", ""])
    lines.extend(["## 指标观测（survey-tool 管理）", "",
                  "> 关键结果与指标观测分别保留，不混合计算。辅助指标不自动成为主指标；结论仍需人工判断。", ""])
    for run in ordered_runs(runs):
        rows = (run.get("key_results") or []) + (run.get("metric_observations") or [])
        analysis = run.get("result_analysis") or run.get("result_summary")
        if not rows and not analysis:
            continue
        lines.extend([f'<details><summary>{cell(run.get("id"))} · 结果、来源与解释</summary>', "",
                      f'- Run 笔记：{run_link(run)}', f'- 最近记录更新：{run.get("updated") or "未登记"}', ""])
        for field, label in (("key_results", "关键结果"), ("metric_observations", "指标观测")):
            for obs in run.get(field) or []:
                definition = definitions.get(obs.get("metric_id"), {})
                lines.extend([f'### {label} · {definition.get("name", obs.get("metric_id", ""))}',
                              f'- 值：{obs.get("value", "")} {definition.get("unit", "")}',
                              f'- 指标含义：{definition.get("meaning") or "未登记"}'])
                for key, name in (("comparison", "比较对象"), ("delta", "差值"), ("sample_count", "样本数")):
                    if obs.get(key) is not None and obs.get(key) != "":
                        lines.append(f'- {name}：{obs[key]}')
                lines.extend([f'- 不确定性：{obs.get("uncertainty") or "未记录"}',
                              f'- 来源/产物：{obs.get("provenance") or obs.get("artifact") or "未记录"}',
                              f'- 本轮解释：{obs.get("interpretation") or "待解释"}', ""])
        if analysis:
            lines.extend(["### 本轮分析", str(analysis), ""])
        if run.get("limitations"):
            lines.extend(["### 本轮局限", str(run["limitations"]), ""])
        lines.extend(["</details>", ""])
    if not any(run.get("key_results") or run.get("metric_observations") or run.get("result_analysis") or run.get("result_summary") for run in runs):
        lines.extend(["（尚无已登记数值或 Run 结果解释；可继续查 Run 产物与专题文档。）", ""])
    lines.extend(["## 详细审计正文（canonical）", detailed or "这里保存指标定义、证据链、逐层结论边界与审核入口；后续 Run 更新不会覆盖本节。", ""])
    return "\n".join(lines)
