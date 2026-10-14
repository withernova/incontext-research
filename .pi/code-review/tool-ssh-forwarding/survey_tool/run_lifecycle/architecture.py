"""Pure validation for a reusable experiment-package implementation reference."""
import pathlib
import re

SCHEMA = "survey-tool.run-implementation/v1"
FIELDS = {"schema", "package_root", "entrypoint", "config_path", "launcher_path", "reused_modules", "added_modules", "tests"}
PATH_FIELDS = ("package_root", "config_path", "launcher_path")
LIST_FIELDS = ("reused_modules", "added_modules", "tests")


def _safe_relative(value, field):
    text = str(value or "").strip()
    if not text or len(text) > 500 or "\0" in text:
        raise ValueError(f"implementation_ref.{field} 必须是非空的短路径")
    path = pathlib.PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts or text.startswith("~"):
        raise ValueError(f"implementation_ref.{field} 必须是仓库内相对路径")
    if "codespace" in path.parts:
        raise ValueError(f"implementation_ref.{field} 不能使用已下线的 legacy codespace")
    if any(part in {".git", ".survey-tool", ".pi", "__pycache__"} for part in path.parts):
        raise ValueError(f"implementation_ref.{field} 不能写入工具状态或缓存目录")
    if path.parts and path.parts[0] == "tmp":
        raise ValueError(f"implementation_ref.{field} 不能位于 tmp")
    return text


def validate_implementation_ref(value):
    if value is None:
        value = {}
    if not isinstance(value, dict):
        raise ValueError("implementation_ref 必须是对象")
    unknown = set(value) - FIELDS
    if unknown:
        raise ValueError("implementation_ref 包含未声明字段：" + ", ".join(sorted(unknown)))
    out = {"schema": str(value.get("schema") or SCHEMA)}
    if out["schema"] != SCHEMA:
        raise ValueError(f"implementation_ref.schema 必须是 {SCHEMA}")
    for field in PATH_FIELDS:
        raw = str(value.get(field) or "").strip()
        out[field] = _safe_relative(raw, field) if raw else ""
    entrypoint = str(value.get("entrypoint") or "").strip()
    if entrypoint and (len(entrypoint) > 300 or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*(?::[A-Za-z_][A-Za-z0-9_]*)?", entrypoint)):
        raise ValueError("implementation_ref.entrypoint 必须是 Python 模块或 module:function")
    out["entrypoint"] = entrypoint
    if out["launcher_path"] and not out["launcher_path"].endswith(".sh"):
        raise ValueError("implementation_ref.launcher_path 必须是可读 Shell 脚本 (.sh)")
    for field in LIST_FIELDS:
        rows = value.get(field) or []
        if not isinstance(rows, list) or len(rows) > 200:
            raise ValueError(f"implementation_ref.{field} 必须是字符串数组")
        out[field] = [_safe_relative(row, field) for row in rows]
    return out


def remove_legacy_codespace_references(value):
    """Drop retired codespace pointers from an already-persisted Run record."""
    if not isinstance(value, dict):
        return value, []
    cleaned = dict(value); removed = []
    for field in PATH_FIELDS:
        raw = str(cleaned.get(field) or "").strip()
        if raw and "codespace" in pathlib.PurePosixPath(raw).parts:
            cleaned[field] = ""; removed.append(field)
    for field in LIST_FIELDS:
        rows = cleaned.get(field)
        if not isinstance(rows, list):
            continue
        kept=[]
        for row in rows:
            raw=str(row or "").strip()
            if raw and "codespace" in pathlib.PurePosixPath(raw).parts:
                removed.append(field)
            else:
                kept.append(row)
        cleaned[field]=kept
    return cleaned, sorted(set(removed))


def architecture_assessment(value, launcher_content=""):
    ref = validate_implementation_ref(value)
    warnings = []
    runners = [p for p in ref["added_modules"] if re.search(r"(?:^|/)runner_[^/]*\.py$", p)]
    if runners:
        warnings.append("新增了按 Run 命名的 Python runner；优先改为公共包模块、配置和薄 Shell")
    text = str(launcher_content or "")
    if text:
        lines = text.splitlines()
        if len(lines) > 80:
            warnings.append("Shell launcher 超过 80 行，建议把实验逻辑移入公共 Python 包")
        if re.search(r"<<\s*['\"]?PY|python(?:3)?\s+-c\b|^\s*(?:def|class)\s+", text, re.M):
            warnings.append("Shell launcher 含内嵌 Python 或函数定义，应只调用稳定 CLI")
        if re.search(r"register_forward_hook|loss\.backward|torch\.|numpy\.|metric|bootstrap", text, re.I):
            warnings.append("Shell launcher 疑似包含科研计算逻辑，应移入 Hook、Metric 或 Pipeline 模块")
    return {"implementation_ref": ref, "warnings": warnings, "ok": not warnings}
