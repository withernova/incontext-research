#!/usr/bin/env python
"""Promotion gate. Sets a claim to status=validated ONLY if:
  (a) r2_verdict == PASS in claims.md
  (b) human_verdict == approved
  (c) >=1 source citekey exists in kernel/citations.md with a content_hash
Can also be used to set r2_verdict / human_verdict before attempting promotion."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
import argparse, pathlib, re
from _common import project_root, emit, now_iso

def get_block(txt, cid):
    m = re.search(rf"^## {re.escape(cid)}\n(.*?)(?=\n## |\Z)", txt, re.S | re.M)
    return m

def set_field(s, field, value):
    return re.sub(rf"(?m)^- {field}: .*$", f"- {field}: {value}", s)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--claim", required=True)
    ap.add_argument("--r2-verdict", default=None, choices=[None,"PASS","REJECT","NEEDS_MORE_EVIDENCE"])
    ap.add_argument("--human-verdict", default=None, choices=[None,"approved","rejected","pending"])
    ap.add_argument("--force", action="store_true", help="promote even if a gate fails (will flag in review_log - use only with explicit human reason)")
    args = ap.parse_args()
    root = project_root(args.project)
    cm = root / "kernel" / "claims.md"
    if not cm.exists():
        sys.exit("[err] claims.md not found")
    txt = cm.read_text(encoding="utf-8")
    m = get_block(txt, args.claim)
    if not m:
        sys.exit(f"[err] claim {args.claim} not found")
    block = m.group(1)

    # optionally update fields (chain on the string)
    if args.r2_verdict:
        block = set_field(block, "r2_verdict", args.r2_verdict)
    if args.human_verdict:
        block = set_field(block, "human_verdict", args.human_verdict)

    # re-read fields from (possibly updated) block
    def fld(name):
        r = re.search(rf"(?m)^- {name}: (.*)$", block)
        return r.group(1).strip() if r else ""
    r2 = fld("r2_verdict")
    hv = fld("human_verdict")
    sources = fld("sources")

    # gate checks
    citekeys = [s.strip().split(" ")[0].strip("[]") for s in re.findall(r"\[\[?([^\]]+)\]\]?", sources)] or [s.strip().split(" ")[0] for s in sources.split(",") if s.strip()]
    citekeys = [c for c in citekeys if c and not c.lower().startswith("unverified")]

    cit_txt = (root / "kernel" / "citations.md").read_text(encoding="utf-8") if (root / "kernel" / "citations.md").exists() else ""
    verified_sources = []
    for ck in citekeys:
        bm = re.search(rf"^## \[{re.escape(ck)}\]\n(.*?)(?=\n## \[|\Z)", cit_txt, re.S | re.M)
        if bm and re.search(r"(?m)^- content_hash: sha256:", bm.group(1)):
            verified_sources.append(ck)

    gates = {
        "r2_pass": r2 == "PASS",
        "human_approved": hv == "approved",
        "has_hashed_source": len(verified_sources) >= 1,
    }
    can_promote = all(gates.values())

    # log the promotion attempt
    rl = root / "kernel" / "review_log.md"
    if not rl.exists():
        rl.write_text("# Review log (append-only. NEVER delete entries.)\n", encoding="utf-8")
    entry = f"""
## {now_iso()} | {args.claim} | PROMOTION_ATTEMPT
- r2_verdict: {r2}
- human_verdict: {hv}
- sources: {sources}
- verified_hashed_sources: {verified_sources}
- gates: {gates}
- result: {"PROMOTED -> validated" if (can_promote or args.force) else "BLOCKED"}
"""
    if args.force and not can_promote:
        entry += "- !! FORCED promotion (human override) -- reason must be recorded above by the agent\n"
    with open(rl, "a", encoding="utf-8") as f:
        f.write(entry)

    if can_promote or args.force:
        block = re.sub(r"(?m)^- status: .*$", "- status: validated", block)
        new_txt = txt[:m.start()] + f"## {args.claim}\n" + block + txt[m.end():]
        cm.write_text(new_txt, encoding="utf-8")
        emit({"claim": args.claim, "promoted": True, "forced": args.force and not can_promote, "gates": gates, "verified_sources": verified_sources})
    else:
        # still persist any r2/human updates
        new_txt = txt[:m.start()] + f"## {args.claim}\n" + block + txt[m.end():]
        cm.write_text(new_txt, encoding="utf-8")
        emit({"claim": args.claim, "promoted": False, "gates": gates, "verified_sources": verified_sources, "reason": "gate(s) failed; see review_log"})

if __name__ == "__main__":
    main()