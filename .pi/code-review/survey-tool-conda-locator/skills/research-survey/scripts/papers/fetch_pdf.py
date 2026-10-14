#!/usr/bin/env python
"""Fetch an open-access PDF by arXiv id or DOI.
Tries arXiv (for arxiv ids) then Unpaywall (for DOIs). Saves to shell/03_evidence/papers/<citekey>.pdf.
Prints JSON with local path. Appends search_log."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
import argparse, urllib.request, urllib.parse, urllib.error, json, pathlib, re
from _common import project_root, papers_dir, ensure_layout, polite_email, emit, append_search_log, slug_citekey

def http_get(url, headers=None, timeout=180):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "research-survey/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def fetch_arxiv(arxiv_id):
    # arxiv PDF URL
    aid = arxiv_id
    url = f"https://arxiv.org/pdf/{aid}.pdf"
    data = http_get(url)
    if data[:4] != b"%PDF":
        raise RuntimeError(f"arxiv returned non-PDF for {aid}")
    return data, url

def fetch_unpaywall(doi, email):
    if "example.com" in email or not email:
        raise RuntimeError("Unpaywall requires a real email. Set `polite_email:` in shell/00_idea/context.md or export RSEARCH_EMAIL=<your@email>.")
    url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={email}"
    try:
        meta = json.loads(http_get(url, timeout=30))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Unpaywall HTTP {e.code} for doi {doi}: {e.read().decode('utf-8','ignore')[:200]}. Use a real polite_email.") from e
    best = meta.get("best_oa_location") or {}
    pdf_url = best.get("url_for_pdf") or best.get("url")
    if not pdf_url:
        # try any oa location with a pdf
        for loc in meta.get("oa_locations", []):
            if loc.get("url_for_pdf"):
                pdf_url = loc["url_for_pdf"]
                break
    if not pdf_url:
        raise RuntimeError(f"no OA PDF found via Unpaywall for doi {doi}")
    data = http_get(pdf_url)
    if data[:4] != b"%PDF":
        raise RuntimeError(f"unpaywall lead URL returned non-PDF: {pdf_url}")
    title = meta.get("title") or ""
    year = str(meta.get("year") or "")
    authors = [a.get("family", "") for a in meta.get("z_authors") or []]
    return data, pdf_url, {"title": title, "year": year, "authors": authors, "doi": doi}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--id", required=True, help="arXiv id (e.g. 2401.12345) or DOI (e.g. 10.x/y)")
    ap.add_argument("--citekey", default=None, help="citekey; auto-generated if omitted")
    ap.add_argument("--doi", default=None, help="DOI (if --id is an arxiv id but you also know the DOI)")
    args = ap.parse_args()
    root = project_root(args.project)
    ensure_layout(root)
    email = polite_email(root)

    is_arxiv = bool(re.match(r"^\d{4}\.\d{4,5}(v\d+)?$|^[a-z\-]+/\d{7}$", args.id))
    try:
        if is_arxiv:
            data, src_url = fetch_arxiv(args.id)
            meta = {"title": "", "year": "", "authors": [], "arxiv_id": args.id, "doi": args.doi or ""}
        else:
            data, src_url, meta = fetch_unpaywall(args.id, email)
            meta["arxiv_id"] = ""
        ck = args.citekey or slug_citekey(meta.get("title",""), meta.get("year",""), (meta.get("authors") or [""])[0])
        out = papers_dir(root) / f"{ck}.pdf"
        out.write_bytes(data)
        append_search_log(root, "fetch_pdf", args.id, [{"citekey": ck, "title": meta.get("title",""), "url": src_url, "year": meta.get("year",""), "doi": meta.get("doi","")}], note=f"saved {out.name}")
        emit({"citekey": ck, "local_pdf": str(out), "source_url": src_url, "bytes": len(data), **meta})
    except Exception as e:
        append_search_log(root, "fetch_pdf", args.id, [], note=f"FAIL: {e}")
        emit({"error": str(e), "id": args.id})
        sys.exit(1)

if __name__ == "__main__":
    main()