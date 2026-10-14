"""Canonical domain extracted from the legacy HTTP server."""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import secrets
import selectors
import shlex
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import uuid
from contextlib import contextmanager

import server
from server import (
    IDEA_KEYS, IMG_EXT, SEVENQ, SEVENQ_OLD, _frontmatter, _replace_section,
    _section, _yaml_scalar, next_object_id, now_iso, tool_dir,
)
from survey_tool.v2.migration import refresh_v2_index

__all__ = [
    "read_state",
    "_title_from_dir",
    "_norm_title",
    "read_papers",
    "_read_index_rows",
    "citekey_for",
    "note_path",
    "parse_note_sections",
    "parse_annot_line",
    "annot_line",
    "_looks_like_latex_math",
    "normalize_imported_markdown_math",
    "write_note_sections",
    "paper_state",
    "save_paper_state",
    "paper_seven_meta",
    "save_paper_seven_meta",
    "update_paper_canonical",
    "read_claims",
    "append_claim",
    "update_claim",
    "_parse_idea_field",
    "_format_idea_field",
    "read_ideas",
    "ideas_path",
    "idea_canonical_hash",
    "append_idea",
    "update_idea",
    "_object_dirs",
    "questions_dir",
    "read_questions",
    "save_question",
    "create_question",
    "ensure_finding_ids",
    "_comparison_path",
    "_finding_path",
    "sync_compares_from_markdown",
    "save_compare_markdown",
    "compares_path",
    "read_compares",
    "_stable_slug",
    "ensure_compare_ids",
    "save_compares",
    "read_citations",
    "_norm",
    "resolve_paper_artifacts",
    "artifacts_for",
    "list_images",
    "mineru_md_for",
    "_mineru_md_for_paper"
]

def read_state(root: pathlib.Path):
    st = root / "state.md"
    info = {"state":"?","iteration":0,"blockers":[],"next_actions":[]}
    if not st.exists(): return info
    txt = st.read_text(encoding="utf-8")
    m = re.search(r"^state:\s*(.+)$", txt, re.M); info["state"]=m.group(1).strip() if m else "?"
    m = re.search(r"^iteration:\s*(\d+)", txt, re.M); info["iteration"]=int(m.group(1)) if m else 0
    m = re.search(r"blockers:\s*(.*)$", txt, re.M)
    if m and m.group(1).strip() not in ("","[]"):
        info["blockers"]=[x.strip() for x in m.group(1).strip("[]").split(",") if x.strip()]
    return info

def _title_from_dir(name):
    # "FOCUS_ Forcing..._2026" -> "FOCUS_ Forcing..." then restore ":" roughly
    t = re.sub(r"_\d{4}$", "", name)
    return t.replace("_ ", ": ", 1) if "_ " in t[:20] else t

def _norm_title(s):
    return re.sub(r"[^a-z0-9]+","", (s or "").lower())

def read_papers(root):
    """Source of truth = papers/ dir. Returns list with has_mineru/has_images/images_count."""
    pdir = root / "papers"
    out = []
    seen_keys = set()
    # 1) subdirs (MinerU-processed papers)
    if pdir.is_dir():
        for d in sorted(pdir.iterdir()):
            if not d.is_dir(): continue
            hybrid = d / "hybrid_auto"
            images_dir = hybrid / "images" if (hybrid/"images").is_dir() else (d/"images")
            has_mineru = (hybrid.is_dir() and any(hybrid.glob("*.md"))) or bool(images_dir.is_dir())
            title = _title_from_dir(d.name)
            ck = citekey_for({"title":title,"date":d.name[-4:] if d.name[-4:].isdigit() else ""})
            pdf = pdir / (d.name + ".pdf")
            if not pdf.exists():  # try matching a .pdf by stem prefix
                cand = [p for p in pdir.glob("*.pdf") if p.stem == d.name]
                if cand: pdf = cand[0]
            entry = {"citekey":ck, "title":title, "date":d.name[-4:] if re.search(r"_\d{4}$", d.name) else "",
                     "venue":"", "link":"", "file":pdf.name if pdf.exists() else "",
                     "has_pdf":pdf.exists(), "has_mineru":has_mineru,
                     "has_images":images_dir.is_dir(),
                     "images_count":len([p for p in images_dir.iterdir() if p.suffix.lower() in IMG_EXT]) if images_dir.is_dir() else 0,
                     "dir":str(d)}
            out.append(entry); seen_keys.add(_norm_title(title))
    # 2) loose PDFs without a matching subdir (no MinerU)
    if pdir.is_dir():
        for p in sorted(pdir.glob("*.pdf")):
            stem = p.stem
            if any(_norm_title(_title_from_dir(d.name))==_norm_title(stem) for d in [x for x in pdir.iterdir() if x.is_dir()]):
                continue  # already covered by its subdir
            title = _title_from_dir(stem)
            if _norm_title(title) in seen_keys: continue
            date = stem[-4:] if re.search(r"_\d{4}$", stem) else ""
            out.append({"citekey":citekey_for({"title":title,"date":date}), "title":title, "date":date,
                        "venue":"", "link":"", "file":p.name, "has_pdf":True,
                        "has_mineru":False, "has_images":False, "images_count":0, "dir":""})
            seen_keys.add(_norm_title(title))
    # 3) INDEX rows with no local file (e.g. PromptHub ⚠️ no PDF) so user knows to fetch
    for row in _read_index_rows(root):
        if _norm_title(row["title"]) in seen_keys: continue
        if not row["has_pdf"]:
            out.append({**row, "citekey":citekey_for(row), "has_mineru":False, "has_images":False, "images_count":0, "dir":""})
            seen_keys.add(_norm_title(row["title"]))
    # Ingested citation identities take precedence over filename-derived keys.
    # Require a unique path or title/year match; never guess between collisions.
    citations = list(read_citations(root).values())
    for paper in out:
        pdf = (root / "papers" / paper["file"]).resolve() if paper.get("file") else None
        matches = []
        if pdf:
            matches = [citation for citation in citations if citation.get("local_pdf")
                       and (root / citation["local_pdf"]).resolve() == pdf]
        if not matches:
            matches = [citation for citation in citations
                       if citation.get("title") and citation["title"] != "[UNVERIFIED]"
                       and _norm_title(paper["title"])
                       and _norm_title(citation["title"]) == _norm_title(paper["title"])
                       and (not citation.get("year") or not paper.get("date") or citation["year"] == paper["date"])]
        if len(matches) == 1:
            citation = matches[0]
            paper["citekey"] = citation["citekey"]
            for source, target in (("title", "title"), ("year", "date"), ("doi", "doi"), ("source_url", "link")):
                if citation.get(source) and citation[source] != "[UNVERIFIED]": paper[target] = citation[source]
    return out

def _read_index_rows(root):
    """Parse INDEX.md into rows (used only for metadata + no-PDF items)."""
    idx = root / "papers" / "INDEX.md"
    if not idx.exists(): return []
    txt = idx.read_text(encoding="utf-8")
    rows = []
    for m in re.finditer(r"^\|\s*(\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|", txt, re.M):
        num,title,date,venue,link,file = m.groups()
        if title.lower()=="title": continue
        has_pdf = "⚠️" not in file
        rows.append({"num":int(num),"title":title.strip(),"date":date.strip(),
                     "venue":venue.strip(),"link":link.strip(),"file":file.strip().strip("`"),
                     "has_pdf":has_pdf})
    return rows

def citekey_for(row):
    t = re.sub(r"[^a-z0-9]+","", (row.get("title") or "").lower())[:10] or "paper"
    y = (re.search(r"(20\d\d|19\d\d)", row.get("date") or "") or ["",""])[1]
    return f"{t[:8]}{y}"

def note_path(root: pathlib.Path, citekey: str):
    citekey = str(citekey or "")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", citekey) or ".." in citekey:
        raise ValueError("invalid paper citekey")
    # find existing note matching citekey (either <citekey>.md or a paper folder note)
    pd = root / "shell" / "03_evidence" / "papers"
    direct = pd / f"{citekey}.md"
    if direct.exists(): return direct
    # fallback: any .md whose header references the citekey
    for md in pd.glob("*.md"):
        try:
            if f"[[{citekey}]]" in md.read_text(encoding="utf-8")[:200]:
                return md
        except Exception: pass
    return direct  # may not exist yet

def parse_note_sections(md_text: str):
    """Read seven-question notes, migrating legacy labels in memory.

    Migration is semantic rather than positional: old assumptions + counterexamples
    become the new boundary question, while the new method-flow question starts empty.
    The source file is only rewritten when the user explicitly saves.
    """
    seven = {q:"" for q in SEVENQ}
    annots = []
    m = re.search(r"## 七问细读（survey-tool 管理）\n(.*?)(?=\n## |\Z)", md_text, re.S)
    if m:
        body = m.group(1)
        def section(q):
            mm = re.search(rf"### {re.escape(q)}\n(.*?)(?=\n### |\Z)", body, re.S)
            return mm.group(1).strip() if mm else ""
        # Q1 has the same label in v1/v2, so detect v2 using changed Q2-Q7 labels.
        for q in SEVENQ:
            seven[q] = section(q)
        has_v2_sections = any(section(q) for q in SEVENQ[1:])
        if not has_v2_sections:
            old = [section(q) for q in SEVENQ_OLD]
            seven[SEVENQ[0]] = old[0]
            seven[SEVENQ[1]] = ""
            seven[SEVENQ[2]] = old[2]
            seven[SEVENQ[3]] = old[3]
            boundary=[]
            if old[1]: boundary.append("#### 成立前提\n"+old[1])
            if old[4]: boundary.append("#### 反例与失效边界\n"+old[4])
            seven[SEVENQ[4]] = "\n\n".join(boundary)
            seven[SEVENQ[5]] = old[5]
            seven[SEVENQ[6]] = old[6]
    m = re.search(r"## 图片标注（survey-tool 管理）\n(.*?)(?=\n## |\Z)", md_text, re.S)
    if m:
        for line in m.group(1).splitlines():
            line=line.strip()
            if not line.startswith("- "): continue
            annots.append(parse_annot_line(line[2:]))
    return seven, annots

def parse_annot_line(s: str):
    # - [[citekey]] Fig.x | src: images/xx.png | boxes: [[...],...] | note: ...
    d = {"raw": s}
    cm = re.match(r"\[\[([^\]]+)\]\]\s*(Fig\.\S+)?", s)
    d["citekey"] = cm.group(1) if cm else ""
    d["fig"] = cm.group(2) if cm else ""
    for k in ("src","note"):
        mm = re.search(rf"\|\s*{k}:\s*(.*?)\s*(?:\||$)", s)
        d[k] = mm.group(1).strip() if mm else ""
    bm = re.search(r"boxes:\s*(\[\[.*?\]\])", s)
    d["boxes"] = json.loads(bm.group(1)) if bm else []
    return d

def annot_line(d: dict) -> str:
    boxes = json.dumps(d.get("boxes",[]), ensure_ascii=False)
    return (f"- [[{d.get('citekey','')}]] {d.get('fig','') or ''} | src: {d.get('src','')} "
            f"| boxes: {boxes} | note: {d.get('note','')}")

def _looks_like_latex_math(body: str) -> bool:
    """Conservative signal for a bracketed block that lost its LaTeX delimiters."""
    value=str(body or "").strip()
    if not value or "\n#" in value: return False
    signals=[
        r"\\(?:begin|end)\{(?:cases|aligned|align|array|matrix|pmatrix|bmatrix|equation)\}",
        r"\\(?:mathrm|mathbf|mathcal|mathbb|langle|rangle|theta|delta|ell|varnothing|frac|sum|prod|mid|left|right)\b",
        r"(?:^|[^\\])[_^]\s*(?:\{|[A-Za-z0-9])",
    ]
    return any(re.search(pattern,value) for pattern in signals)

def normalize_imported_markdown_math(text: str) -> str:
    """Repair display math written as plain `[`/`]` lines by AI importers.

    Only math-looking blocks outside fenced code are changed. Ordinary brackets,
    Markdown links, and prose are deliberately left untouched.
    """
    source=str(text or "")
    parts=re.split(r"(```[\s\S]*?```)",source)
    bracket_block=re.compile(r"(?m)^[ \t]*\[[ \t]*$\n([\s\S]*?)\n^[ \t]*\][ \t]*$")
    for i in range(0,len(parts),2):
        parts[i]=bracket_block.sub(lambda m: "$$\n"+m.group(1).strip()+"\n$$" if _looks_like_latex_math(m.group(1)) else m.group(0),parts[i])
    return "".join(parts)

def write_note_sections(root: pathlib.Path, citekey: str, seven: dict, annots: list):
    p = note_path(root, citekey)
    if not p.exists():
        p.write_text(f"# [[{citekey}]] — (待补)\n\n> source: \n\n", encoding="utf-8")
    txt = p.read_text(encoding="utf-8")
    # strip old managed sections
    txt = re.sub(r"\n*## 七问细读（survey-tool 管理）\n.*?(?=\n## |\Z)", "", txt, flags=re.S)
    txt = re.sub(r"\n*## 图片标注（survey-tool 管理）\n.*?(?=\n## |\Z)", "", txt, flags=re.S)
    txt = txt.rstrip() + "\n\n"
    seven_block = "## 七问细读（survey-tool 管理）\n"
    for q in SEVENQ:
        v = normalize_imported_markdown_math(seven.get(q) or "").strip()
        seven_block += f"### {q}\n{v}\n\n" if v else f"### {q}\n\n\n"
    annot_block = "## 图片标注（survey-tool 管理）\n"
    for a in annots:
        annot_block += annot_line(a) + "\n"
    txt = txt + seven_block + "\n" + annot_block
    p.write_text(txt, encoding="utf-8")
    return p

def paper_state(root: pathlib.Path, citekey: str):
    f = tool_dir(root) / "papers" / f"{citekey}.json"
    if f.exists():
        try: return json.loads(f.read_text(encoding="utf-8"))
        except Exception: pass
    return {"triage":"deep","github_repo":"","github_status":"unscanned","clone_dir":"","claims":[]}

def save_paper_state(root: pathlib.Path, citekey: str, st: dict):
    f = tool_dir(root) / "papers" / f"{citekey}.json"
    f.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")
    return st

def paper_seven_meta(root: pathlib.Path, citekey: str):
    """UI-only per-question metadata; intentionally outside canonical notes."""
    st=paper_state(root, citekey)
    return st.get("seven_meta",{}) if isinstance(st.get("seven_meta",{}),dict) else {}

def save_paper_seven_meta(root: pathlib.Path, citekey: str, seven: dict):
    st=paper_state(root, citekey)
    meta=dict(st.get("seven_meta",{}) or {})
    for k,v in seven.items():
        if k.startswith("_"): meta[k]=v
    st["seven_meta"]=meta
    save_paper_state(root, citekey, st)
    return meta

def update_paper_canonical(root: pathlib.Path, citekey: str, payload: dict):
    """Apply the legacy-compatible Paper merge rules to canonical authority."""
    if "seven" in payload or "annotations" in payload:
        p=note_path(root,citekey)
        cur_seven,cur_annots=parse_note_sections(p.read_text(encoding="utf-8") if p.exists() else "")
        seven=payload.get("seven",cur_seven); annots=payload.get("annotations",cur_annots)
        write_note_sections(root,citekey,seven,annots)
    else:
        seven={}
    previous=paper_state(root,citekey)
    st=payload.get("state")
    if st:
        merged=dict(st)
        if previous.get("seven_meta"): merged["seven_meta"]=previous["seven_meta"]
        save_paper_state(root,citekey,merged)
    save_paper_seven_meta(root,citekey,seven)

def read_claims(root: pathlib.Path):
    cm = root / "kernel" / "claims.md"
    if not cm.exists(): return []
    txt = cm.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"^## (C\d+)\n((?:(?!^## ).+|\n)+)", txt, re.M|re.S):
        cid = m.group(1); body = m.group(2)
        c = {"id":cid}
        for k in ["text","status","confidence","sources","contradicting_evidence",
                  "r2_verdict","human_verdict","created","rationale","citekey",
                  "source_type","source_ref"]:
            mm = re.search(rf"^- {k}:\s*(.*)$", body, re.M)
            c[k] = mm.group(1).strip() if mm else ""
        out.append(c)
    return out

def append_claim(root: pathlib.Path, text, sources="", rationale="", citekey="", source_type="manual", source_ref=""):
    cm = root / "kernel" / "claims.md"
    if not cm.exists():
        cm.write_text("# 声明注册表（Claims registry，kernel 真相层）\n\n", encoding="utf-8")
    txt = cm.read_text(encoding="utf-8")
    ids = [int(x) for x in re.findall(r"^## C(\d+)", txt, re.M)]
    cid = f"C{(max(ids)+1) if ids else 1:02d}"
    block = (f"\n## {cid}\n- text: {text}\n- status: draft\n- confidence: \n"
             f"- sources: {sources}\n- contradicting_evidence: \n"
             f"- r2_verdict: pending\n- human_verdict: pending\n"
             f"- citekey: {citekey}\n- source_type: {source_type}\n- source_ref: {source_ref}\n"
             f"- created: {now_iso()}\n- rationale: {rationale}\n")
    cm.write_text(txt.rstrip()+"\n"+block, encoding="utf-8")
    return cid

def update_claim(root, cid, fields):
    cm = root / "kernel" / "claims.md"
    txt = cm.read_text(encoding="utf-8")
    def repl(m):
        body = m.group(2)
        for k,v in fields.items():
            body = re.sub(rf"^- {k}:.*$", f"- {k}: {v}", body, count=1, flags=re.M)
            if f"- {k}:" not in body:
                body = body.rstrip()+"\n"+f"- {k}: {v}\n"
        return f"## {cid}\n{body}"
    new = re.sub(rf"^## {re.escape(cid)}\n((?:(?!^## ).+|\n)+)", repl, txt, count=1, flags=re.M|re.S)
    cm.write_text(new, encoding="utf-8")

def _parse_idea_field(body, k):
    # Multi-line: - key: |\n  line1\n  line2
    mm = re.search(rf"^- {k}:[ \t]*\|[ \t]*\n((?:^[ \t]+.*\n?)+)", body, re.M)
    if mm:
        return "\n".join(l.strip() for l in mm.group(1).splitlines()).strip()
    # Single-line: [ \t]* prevents matching across newlines (unlike \s*)
    mm = re.search(rf"^- {k}:[ \t]*(.*)$", body, re.M)
    return mm.group(1).strip() if mm else ""

def _format_idea_field(k, v):
    v = str(v or "")
    if "\n" in v:
        return f"- {k}: |\n" + "\n".join(f"  {l}" for l in v.split("\n"))
    return f"- {k}: {v}"

def ideas_path(root: pathlib.Path):
    return root / "shell" / "00_idea" / "idea.md"

def idea_canonical_hash(root: pathlib.Path):
    im=ideas_path(root); text=im.read_text(encoding="utf-8") if im.exists() else ""
    return "sha256:"+hashlib.sha256(text.encode()).hexdigest()

def read_ideas(root: pathlib.Path):
    im = ideas_path(root)
    if not im.exists(): return []
    txt = im.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"^## (I-\d+)\n(.*?)(?=\n^## |\Z)", txt, re.M|re.S):
        iid = m.group(1); body = m.group(2)
        d = {"id":iid}
        for k in IDEA_KEYS:
            d[k] = _parse_idea_field(body, k)
        d["_canonical_rev"]="sha256:"+hashlib.sha256(txt.encode()).hexdigest()
        out.append(d)
    return out

def append_idea(root, fields):
    im = ideas_path(root)
    im.parent.mkdir(parents=True, exist_ok=True)
    if not im.exists():
        im.write_text("# 想法（Idea）\n\n", encoding="utf-8")
    txt = im.read_text(encoding="utf-8")
    ids = [int(x) for x in re.findall(r"^## I-(\d+)", txt, re.M)]
    iid = f"I-{(max(ids)+1) if ids else 1:02d}"
    iso = now_iso()
    fields.setdefault("status","draft"); fields.setdefault("novelty","unknown")
    fields.setdefault("created",iso); fields["updated"]=iso
    block = f"\n## {iid}\n" + "\n".join(_format_idea_field(k, fields.get(k,'')) for k in IDEA_KEYS if fields.get(k)!="") + "\n"
    im.write_text(txt.rstrip()+"\n"+block, encoding="utf-8")
    return iid

def update_idea(root, iid, fields):
    im = ideas_path(root)
    txt = im.read_text(encoding="utf-8")
    fields["updated"]=now_iso()
    def repl(m):
        body = m.group(1)
        for k,v in fields.items():
            # Remove old field: first multi-line block (| + indented lines), then single-line
            body = re.sub(rf"^- {k}:\s*\|\s*\n(?:^[ \t]+.*\n?)*", "", body, flags=re.M)
            body = re.sub(rf"^- {k}:.*$", "", body, count=1, flags=re.M)
            # Always append new value at end of block
            body = body.rstrip()+"\n"+_format_idea_field(k, v)+"\n"
        return f"## {iid}\n{body}"
    new = re.sub(rf"^## {re.escape(iid)}\n(.*?)(?=\n^## |\Z)", repl, txt, count=1, flags=re.M|re.S)
    im.write_text(new, encoding="utf-8")

def _object_dirs(root):
    paths=[root/"shell"/"01_questions",root/"shell"/"04_comparisons",root/"shell"/"04_comparisons"/"findings",root/"index"]
    for p in paths: p.mkdir(parents=True,exist_ok=True)
    return paths

def questions_dir(root): return _object_dirs(root)[0]

def read_questions(root):
    rows=[]
    for p in sorted(questions_dir(root).glob("Q-*.md")):
        text=p.read_text(encoding="utf-8"); fm=_frontmatter(text)
        qid=str(fm.get("id") or p.stem)
        rows.append({"id":qid,"title":str(fm.get("title") or re.sub(rf"^#\s+{re.escape(qid)}\s*[·—-]?\s*","",text.splitlines()[text.startswith('---') and next((i for i,x in enumerate(text.splitlines()) if i>0 and x=='---'),0)+1 or 0] if text.splitlines() else qid)),"status":str(fm.get("status") or "inbox"),"created":str(fm.get("created") or ""),"updated":str(fm.get("updated") or ""),"papers":fm.get("papers",[]) if isinstance(fm.get("papers",[]),list) else [],"comparisons":fm.get("comparisons",[]) if isinstance(fm.get("comparisons",[]),list) else [],"findings":fm.get("findings",[]) if isinstance(fm.get("findings",[]),list) else [],"experiments":fm.get("experiments",[]) if isinstance(fm.get("experiments",[]),list) else [],"question":_section(text,"原始疑问"),"current_judgement":_section(text,"当前判断"),"investigation":_section(text,"深究记录"),"path":str(p.relative_to(root)),"_canonical_rev":"sha256:"+hashlib.sha256(text.encode()).hexdigest()})
    return rows

def save_question(root, q, existing=None):
    qid=q["id"]; p=questions_dir(root)/f"{qid}.md"; old=p.read_text(encoding="utf-8") if p.exists() else ""
    created=q.get("created") or (existing or {}).get("created") or now_iso(); updated=q.get("updated") or now_iso()
    def yl(key):
        vals=q.get(key,[]) or []
        return f"{key}:\n"+"".join(f"  - {_yaml_scalar(x)}\n" for x in vals)
    front="---\n"+f'id: {_yaml_scalar(qid)}\ntype: research-question\ntitle: {_yaml_scalar(q.get("title",""))}\nstatus: {_yaml_scalar(q.get("status","inbox"))}\ncreated: {_yaml_scalar(created)}\nupdated: {_yaml_scalar(updated)}\n'+yl("papers")+yl("comparisons")+yl("findings")+yl("experiments")+"---\n"
    if old:
        end=old.find("\n---\n",4); body=old[end+5:] if old.startswith("---\n") and end>=0 else old
    else:
        body=f'# {qid} · {q.get("title","")}\n\n## 原始疑问\n\n{q.get("question","")}\n\n## 当前判断\n\n{q.get("current_judgement","") or "（待核验；不能作为已验证 Claim）"}\n\n## 深究记录\n\n{q.get("investigation","") or "在这里用 Obsidian 或工作台持续记录推理、证据与反例。"}\n\n## 后续去向\n\n- （可关联 Finding、Comparison、Claim、Idea 或 Experiment）\n'
    body=re.sub(r"^# .*?$",f'# {qid} · {q.get("title","")}',body,count=1,flags=re.M)
    for heading,key in [("原始疑问","question"),("当前判断","current_judgement"),("深究记录","investigation")]:
        if key in q: body=_replace_section(body,heading,q.get(key,""))
    p.write_text(front+body.lstrip(),encoding="utf-8")
    refresh_v2_index(root, actor_id="web-legacy", content=False)
    return p

def create_question(root, fields):
    rows=read_questions(root); qid=next_object_id(rows,"Q")
    q={"id":qid,"title":fields.get("title") or str(fields.get("question","")).strip().splitlines()[0][:80],"status":fields.get("status","inbox"),"question":fields.get("question",""),"current_judgement":fields.get("current_judgement",""),"investigation":fields.get("investigation",""),"papers":fields.get("papers",[]) or [],"comparisons":fields.get("comparisons",[]) or [],"findings":fields.get("findings",[]) or [],"experiments":fields.get("experiments",[]) or [],"created":now_iso(),"updated":now_iso()}
    from survey_tool.integrations import generate_obsidian_indexes
    save_question(root,q); generate_obsidian_indexes(root)
    return q

def ensure_finding_ids(data):
    used={str(f.get("id")) for c in data for f in (c.get("findings",[]) or []) if f.get("id")}; n=1
    for c in data:
        for f in c.get("findings",[]) or []:
            if not f.get("id"):
                while f"F-{n:03d}" in used: n+=1
                f["id"]=f"F-{n:03d}"; used.add(f["id"]); n+=1
    return data

def _comparison_path(root,cid): return _object_dirs(root)[1]/f"{cid}.md"

def _finding_path(root,fid): return _object_dirs(root)[2]/f"{fid}.md"

def sync_compares_from_markdown(root,data):
    """Canonical prose wins when edited in Obsidian; legacy JSON remains the structural compatibility index."""
    for c in data:
        p=_comparison_path(root,c.get("id",""))
        if p.exists():
            text=p.read_text(encoding="utf-8"); fm=_frontmatter(text); c["_canonical_rev"]=hashlib.sha256(text.encode()).hexdigest()
            c["name"]=str(fm.get("title") or c.get("name","")); c["mode"]=str(fm.get("mode") or c.get("mode","structured"))
            if isinstance(fm.get("papers"),list): c["papers"]=fm["papers"]
            analysis=_section(text,"关联分析")
            if analysis:
                c["analysis"]=analysis
                if c.get("mode","structured")=="structured": c["piAnalysis"]=analysis
            notes=_section(text,"自由笔记（Obsidian）")
            if notes: c["obsidian_notes"]=notes
        for f in c.get("findings",[]) or []:
            fp=_finding_path(root,f.get("id",""))
            if fp.exists():
                ft=fp.read_text(encoding="utf-8"); fm=_frontmatter(ft); f["_canonical_rev"]=hashlib.sha256(ft.encode()).hexdigest()
                body=_section(ft,"Finding")
                if body: f["text"]=body
                if fm.get("source"): f["source"]=fm["source"]
    return data

def save_compare_markdown(root,c):
    p=_comparison_path(root,c["id"]); old=p.read_text(encoding="utf-8") if p.exists() else ""
    # Optimistic merge: if Obsidian changed after this browser loaded the object,
    # preserve canonical prose instead of silently overwriting it with stale UI state.
    if old and c.get("_canonical_rev") and c["_canonical_rev"]!=hashlib.sha256(old.encode()).hexdigest():
        fm=_frontmatter(old); c["name"]=str(fm.get("title") or c.get("name","")); c["mode"]=str(fm.get("mode") or c.get("mode","structured"))
        if isinstance(fm.get("papers"),list): c["papers"]=fm["papers"]
        if _section(old,"关联分析"):
            c["analysis"]=_section(old,"关联分析")
            if c.get("mode","structured")=="structured": c["piAnalysis"]=c["analysis"]
    findings=[f.get("id") for f in c.get("findings",[]) if f.get("id")]
    def yl(k,vals): return f"{k}:\n"+"".join(f"  - {_yaml_scalar(x)}\n" for x in vals)
    front="---\n"+f'id: {_yaml_scalar(c["id"])}\ntype: comparison\ntitle: {_yaml_scalar(c.get("name",""))}\nmode: {_yaml_scalar(c.get("mode","structured"))}\nupdated: {_yaml_scalar(now_iso())}\n'+yl("papers",c.get("papers",[]) or [])+yl("axes",c.get("axes",[]) or [])+yl("findings",findings)+"---\n"
    if old:
        end=old.find("\n---\n",4); body=old[end+5:] if old.startswith("---\n") and end>=0 else old
    else:
        body=f'# {c["id"]} · {c.get("name","")}\n\n## 参与论文\n\n'+("\n".join(f"- [[{x}]]" for x in c.get("papers",[])) or "- （待添加）")+"\n\n## 关联分析\n\n\n\n## Findings\n\n\n\n## 自由笔记（Obsidian）\n\n这里可自由书写；survey-tool 不会覆盖本节。\n"
    body=re.sub(r"^# .*?$",f'# {c["id"]} · {c.get("name","")}',body,count=1,flags=re.M)
    body=_replace_section(body,"参与论文","\n".join(f"- [[{x}]]" for x in c.get("papers",[])) or "- （待添加）")
    body=_replace_section(body,"关联分析",c.get("analysis","") or c.get("piAnalysis","") or "（待分析）")
    body=_replace_section(body,"Findings","\n".join(f'- [[{f.get("id")}|{str(f.get("text","")).splitlines()[0][:70]}]]' for f in c.get("findings",[]) if f.get("id")) or "- （无）")
    p.write_text(front+body.lstrip(),encoding="utf-8")
    for f in c.get("findings",[]) or []:
        fp=_finding_path(root,f["id"]); fold=fp.read_text(encoding="utf-8") if fp.exists() else ""
        if fold and f.get("_canonical_rev") and f["_canonical_rev"]!=hashlib.sha256(fold.encode()).hexdigest():
            canonical_text=_section(fold,"Finding")
            if canonical_text: f["text"]=canonical_text
        ffront="---\n"+f'id: {_yaml_scalar(f["id"])}\ntype: finding\ntitle: {_yaml_scalar(str(f.get("text","")).splitlines()[0][:80])}\ncomparison: {_yaml_scalar(c["id"])}\nsource: {_yaml_scalar(f.get("source",""))}\nupdated: {_yaml_scalar(now_iso())}\n---\n'
        if fold:
            end=fold.find("\n---\n",4); fbody=fold[end+5:] if fold.startswith("---\n") and end>=0 else fold
        else: fbody=f'# {f["id"]}\n\n## Finding\n\n{f.get("text","")}\n\n## 证据与不确定性\n\n（在 Obsidian 中补充 `[[citekey]] §小节`；未核验内容不得提升为 Claim。）\n\n## 自由笔记（Obsidian）\n\n'
        fbody=re.sub(r"^# .*?$",f'# {f["id"]} · {str(f.get("text","")).splitlines()[0][:80]}',fbody,count=1,flags=re.M)
        fbody=_replace_section(fbody,"Finding",f.get("text",""))
        fp.write_text(ffront+fbody.lstrip(),encoding="utf-8")

def compares_path(root): return tool_dir(root) / "compares.json"

def read_compares(root, _sync=True):
    p = compares_path(root)
    if p.exists():
        try:
            data=json.loads(p.read_text(encoding="utf-8")); before=json.dumps(data,sort_keys=True,ensure_ascii=False)
            ensure_compare_ids(data); ensure_finding_ids(data)
            if _sync: sync_compares_from_markdown(root,data)
            if json.dumps(data,sort_keys=True,ensure_ascii=False)!=before:
                p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
            return data
        except Exception: pass
    return []

def _stable_slug(text, fallback):
    s=re.sub(r"[^a-z0-9]+","-",(text or "").lower()).strip("-")
    return (s[:36] or fallback)

def ensure_compare_ids(data):
    """Add invisible stable IDs without forcing a heavy schema migration."""
    used=set()
    for i,c in enumerate(data):
        cid=c.get("id") or f"cmp-{_stable_slug(c.get('name',''),str(i+1))}"
        base=cid; n=2
        while cid in used: cid=f"{base}-{n}"; n+=1
        c["id"]=cid; used.add(cid)
        ids=c.get("axisIds",{}) if isinstance(c.get("axisIds",{}),dict) else {}
        taken=set(ids.values())
        for j,title in enumerate(c.get("axes",[]) or []):
            key=str(title.get("title",title) if isinstance(title,dict) else title)
            if key not in ids:
                aid=f"axis-{_stable_slug(key,str(j+1))}"; basea=aid; k=2
                while aid in taken: aid=f"{basea}-{k}"; k+=1
                ids[key]=aid; taken.add(aid)
        c["axisIds"]=ids
    return data

def save_compares(root, data):
    data=ensure_finding_ids(ensure_compare_ids(data))
    for c in data: save_compare_markdown(root,c)
    compares_path(root).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    from survey_tool.integrations import generate_obsidian_indexes
    generate_obsidian_indexes(root)
    refresh_v2_index(root, actor_id="web-legacy", identity=False)
    return data

def read_citations(root):
    cm = root / "kernel" / "citations.md"
    if not cm.exists(): return {}
    txt = cm.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"^## \[([^\]\r\n]+)\][ \t]*\r?\n(.*?)(?=^## \[|\Z)", txt, re.M|re.S):
        key = m.group(1); body = m.group(2)
        d = {"citekey":key}
        for k in ["title","authors","year","doi","source_url","content_hash","fetched_at","local_pdf"]:
            mm = re.search(rf"^- {k}:[ \t]*([^\r\n]*)$", body, re.M)
            d[k] = mm.group(1).strip() if mm else ""
        out[key]=d
    return out

def _norm(s): return re.sub(r"[^a-z0-9]+","", (s or "").lower())

def resolve_paper_artifacts(root):
    """Scan papers/ (Zotero output) for MinerU dirs, map by normalized title.
    Returns {norm_title: {dir, images_dir, mineru_md, images:[abs]}}.
    Independent of ingest — works from Zotero sync output directly."""
    rk = str(root)
    if rk in server._RPA_CACHE: return server._RPA_CACHE[rk]
    out = {}
    pdir = root / "papers"
    if pdir.is_dir():
        for d in pdir.iterdir():
            if not d.is_dir(): continue
            for sub in [d, *(x for x in d.iterdir() if x.is_dir())]:
                img = sub/"images" if (sub/"images").is_dir() else (d/"images")
                mds = [p for p in sub.glob("*.md") if p.stat().st_size>5000] or [p for p in d.glob("*.md") if p.stat().st_size>5000]
                if img.is_dir() or mds:
                    nt = _norm(d.name)
                    out[nt] = {"dir":str(d),
                               "images_dir":str(img) if img.is_dir() else "",
                               "mineru_md":str(mds[0]) if mds else "",
                               "images":[str(p) for p in img.iterdir() if p.suffix.lower() in IMG_EXT] if img.is_dir() else []}
                    break
    server._RPA_CACHE[rk] = out
    return out

def artifacts_for(root, title):
    """Best-effort match a paper title to its MinerU artifacts."""
    arts = resolve_paper_artifacts(root)
    nt = _norm(title)
    if nt in arts: return arts[nt]
    # substring match either direction
    for k,v in arts.items():
        if k and (k in nt or nt in k):
            return v
    return {"dir":"","images_dir":"","mineru_md":"","images":[]}

def list_images(root, citekey):
    # 1) citations.md mineru_images (if ingested)
    c = read_citations(root).get(citekey,{})
    img_dir = c.get("mineru_images") or ""
    if img_dir and pathlib.Path(img_dir).is_dir():
        return [str(p) for p in pathlib.Path(img_dir).iterdir() if p.suffix.lower() in IMG_EXT]
    # 2) match by title from INDEX → MinerU dir in papers/
    for p in read_papers(root):
        if citekey_for(p) == citekey:
            return artifacts_for(root, p["title"]).get("images",[])
    # 3) fallback: citekey substring vs paper dir name
    arts = resolve_paper_artifacts(root)
    for k,v in arts.items():
        if citekey.lower() in k:
            return v.get("images",[])
    return []

def mineru_md_for(root, citekey):
    for p in read_papers(root):
        if citekey_for(p) == citekey:
            return artifacts_for(root, p["title"]).get("mineru_md","")
    arts = resolve_paper_artifacts(root)
    for k,v in arts.items():
        if citekey.lower() in k:
            return v.get("mineru_md","")
    return ""

def _mineru_md_for_paper(root, paper):
    d = paper.get("dir","")
    if d:
        p = pathlib.Path(d)
        for sub in [p/"hybrid_auto", p]:
            if sub.is_dir():
                mds = [x for x in sub.glob("*.md") if x.stat().st_size>5000]
                if mds: return mds[0]
    art = artifacts_for(root, paper.get("title",""))
    return pathlib.Path(art["mineru_md"]) if art.get("mineru_md") else None
