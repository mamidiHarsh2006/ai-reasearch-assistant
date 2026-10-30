from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable

from services import arxiv_service, ieee_service, openalex_service

SourceFunction = Callable[[list[str]], Awaitable[list[dict[str, Any]]]]


async def search_sources(
    queries: list[str],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    sources: dict[str, SourceFunction] = {
        "OpenAlex": openalex_service.search,
        "arXiv": arxiv_service.search,
        "IEEE": ieee_service.search,
    }

    async def retrieve(
        name: str, search: SourceFunction
    ) -> tuple[str, list[dict[str, Any]], str | None]:
        try:
            return name, await search(queries), None
        except Exception as exc:
            return name, [], _source_error(exc)

    responses = await asyncio.gather(
        *(retrieve(name, search) for name, search in sources.items())
    )
    papers: list[dict[str, Any]] = []
    status: dict[str, dict[str, Any]] = {}
    for name, results, error in responses:
        papers.extend(results)
        status[name] = {
            "available": error is None,
            "retrieved": len(results),
            "error": error,
        }
    return papers, status


def _source_error(exc: Exception) -> str:
    message = str(exc).strip()
    return message[:240] if message else f"{type(exc).__name__} while querying source."
