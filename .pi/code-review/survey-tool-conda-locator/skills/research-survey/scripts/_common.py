"""Shared helpers for paper-acquisition scripts."""
from __future__ import annotations
import os, sys, json, datetime, hashlib, pathlib

def project_root(p: str) -> pathlib.Path:
    root = pathlib.Path(p).resolve()
    if not root.exists():
        sys.exit(f"[err] project root does not exist: {root}")
    return root

def ensure_layout(root: pathlib.Path):
    for sub in ["kernel", "shell/02_search", "shell/03_evidence/papers"]:
        (root / sub).mkdir(parents=True, exist_ok=True)

def search_log(root: pathlib.Path) -> pathlib.Path:
    return root / "shell" / "02_search" / "search_log.md"

def citations_md(root: pathlib.Path) -> pathlib.Path:
    return root / "kernel" / "citations.md"

def papers_dir(root: pathlib.Path) -> pathlib.Path:
    return root / "shell" / "03_evidence" / "papers"

def now_iso() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")

def append_search_log(root, source: str, query: str, hits: list[dict], note: str = ""):
    """Append one search entry. hits: list of {citekey,title,url,year,doi} (may be empty)."""
    ensure_layout(root)
    line = f"\n## {now_iso()} | {source} | query: {query!r}\n"
    if not hits:
        line += f"- hits: 0  {note}\n"
    else:
        line += f"- hits: {len(hits)}  {note}\n"
        for h in hits:
            line += f"  - {h.get('citekey','?')}: {h.get('title','?')[:120]} | {h.get('url','')} | {h.get('year','')} | doi={h.get('doi','')}\n"
    with open(search_log(root), "a", encoding="utf-8") as f:
        f.write(line)

def polite_email(root: pathlib.Path) -> str:
    """Read polite email from context.md or env; else default."""
    env = os.environ.get("RSEARCH_EMAIL")
    if env:
        return env
    ctx = root / "shell" / "00_idea" / "context.md"
    if ctx.exists():
        for ln in ctx.read_text(encoding="utf-8").splitlines():
            if ln.lower().startswith("polite_email:"):
                return ln.split(":", 1)[1].strip()
    return "research-survey@example.com"

def emit(obj: dict):
    """Print JSON to stdout for the agent to parse."""
    print(json.dumps(obj, ensure_ascii=False, indent=2))

def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"

def slug_citekey(title: str, year: str | None, author0: str | None) -> str:
    """Make a tentative citekey like wang2024vlod."""
    import re
    def part(s):
        s = (s or "").lower()
        s = re.sub(r"[^a-z0-9]+", "", s)
        return s
    a = part(author0)[:8] if author0 else "anon"
    y = (year or "0000")[:4]
    t = part(title)[:8] or "untitled"
    return f"{a}{y}{t}"