from __future__ import annotations

import re
from dataclasses import dataclass

STOP_WORDS = {
    "a", "an", "and", "are", "for", "from", "in", "into", "of", "on", "or",
    "the", "to", "using", "with", "by", "based", "research", "study",
}

ALIASES = {
    "ai": "artificial intelligence",
    "artificial intelligence": "AI",
    "dl": "deep learning",
    "deep learning": "neural networks",
    "ml": "machine learning",
    "machine learning": "ML",
    "nlp": "natural language processing",
    "natural language processing": "NLP",
}


@dataclass(frozen=True)
class ResearchPlan:
    research_topic: str
    expanded_keywords: list[str]
    search_queries: list[str]


def plan_research(query: str) -> ResearchPlan:
    topic = " ".join(query.split())
    words = re.findall(r"[\w'-]+", topic.casefold())
    keywords = [word for word in words if word not in STOP_WORDS and len(word) > 1]

    expanded = list(dict.fromkeys(keywords))
    for phrase, alias in ALIASES.items():
        if re.search(r"\b" + re.escape(phrase) + r"\b", topic.casefold()):
            expanded.append(alias)
    expanded_keywords = list(dict.fromkeys(expanded))[:12]

    queries = [topic]
    if expanded_keywords:
        keyword_query = " ".join(expanded_keywords[:8])
        if keyword_query.casefold() != topic.casefold():
            queries.append(keyword_query)
    return ResearchPlan(
        research_topic=topic,
        expanded_keywords=expanded_keywords,
        search_queries=queries[:3],
    )
