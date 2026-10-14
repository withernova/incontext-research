#!/usr/bin/env python
"""Verify content_hash of ingested PDFs. Re-hash the local PDF and compare to kernel/citations.md."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
import argparse, pathlib, re
from _common import project_root, citations_md, sha256_file, emit

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--citekey", default=None, help="check one; else check all")
    args = ap.parse_args()
    root = project_root(args.project)
    cm = citations_md(root)
    if not cm.exists():
        sys.exit("[err] citations.md not found")
    txt = cm.read_text(encoding="utf-8")
    blocks = re.findall(r"^## \[(?P<k>[^\]]+)\]\n(?P<b>.*?)(?=\n## \[|\Z)", txt, re.S | re.M)
    results = []
    for k, b in blocks:
        if args.citekey and k != args.citekey:
            continue
        stored = re.search(r"(?m)^- content_hash: (sha256:\S+)", b)
        path = re.search(r"(?m)^- local_pdf: (.*)$", b)
        rec = {"citekey": k, "stored_hash": stored.group(1) if stored else None, "local_pdf": path.group(1).strip() if path else None}
        if rec["local_pdf"]:
            p = pathlib.Path(rec["local_pdf"])
            if not p.is_absolute():
                p = root / p
            if p.exists():
                rec["computed_hash"] = sha256_file(p)
                rec["ok"] = (rec["computed_hash"] == rec["stored_hash"])
            else:
                rec["computed_hash"] = None
                rec["ok"] = False
                rec["error"] = "pdf missing"
        else:
            rec["ok"] = False
            rec["error"] = "no local_pdf"
        results.append(rec)
    emit({"results": results, "all_ok": all(r.get("ok") for r in results) if results else False})
    if not all(r.get("ok") for r in results) if results else False:
        sys.exit(1)

if __name__ == "__main__":
    main()