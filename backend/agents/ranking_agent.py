from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Any

_encoder: Any = None
_encoder_attempted = False
_last_ranking_method = "keyword-overlap"


def rank_papers(
    papers: list[dict[str, Any]], research_topic: str
) -> list[dict[str, Any]]:
    relevance, _ = _semantic_scores(papers, research_topic)
    max_citations = max(
        (paper.get("citation_count") or 0 for paper in papers), default=0
    )
    current_year = datetime.now(timezone.utc).year

    for paper, relevance_score in zip(papers, relevance):
        citations = paper.get("citation_count")
        citation_score = (
            100 * math.log1p(max(0, citations)) / math.log1p(max_citations)
            if citations is not None and max_citations > 0
            else 0.0
        )
        year = paper.get("publication_year")
        recency_score = (
            max(0.0, min(100.0, (year - (current_year - 10)) * 10))
            if year is not None
            else 0.0
        )
        paper["relevance_score"] = round(relevance_score, 2)
        paper["citation_score"] = round(citation_score, 2)
        paper["recency_score"] = round(recency_score, 2)
        paper["final_score"] = round(
            0.60 * relevance_score + 0.25 * citation_score + 0.15 * recency_score,
            2,
        )

    return sorted(papers, key=lambda paper: paper["final_score"], reverse=True)


def _semantic_scores(
    papers: list[dict[str, Any]], research_topic: str
) -> tuple[list[float], str]:
    global _last_ranking_method
    if not papers:
        _last_ranking_method = "keyword-overlap"
        return [], _last_ranking_method
    encoder = _load_encoder()
    texts = [
        f"{paper.get('title') or ''}. {paper.get('abstract') or ''}" for paper in papers
    ]
    if encoder is not None and texts:
        try:
            import numpy as np

            embeddings = encoder.encode([research_topic, *texts], normalize_embeddings=True)
            query_vector = embeddings[0]
            scores = [
                float(np.clip(np.dot(query_vector, vector), 0.0, 1.0) * 100)
                for vector in embeddings[1:]
            ]
            _last_ranking_method = "sentence-transformers"
            return scores, _last_ranking_method
        except Exception:
            pass

    query_tokens = set(_tokens(research_topic))
    scores = [
        100 * len(query_tokens.intersection(_tokens(text))) / len(query_tokens)
        if query_tokens
        else 0.0
        for text in texts
    ]
    _last_ranking_method = "keyword-overlap"
    return scores, _last_ranking_method


def _load_encoder() -> Any:
    global _encoder, _encoder_attempted
    if _encoder_attempted:
        return _encoder
    _encoder_attempted = True
    try:
        from sentence_transformers import SentenceTransformer

        _encoder = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        _encoder = None
    return _encoder


def ranking_method() -> str:
    return _last_ranking_method


def _tokens(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[\w'-]+", text.casefold())
        if len(token) > 2
    ]
