#!/usr/bin/env python
"""Search arXiv. No API key. Prints JSON; appends to search_log.md."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
import argparse, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from _common import project_root, append_search_log, emit, slug_citekey, polite_email

NS = {"a": "http://www.w3.org/2005/Atom"}

def search(query, email, max_results=10):
    base = "https://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
    }
    url = base + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": f"research-survey/0.1 (mailto:{email})"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    root = ET.fromstring(data)
    hits = []
    for e in root.findall("a:entry", NS):
        title = " ".join((e.findtext("a:title", default="", namespaces=NS) or "").split())
        arxiv_url = e.findtext("a:id", default="", namespaces=NS) or ""
        arxiv_id = arxiv_url.rsplit("/", 1)[-1]
        published = e.findtext("a:published", default="", namespaces=NS) or ""
        year = published[:4] if published else ""
        authors = [a.findtext("a:name", default="", namespaces=NS) for a in e.findall("a:author", NS)]
        a0 = authors[0].split()[-1] if authors else ""
        doi = e.findtext("a:arxiv:doi", default="", namespaces=NS) or ""  # may be empty
        # arxiv:doi is in a different namespace; try direct find
        doi_el = e.find("{http://arxiv.org/schemas/atom}doi")
        if doi_el is not None and doi_el.text:
            doi = doi_el.text
        hits.append({
            "citekey": slug_citekey(title, year, a0),
            "title": title,
            "authors": authors,
            "year": year,
            "arxiv_id": arxiv_id,
            "url": arxiv_url,
            "doi": doi,
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
    try:
        hits = search(args.query, polite_email(root), args.max)
    except Exception as e:
        if not args.no_log:
            append_search_log(root, "arxiv", args.query, [], note=f"FAIL: {e}")
        emit({"source": "arxiv", "query": args.query, "error": str(e), "hits": []})
        sys.exit(1)
    if not args.no_log:
        append_search_log(root, "arxiv", args.query, hits)
    emit({"source": "arxiv", "query": args.query, "hits": hits})

if __name__ == "__main__":
    main()
