"""Fetch publications from a Google Scholar profile and write them to assets/data/papers.json.

Usage: python scripts/fetch_scholar.py
Requires: pip install scholarly
"""
import json
import pathlib

from scholarly import scholarly

SCHOLAR_USER_ID = "5Oi5SOEAAAAJ"
OUTPUT_PATH = pathlib.Path(__file__).resolve().parent.parent / "assets" / "data" / "papers.json"


def fetch_papers():
    author = scholarly.search_author_id(SCHOLAR_USER_ID)
    author = scholarly.fill(author, sections=["publications"])

    papers = []
    for pub in author.get("publications", []):
        bib = pub.get("bib", {})
        filled = scholarly.fill(pub)
        bib = filled.get("bib", bib)
        papers.append({
            "title": bib.get("title", "").strip(),
            "authors": bib.get("author", "").strip(),
            "venue": bib.get("citation") or bib.get("venue", ""),
            "year": bib.get("pub_year", ""),
            "link": filled.get("pub_url") or filled.get("eprint_url") or "",
            "abstract": bib.get("abstract", "").strip(),
        })

    papers.sort(key=lambda p: p.get("year") or "", reverse=True)
    return papers


def main():
    # Google Scholar rate-limits/blocks scraping fairly often. If anything goes
    # wrong here, or it comes back empty, keep the existing papers.json as-is
    # rather than overwrite good data with an error or an empty list. Exit 0
    # either way so the scheduled workflow doesn't show a false failure.
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
