from __future__ import annotations

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)
    limit: int = Field(default=5, ge=1, le=25)


class Paper(BaseModel):
    paper_id: str
    title: str
    authors: list[str] = Field(default_factory=list)
    abstract: str | None = None
    publication_year: int | None = None
    citation_count: int | None = None
    doi: str | None = None
    source: str
    publication_venue: str | None = None
    paper_url: str | None = None
    pdf_url: str | None = None
    relevance_score: float
    citation_score: float
    recency_score: float
    final_score: float


class SourceStatus(BaseModel):
    available: bool
    retrieved: int
    error: str | None = None


class ResearchResponse(BaseModel):
    query: str
    research_topic: str
    expanded_keywords: list[str]
    search_queries: list[str]
    total_retrieved: int
    papers: list[Paper]
    sources: dict[str, SourceStatus]
    ranking_method: str
