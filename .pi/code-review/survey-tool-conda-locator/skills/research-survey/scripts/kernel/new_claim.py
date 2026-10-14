#!/usr/bin/env python
"""Append a new claim to kernel/claims.md with status=draft."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
import argparse, pathlib, re
from _common import project_root, emit, now_iso

def next_id(txt):
    ids = [int(m) for m in re.findall(r"^## C(\d+)", txt, re.M)]
    return f"C{(max(ids)+1) if ids else 1:02d}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--sources", default="", help="comma-separated citekeys/locators")
    ap.add_argument("--rationale", default="")
    args = ap.parse_args()
    root = project_root(args.project)
    cm = root / "kernel" / "claims.md"
    cm.parent.mkdir(parents=True, exist_ok=True)
    if not cm.exists():
        cm.write_text("# Claims registry (kernel truth)\n\nStatus lifecycle: draft -> supported -> validated (needs R2 PASS + human approved + >=1 hashed source)\n        draft -> contradicted / contradicted_by_prior / partial / inference_only\n\n", encoding="utf-8")
    txt = cm.read_text(encoding="utf-8")
    cid = next_id(txt)
    block = f"""
## {cid}
- text: {args.text}
- status: draft
- confidence: 
- sources: {args.sources}
- contradicting_evidence: 
- r2_verdict: pending
- human_verdict: pending
- created: {now_iso()}
- rationale: {args.rationale}
"""
    cm.write_text(txt.rstrip() + "\n" + block, encoding="utf-8")
    emit({"claim": cid, "text": args.text, "claims_md": str(cm)})

if __name__ == "__main__":
    main()