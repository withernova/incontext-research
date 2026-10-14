#!/usr/bin/env python
"""Generate an R2 adversarial review scaffold for a claim and append it to kernel/review_log.md.
The agent fills in the body (this just creates the structure + reminds of the adversarial stance)."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
import argparse, pathlib, re
from _common import project_root, emit, now_iso

def get_claim(txt, cid):
    m = re.search(rf"^## {re.escape(cid)}\n(.*?)(?=\n## |\Z)", txt, re.S | re.M)
    return m.group(1) if m else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--claim", required=True)
    args = ap.parse_args()
    root = project_root(args.project)
    claims_md = root / "kernel" / "claims.md"
    if not claims_md.exists():
        sys.exit("[err] claims.md not found")
    ctxt = claims_md.read_text(encoding="utf-8")
    body = get_claim(ctxt, args.claim)
    if not body:
        sys.exit(f"[err] claim {args.claim} not found in claims.md")
    rl = root / "kernel" / "review_log.md"
    if not rl.exists():
        rl.write_text("# Review log (append-only. NEVER delete entries.)\n", encoding="utf-8")
    scaffold = f"""
## {now_iso()} | {args.claim} | R2 adversarial
> stance: TRY TO KILL this claim. Find the weakest link, hunt counterexamples, expose ignored confounds.
- claim_text: {re.search(r'(?m)^- text: (.*)$', body).group(1) if re.search(r'(?m)^- text: (.*)$', body) else ''}
- sources: {re.search(r'(?m)^- sources: (.*)$', body).group(1) if re.search(r'(?m)^- sources: (.*)$', body) else ''}
- weakest_link: 
- counterexample_search_queries: []
- counterexamples_found: []
- confounds_ignored: 
- contradicting_evidence_in_corpus: 
- verdict: PASS | REJECT | NEEDS_MORE_EVIDENCE
- reasoning: 
- next_action: 
"""
    with open(rl, "a", encoding="utf-8") as f:
        f.write(scaffold)
    emit({"claim": args.claim, "review_log": str(rl), "note": "Fill the scaffold, then run promote_claim.py with --r2-verdict PASS if it survived."})

if __name__ == "__main__":
    main()