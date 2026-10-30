from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from agents.planner_agent import plan_research
from agents.ranking_agent import rank_papers, ranking_method
from agents.search_agent import search_sources
from models.paper import ResearchRequest, ResearchResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(title="ResearchAI API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/research", response_model=ResearchResponse)
async def research(request: ResearchRequest) -> ResearchResponse:
    plan = plan_research(request.query)

    try:
        collected, source_status = await search_sources(plan.search_queries)
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504, detail="The academic sources did not respond in time."
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail="Unable to complete the research search."
        ) from exc

    unique_papers = _deduplicate(collected)
    ranked = rank_papers(unique_papers, plan.research_topic)
    return ResearchResponse(
        query=request.query,
        research_topic=plan.research_topic,
        expanded_keywords=plan.expanded_keywords,
        search_queries=plan.search_queries,
        total_retrieved=len(unique_papers),
        papers=ranked[: request.limit],
        sources=source_status,
        ranking_method=ranking_method(),
    )


def _deduplicate(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen_dois: set[str] = set()
    seen_titles: set[str] = set()
    unique: list[dict[str, Any]] = []

    for paper in papers:
        doi = (paper.get("doi") or "").strip().lower().removeprefix("https://doi.org/")
        title = " ".join((paper.get("title") or "").casefold().split())
        if (doi and doi in seen_dois) or (title and title in seen_titles):
            continue
        if doi:
            seen_dois.add(doi)
        if title:
            seen_titles.add(title)
        unique.append(paper)
    return unique
