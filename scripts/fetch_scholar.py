"""Fetch publications from a Google Scholar profile and write them to assets/data/papers.json.

Usage: python scripts/fetch_scholar.py
Requires: pip install scholarly
"""
import difflib
import json
import pathlib
import re

import requests
from scholarly import scholarly, ProxyGenerator

SCHOLAR_USER_ID = "5Oi5SOEAAAAJ"
OUTPUT_PATH = pathlib.Path(__file__).resolve().parent.parent / "assets" / "data" / "papers.json"


def _normalize(text):
    return re.sub(r"\W+", " ", text or "").strip().lower()


def crossref_lookup(title):
    # Cross-reference Scholar's entry against Crossref (the DOI registry) so
    # we can link to the publisher's page (via doi.org) instead of whatever
    # raw URL Scholar happened to index — which is sometimes a direct PDF —
    # and, when available, pull Crossref's full (untruncated) abstract.
    try:
        response = requests.get(
            "https://api.crossref.org/works",
            params={"query.bibliographic": title, "rows": 1},
            timeout=10,
        )
        response.raise_for_status()
        items = json.loads(response.content.decode("utf-8"))["message"]["items"]
        if not items:
            return None

        item = items[0]
        candidate_title = (item.get("title") or [""])[0]
        similarity = difflib.SequenceMatcher(
            None, _normalize(title), _normalize(candidate_title)
        ).ratio()
        if similarity < 0.9:
            return None

        doi = item.get("DOI")
        abstract = item.get("abstract")
        if abstract:
            abstract = re.sub(r"<[^>]+>", " ", abstract)
            abstract = re.sub(r"\s+", " ", abstract).strip()
            abstract = re.sub(r"^Abstract\s+", "", abstract)

        return {
            "link": f"https://doi.org/{doi}" if doi else None,
            "abstract": abstract or None,
        }
    except Exception as exc:
        print(f"Crossref lookup failed for '{title[:60]}...': {exc}")
        return None


def setup_proxy():
    # Google Scholar blocks requests from GitHub Actions' shared IP ranges.
    # Routing through a free rotating proxy usually gets past that. If proxy
    # setup itself fails (e.g. no working free proxies right now), fall back
    # to a direct connection rather than aborting.
    try:
        pg = ProxyGenerator()
        if pg.FreeProxies():
            scholarly.use_proxy(pg)
            print("Using a free rotating proxy for Scholar requests")
        else:
            print("No working free proxy found; using a direct connection")
    except Exception as exc:
        print(f"Proxy setup failed ({exc}); using a direct connection")


def fetch_papers():
    author = scholarly.search_author_id(SCHOLAR_USER_ID)
    author = scholarly.fill(author, sections=["publications"])

    papers = []
    for pub in author.get("publications", []):
        bib = pub.get("bib", {})
        filled = scholarly.fill(pub)
        bib = filled.get("bib", bib)
        title = bib.get("title", "").strip()
        link = filled.get("pub_url") or filled.get("eprint_url") or ""
        abstract = bib.get("abstract", "").strip()

        crossref = crossref_lookup(title)
        if crossref:
            link = crossref["link"] or link
            abstract = crossref["abstract"] or abstract

        papers.append({
            "title": title,
            "authors": bib.get("author", "").strip(),
            "venue": bib.get("citation") or bib.get("venue", ""),
            "year": str(bib.get("pub_year", "")).strip(),
            "link": link,
            "abstract": abstract,
        })

    papers.sort(key=lambda p: p.get("year") or "", reverse=True)
    return papers


def main():
    # Google Scholar rate-limits/blocks scraping fairly often. If anything goes
    # wrong here, or it comes back empty, keep the existing papers.json as-is
    # rather than overwrite good data with an error or an empty list. Exit 0
    # either way so the scheduled workflow doesn't show a false failure.
    #
    # Try a direct connection first — it's fast and works fine outside CI.
    # Only pay the (slow, not-always-successful) cost of scanning free
    # proxies if the direct attempt actually gets blocked.
    try:
        papers = fetch_papers()
    except Exception as direct_exc:
        print(f"Direct Scholar fetch failed ({direct_exc}); trying a proxy")
        setup_proxy()
        try:
            papers = fetch_papers()
        except Exception as exc:
            print(f"Scholar fetch failed ({exc}); keeping existing {OUTPUT_PATH}")
            return

    if not papers:
        print(f"Scholar fetch returned no papers; keeping existing {OUTPUT_PATH}")
        return

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(papers, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(papers)} papers to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
