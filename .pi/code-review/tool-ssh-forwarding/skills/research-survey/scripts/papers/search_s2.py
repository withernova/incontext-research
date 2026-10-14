#!/usr/bin/env python
"""Search Semantic Scholar. No key required (rate-limited). Prints JSON; appends search_log."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
import argparse, urllib.parse, urllib.request, json, os, time
from _common import project_root, append_search_log, emit, slug_citekey

def search(query, max_results=10, api_key=None):
    base = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": max_results,
        "fields": "title,authors,year,externalIds,openAccessPdf,citationCount,abstract",
    }
    url = base + "?" + urllib.parse.urlencode(params)
    headers = {"User-Agent": "research-survey/0.1"}
    if api_key:
        headers["x-api-key"] = api_key
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    hits = []
    for p in data.get("data", []):
        title = (p.get("title") or "").strip()
        year = str(p.get("year") or "")
        ext = p.get("externalIds") or {}
        doi = ext.get("DOI", "")
        arxiv_id = ext.get("ArXiv", "")
        authors = [a.get("name", "") for a in p.get("authors", [])]
        a0 = authors[0].split()[-1] if authors else ""
        oa = p.get("openAccessPdf") or {}
        hits.append({
            "citekey": slug_citekey(title, year, a0),
            "title": title,
            "authors": authors,
            "year": year,
            "doi": doi,
            "arxiv_id": arxiv_id,
            "url": f"https://www.semanticscholar.org/paper/{p.get('paperId','')}",
            "oa_pdf_url": oa.get("url"),
            "citation_count": p.get("citationCount", 0),
            "abstract": (p.get("abstract") or "")[:500],
        })
    return hits

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("query")
    ap.add_argument("--max", type=int, default=10)
    ap.add_argument("--no-log", action="store_true")
    args = ap.parse_args()
    root = project_root(args.project)
    key = os.environ.get("S2_API_KEY")
    try:
        hits = search(args.query, args.max, key)
    except Exception as e:
        if not args.no_log:
            append_search_log(root, "s2", args.query, [], note=f"FAIL: {e}")
        emit({"source": "s2", "query": args.query, "error": str(e), "hits": []})
        sys.exit(1)
    if not args.no_log:
        append_search_log(root, "s2", args.query, hits)
    emit({"source": "s2", "query": args.query, "hits": hits})

if __name__ == "__main__":
    main()