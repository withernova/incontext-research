#!/usr/bin/env python
"""Search OpenAlex. No API key (polite email recommended). Prints JSON; appends search_log."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
import argparse, urllib.parse, urllib.request, json, re
from _common import project_root, append_search_log, emit, polite_email, slug_citekey

def search(query, email, max_results=10):
    base = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per-page": max_results,
        "mailto": email,
    }
    url = base + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": f"research-survey/0.1 (mailto:{email})"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    hits = []
    for w in data.get("results", []):
        title = (w.get("title") or "").strip()
        year = str(w.get("publication_year") or "")
        doi = (w.get("doi") or "").replace("https://doi.org/", "")
        authors = [a.get("author", {}).get("display_name", "") for a in w.get("authorships", [])]
        a0 = authors[0].split()[-1] if authors else ""
        url0 = w.get("id") or ""
        arxiv_id = ""
        candidates = [(w.get("ids") or {}).get("arxiv")]
        for location in [w.get("primary_location"),w.get("best_oa_location"),*((w.get("locations") or []))]:
            if isinstance(location,dict): candidates.extend([location.get("landing_page_url"),location.get("pdf_url")])
        for candidate in candidates:
            plain = re.fullmatch(r"(?:\d{4}\.\d{4,5}|[A-Za-z][A-Za-z0-9.-]*/\d{7})(?:v\d+)?",str(candidate or ""))
            if plain: arxiv_id=plain.group(0); break
            match = re.search(r"arxiv\.org/(?:abs|pdf)/((?:\d{4}\.\d{4,5}|[A-Za-z][A-Za-z0-9.-]*/\d{7})(?:v\d+)?)(?:\.pdf)?",str(candidate or ""),re.I)
            if match: arxiv_id=match.group(1); break
        oa_url = f"https://arxiv.org/pdf/{urllib.parse.quote(arxiv_id,safe='/.')}.pdf" if arxiv_id else (w.get("open_access") or {}).get("oa_url")
        hits.append({
            "citekey": slug_citekey(title, year, a0),
            "title": title,
            "authors": authors,
            "year": year,
            "doi": doi,
            "url": url0,
            "openalex_id": (w.get("id") or "").rsplit("/", 1)[-1],
            "is_oa": True if arxiv_id else (w.get("open_access") or {}).get("is_oa", False),
            "oa_url": oa_url,
            "arxiv_id": arxiv_id,
            "cited_by_count": w.get("cited_by_count", 0),
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
    email = polite_email(root)
    try:
        hits = search(args.query, email, args.max)
    except Exception as e:
        if not args.no_log:
            append_search_log(root, "openalex", args.query, [], note=f"FAIL: {e}")
        emit({"source": "openalex", "query": args.query, "error": str(e), "hits": []})
        sys.exit(1)
    if not args.no_log:
        append_search_log(root, "openalex", args.query, hits)
    emit({"source": "openalex", "query": args.query, "hits": hits})

if __name__ == "__main__":
    main()
