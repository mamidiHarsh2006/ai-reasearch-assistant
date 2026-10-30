from __future__ import annotations

import asyncio
import os
from typing import Any

import httpx

API_URL = "https://ieeexploreapi.ieee.org/api/v1/search/articles"
RESULTS_PER_QUERY = 5


async def search(queries: list[str]) -> list[dict[str, Any]]:
    api_key = os.getenv("IEEE_API_KEY")
    if not api_key:
        raise RuntimeError("IEEE retrieval unavailable: IEEE_API_KEY is not configured.")

    async with httpx.AsyncClient(timeout=20) as client:
        results = await asyncio.gather(
            *(_search_query(client, api_key, query) for query in queries),
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


async def _search_query(
    client: httpx.AsyncClient, api_key: str, query: str
) -> list[dict[str, Any]]:
    response = await client.get(
        API_URL,
        params={
            "apikey": api_key,
            "format": "json",
            "max_records": RESULTS_PER_QUERY,
            "start_record": 1,
            "sort_order": "asc",
            "sort_field": "relevance",
            "querytext": query,
        },
    )
    response.raise_for_status()
    payload = response.json()
    return [
        _normalize(record)
        for record in payload.get("articles", [])
        if record.get("title")
    ]


def _normalize(record: dict[str, Any]) -> dict[str, Any]:
    authors_data = record.get("authors") or {}
    authors = authors_data.get("authors", []) if isinstance(authors_data, dict) else []
    doi = record.get("doi")
    return {
        "paper_id": str(record.get("article_number") or doi or record.get("title")),
        "title": record.get("title"),
        "authors": [
            author.get("full_name") or author.get("name")
            for author in authors
            if author.get("full_name") or author.get("name")
        ],
        "abstract": record.get("abstract"),
        "publication_year": _year(record.get("publication_year")),
        "citation_count": _integer(record.get("citing_paper_count")),
        "doi": doi,
        "source": "IEEE",
        "publication_venue": record.get("publication_title"),
        "paper_url": record.get("html_url") or record.get("pdf_url"),
        "pdf_url": record.get("pdf_url"),
    }


def _year(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _integer(value: Any) -> int | None:
    return _year(value)


def _unique(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique = []
    for paper in papers:
        key = (paper.get("doi") or paper.get("title") or "").casefold()
        if key and key not in seen:
            seen.add(key)
            unique.append(paper)
    return unique
