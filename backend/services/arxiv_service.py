from __future__ import annotations

import asyncio
import re
import xml.etree.ElementTree as ET
from typing import Any
import httpx

API_URL = "https://export.arxiv.org/api/query"
NAMESPACE = {"atom": "http://www.w3.org/2005/Atom"}
ARXIV_NAMESPACE = "http://arxiv.org/schemas/atom"
RESULTS_PER_QUERY = 5


async def search(queries: list[str]) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=25) as client:
        results = await asyncio.gather(
            *(_search_query(client, query) for query in queries),
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
            "search_query": f'all:"{query}"',
            "start": 0,
            "max_results": RESULTS_PER_QUERY,
            "sortBy": "relevance",
        },
    )
    response.raise_for_status()
    root = ET.fromstring(response.text)
    return [_normalize(entry) for entry in root.findall("atom:entry", NAMESPACE)]


def _normalize(entry: ET.Element) -> dict[str, Any]:
    links = entry.findall("atom:link", NAMESPACE)
    paper_url = _text(entry, "atom:id")
    pdf_link = next(
        (
            link.get("href")
            for link in links
            if link.get("title") == "pdf" or link.get("type") == "application/pdf"
        ),
        None,
    )
    published = _text(entry, "atom:published")
    year_match = re.match(r"(\d{4})", published or "")
    doi_node = entry.find(f"{{{ARXIV_NAMESPACE}}}doi")
    venue_node = entry.find(f"{{{ARXIV_NAMESPACE}}}journal_ref")
    return {
        "paper_id": paper_url,
        "title": " ".join((_text(entry, "atom:title") or "").split()),
        "authors": [
            name
            for author in entry.findall("atom:author", NAMESPACE)
            if (name := _text(author, "atom:name"))
        ],
        "abstract": " ".join((_text(entry, "atom:summary") or "").split()) or None,
        "publication_year": int(year_match.group(1)) if year_match else None,
        "citation_count": None,
        "doi": doi_node.text.strip() if doi_node is not None and doi_node.text else None,
        "source": "arXiv",
        "publication_venue": venue_node.text.strip() if venue_node is not None and venue_node.text else None,
        "paper_url": paper_url,
        "pdf_url": pdf_link,
    }


def _text(element: ET.Element, path: str) -> str | None:
    child = element.find(path, NAMESPACE)
    return child.text.strip() if child is not None and child.text else None


def _unique(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique = []
    for paper in papers:
        key = (paper.get("doi") or paper.get("paper_id") or paper.get("title") or "").casefold()
        if key and key not in seen:
            seen.add(key)
            unique.append(paper)
    return unique
