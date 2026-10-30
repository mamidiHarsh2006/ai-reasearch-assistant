from __future__ import annotations

import asyncio
import os
from typing import Any

import httpx

API_URL = "https://api.openalex.org/works"
RESULTS_PER_QUERY = 5


async def search(queries: list[str]) -> list[dict[str, Any]]:
    headers = {"User-Agent": "ResearchAI/1.0"}
    mailto = os.getenv("OPENALEX_MAILTO")
    if mailto:
        headers["User-Agent"] = f"ResearchAI/1.0 (mailto:{mailto})"
    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        results = await asyncio.gather(
            *( _search_query(client, query) for query in queries),
            return_exceptions=True,
        )
    papers: list[dict[str, Any]] = []
    errors = []
    for result in results:
        if isinstance(result, Exception):
            errors.append(result)
        else:
            papers.extend(result)
    if not papers and errors:
        raise errors[0]
    return _unique(papers)[:RESULTS_PER_QUERY]


async def _search_query(client: httpx.AsyncClient, query: str) -> list[dict[str, Any]]:
    response = await client.get(
        API_URL,
        params={
            "search": query,
            "per-page": RESULTS_PER_QUERY,
            "select": (
                "id,doi,title,authorships,abstract_inverted_index,publication_year,"
                "cited_by_count,primary_location,biblio"
            ),
        },
    )
    response.raise_for_status()
    records = response.json().get("results", [])
    return [_normalize(record) for record in records if record.get("title")]


def _normalize(record: dict[str, Any]) -> dict[str, Any]:
    location = record.get("primary_location") or {}
    source = location.get("source") or {}
    landing_page = location.get("landing_page_url")
    doi = record.get("doi")
    return {
        "paper_id": record.get("id") or doi or record.get("title"),
        "title": record.get("title"),
        "authors": [
            author.get("author", {}).get("display_name")
            for author in record.get("authorships", [])
            if author.get("author", {}).get("display_name")
        ],
        "abstract": _abstract(record.get("abstract_inverted_index")),
        "publication_year": record.get("publication_year"),
        "citation_count": record.get("cited_by_count"),
        "doi": doi,
        "source": "OpenAlex",
        "publication_venue": source.get("display_name"),
        "paper_url": landing_page or record.get("id"),
        "pdf_url": (location.get("pdf_url")),
    }


def _abstract(inverted_index: dict[str, list[int]] | None) -> str | None:
    if not inverted_index:
        return None
    words = sorted(
        (position, word)
        for word, positions in inverted_index.items()
        for position in positions
    )
    return " ".join(word for _, word in words) or None


def _unique(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique = []
    for paper in papers:
        key = (paper.get("doi") or paper.get("title") or "").casefold()
        if key and key not in seen:
            seen.add(key)
            unique.append(paper)
    return unique
