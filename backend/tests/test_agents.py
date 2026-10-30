import unittest
from unittest.mock import patch

from agents.planner_agent import plan_research
from agents.ranking_agent import rank_papers
from main import _deduplicate


class ResearchAgentTests(unittest.TestCase):
    def test_planner_keeps_topic_and_expands_known_synonym(self):
        plan = plan_research("Deep learning for deepfake detection")

        self.assertEqual(plan.research_topic, "Deep learning for deepfake detection")
        self.assertIn("neural networks", plan.expanded_keywords)
        self.assertEqual(plan.search_queries[0], plan.research_topic)
        self.assertTrue(any("neural networks" in query for query in plan.search_queries))

    def test_ranking_applies_all_three_scores(self):
        papers = [
            {
                "title": "Deep learning research",
                "abstract": "Deep learning detects deepfakes",
                "citation_count": 100,
                "publication_year": 2025,
            },
            {
                "title": "Unrelated astronomy paper",
                "abstract": "Observations of distant galaxies",
                "citation_count": None,
                "publication_year": 2015,
            },
        ]

        with patch("agents.ranking_agent._load_encoder", return_value=None):
            ranked = rank_papers(papers, "deep learning deepfake detection")

        self.assertEqual(ranked[0]["title"], "Deep learning research")
        self.assertIn("relevance_score", ranked[0])
        self.assertIn("citation_score", ranked[0])
        self.assertIn("recency_score", ranked[0])
        self.assertIn("final_score", ranked[0])
        self.assertEqual(ranked[1]["citation_score"], 0)

    def test_deduplication_uses_doi_then_normalized_title(self):
        papers = [
            {"title": "A Paper", "doi": "https://doi.org/10.1/example"},
            {"title": "Another title", "doi": "https://doi.org/10.1/example"},
            {"title": " a   paper ", "doi": None},
            {"title": "Unique work", "doi": None},
        ]

        self.assertEqual(len(_deduplicate(papers)), 2)


if __name__ == "__main__":
    unittest.main()
