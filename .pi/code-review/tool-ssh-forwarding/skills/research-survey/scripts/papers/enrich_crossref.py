#!/usr/bin/env python
"""Enrich/verify citation metadata via CrossRef by DOI. Prints JSON."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
import argparse, urllib.request, urllib.parse, json
from _common import project_root, polite_email, emit, append_search_log

def lookup(doi, email):
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    req = urllib.request.Request(url, headers={"User-Agent": f"research-survey/0.1 (mailto:{email})"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    msg = data.get("message", {})
    title = (msg.get("title") or [""])[0]
    year = ""
    if msg.get("published-print") or msg.get("published-online"):
        d = msg.get("published-print") or msg.get("published-online")
        year = str((d.get("date-parts") or [[""]])[0][0])
    authors = [f"{a.get('family','')}" for a in msg.get("author", [])]
    return {
        "title": title,
        "authors": authors,
        "year": year,
        "doi": doi,
        "venue": (msg.get("container-title") or [""])[0],
        "publisher": msg.get("publisher", ""),
        "url": msg.get("URL", ""),
        "type": msg.get("type", ""),
        "references_count": len(msg.get("reference", []) or []),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--doi", required=True)
    ap.add_argument("--no-log", action="store_true")
    args = ap.parse_args()
    root = project_root(args.project)
    email = polite_email(root)
    try:
        meta = lookup(args.doi, email)
    except Exception as e:
        if not args.no_log:
            append_search_log(root, "crossref", args.doi, [], note=f"FAIL: {e}")
        emit({"error": str(e), "doi": args.doi})
        sys.exit(1)
    if not args.no_log:
        append_search_log(root, "crossref", args.doi, [{"citekey": "", "title": meta["title"], "url": meta["url"], "year": meta["year"], "doi": meta["doi"]}])
    emit(meta)

if __name__ == "__main__":
    main()