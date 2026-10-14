#!/usr/bin/env python
"""Ingest a PDF into the corpus: compute SHA-256, write kernel/citations.md,
create shell/03_evidence/papers/<citekey>.md note skeleton. Idempotent on citekey.
Use this for seed papers AND fetched PDFs (fetch_pdf.py only saves the file; ingest records provenance)."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
import argparse, pathlib, re, datetime
from _common import project_root, papers_dir, citations_md, ensure_layout, sha256_file, now_iso, emit

CITEKEY_RE = re.compile(r"^## \[(?P<key>[^\]]+)\]", re.M)


def detect_mineru(pdf_path: pathlib.Path):
    """探测同名/同级目录下 MinerU 抽取产物，返回 (mineru_md, mineru_images)。

    MinerU 典型布局：
        papers/<Title>_<year>.pdf
        papers/<Title>_<year>/hybrid_auto/<Title>_<year>.md   + images/
    也会兼容 <Title>_<year>/<Title>_<year>.md + images/ 的平铺布局。
    返回首个匹配的 .md 及其同级/子级 images/ 目录（无则 None）。
    """
    if pdf_path is None:
        return None, None
    stem = pdf_path.stem
    parent = pdf_path.parent
    candidates = []
    # 1) 同名子目录
    sub = parent / stem
    if sub.is_dir():
        candidates.append(sub)
        # 2) 子目录下的 hybrid_auto / *_auto
        for d in sub.iterdir():
            if d.is_dir() and "auto" in d.name.lower():
                candidates.append(d)
    # 3) PDF 同级直接平铺（较少见）
    candidates.append(parent)

    for d in candidates:
        if not d.is_dir():
            continue
        # 找与 PDF 同名（或以 PDF 名为前缀）的 .md
        md_files = [p for p in d.glob("*.md") if p.stem == stem or p.stem.startswith(stem)]
        # 回退：目录内任意较大的 .md（排除我们的 note skeleton 路径）
        if not md_files:
            md_files = [p for p in d.glob("*.md") if p.stat().st_size > 20000]
        if not md_files:
            continue
        md_files.sort(key=lambda p: (p.stem != stem, -p.stat().st_size))
        mineru_md = md_files[0]
        # images/ 在 .md 同级或上一级
        for img_dir in [mineru_md.parent / "images", mineru_md.parent.parent / "images"]:
            if img_dir.is_dir():
                return mineru_md, img_dir
        return mineru_md, None
    return None, None

def upsert_citation(root, citekey, *, title, authors, year, url, doi, pdf_path, content_hash, extra=""):
    cm = citations_md(root)
    if not cm.exists():
        cm.write_text("# Citations (kernel truth, append-only metadata; content_hash immutable)\n", encoding="utf-8")
    txt = cm.read_text(encoding="utf-8")
    block = f"""## [{citekey}]
- title: {title or "[UNVERIFIED]"}
- authors: {", ".join(authors) if authors else "[unknown]"}
- year: {year or ""}
- doi: {doi or ""}
- source_url: {url or ""}
- content_hash: {content_hash}
- fetched_at: {now_iso()}
- local_pdf: {pdf_path}
{extra}
"""
    if f"## [{citekey}]" in txt:
        # update block but preserve an existing content_hash if present and unchanged
        existing = re.search(rf"## \[{re.escape(citekey)}\]\n(.*?)(?=\n## \[|\Z)", txt, re.S)
        if existing:
            old_hash = re.search(r"content_hash:\s*(sha256:\S+)", existing.group(1))
            if old_hash and old_hash.group(1) != content_hash:
                extra = extra + f"\n- prior_content_hash: {old_hash.group(1)}  # CHANGED - flag to human\n"
                block = f"""## [{citekey}]
- title: {title or "[UNVERIFIED]"}
- authors: {", ".join(authors) if authors else "[unknown]"}
- year: {year or ""}
- doi: {doi or ""}
- source_url: {url or ""}
- content_hash: {content_hash}
- fetched_at: {now_iso()}
- local_pdf: {pdf_path}
{extra}
"""
            txt = re.sub(rf"## \[{re.escape(citekey)}\]\n.*?(?=\n## \[|\Z)", block.rstrip()+"\n", txt, flags=re.S)
            cm.write_text(txt, encoding="utf-8")
        else:
            cm.write_text(txt + block, encoding="utf-8")
    else:
        cm.write_text(txt.rstrip()+"\n"+block, encoding="utf-8")

def note_skeleton(citekey, title, pdf_rel, mineru_md=None, mineru_images=None):
    mineru_block = ""
    if mineru_md:
        mineru_block += f"\n> mineru_md: {mineru_md}   # ← 优先阅读对象（含图像 + 公式，见 SKILL.md C2）"
    if mineru_images:
        mineru_block += f"\n> mineru_images: {mineru_images}"
    if not mineru_block:
        mineru_block = "\n> 未检测到 MinerU 产物；回退到对 PDF 做 read/pdf-converter 抽取。"
    return f"""# [[{citekey}]] — {title or "[未命名]"}

> source: {pdf_rel}
> content_hash 仍以原始 PDF 计算；以下阅读以 MinerU .md 为准（若有）。{mineru_block}
> 引用格式：[[{citekey}]] §小节。

## 书目信息
- authors:
- year:
- venue:
- doi:

## TL;DR（3 行，用你自己的话）

## 与本项目相关的关键声明

## 方法 / 设置

## 结果 / 表格（标注表/图编号；图像见 mineru_images）

## 局限 / 效度威胁

## 可能引用的原句（附 §定位）
- p.X §: "..." — 支持哪条声明？[Cxx]

## 对我们任意声明的反驳证据
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--pdf", required=True, help="path to a PDF file (local)")
    ap.add_argument("--citekey", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--authors", default="", help="comma-separated")
    ap.add_argument("--year", default="")
    ap.add_argument("--url", default="")
    ap.add_argument("--doi", default="")
    ap.add_argument("--extra", default="")
    ap.add_argument("--copy", action="store_true", help="copy the PDF into shell/03_evidence/papers/ if not already there")
    args = ap.parse_args()
    root = project_root(args.project)
    ensure_layout(root)
    src = pathlib.Path(args.pdf).resolve()
    if not src.exists():
        sys.exit(f"[err] pdf not found: {src}")
    if args.copy or (papers_dir(root) not in src.parents):
        dest = papers_dir(root) / f"{args.citekey}.pdf"
        if src != dest:
            dest.write_bytes(src.read_bytes())
        pdf_path = dest
    else:
        pdf_path = src
    h = sha256_file(pdf_path)
    rel = pdf_path.relative_to(root).as_posix() if str(root) in str(pdf_path) else str(pdf_path)
    # 探测 MinerU 产物（C2）：优先在原始 PDF 所在路径附近找，而非复制后的副本
    mineru_md, mineru_images = detect_mineru(src)
    authors = [a.strip() for a in args.authors.split(",") if a.strip()]
    extra = args.extra
    if mineru_md:
        mineru_note = f"mineru_md: {mineru_md}"
        if mineru_images:
            mineru_note += f" | mineru_images: {mineru_images}"
        extra = (extra + "\n" if extra else "") + f"- {mineru_note}  # 优先阅读对象（C2）"
    upsert_citation(root, args.citekey, title=args.title, authors=authors, year=args.year,
                    url=args.url, doi=args.doi, pdf_path=rel, content_hash=h, extra=extra)
    note = papers_dir(root) / f"{args.citekey}.md"
    if not note.exists():
        note.write_text(note_skeleton(args.citekey, args.title, rel, mineru_md=mineru_md, mineru_images=mineru_images), encoding="utf-8")
    emit({"citekey": args.citekey, "content_hash": h, "local_pdf": str(pdf_path), "mineru_md": str(mineru_md) if mineru_md else None, "mineru_images": str(mineru_images) if mineru_images else None, "note": str(note), "citations_md": str(citations_md(root))})

if __name__ == "__main__":
    main()