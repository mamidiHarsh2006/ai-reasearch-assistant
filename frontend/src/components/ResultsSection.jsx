import { ArrowDownWideNarrow, SlidersHorizontal } from "lucide-react";
import { useMemo, useState } from "react";
import PaperCard from "./PaperCard.jsx";

const SOURCE_OPTIONS = ["All Sources", "OpenAlex", "arXiv", "IEEE"];

export default function ResultsSection({ result, onRetry }) {
  const [source, setSource] = useState("All Sources");
  const [sort, setSort] = useState("relevance");
  const papers = useMemo(() => {
    const filtered = source === "All Sources" ? [...result.papers] : result.papers.filter((paper) => paper.source === source);
    return filtered.sort((a, b) => {
      if (sort === "citations") return (b.citation_count || 0) - (a.citation_count || 0);
      if (sort === "newest") return (b.publication_year || 0) - (a.publication_year || 0);
      return b.final_score - a.final_score;
    });
  }, [result.papers, source, sort]);
  const sourceNames = Object.keys(result.sources || {});
  const failures = sourceNames.filter((name) => !result.sources[name].available);
  const responded = sourceNames.filter((name) => result.sources[name].available).length;

  return (
    <section className="results-section">
      <div className="results-heading-row">
        <div>
          <div className="eyebrow"><span className="eyebrow-line" /> YOUR DISCOVERIES</div>
          <h2>Top {result.papers.length || 5} Relevant Research Papers</h2>
        </div>
        <div className="results-count">{result.total_retrieved} found</div>
      </div>
      <p className="results-summary">
        Retrieved {result.total_retrieved} {result.total_retrieved === 1 ? "paper" : "papers"} from {responded} of 3 academic sources. Showing the top {result.papers.length} ranked papers.
      </p>
      <p className="ranking-note">
        Scores use {result.ranking_method === "sentence-transformers" ? "Sentence Transformers semantic similarity" : "keyword overlap (semantic model unavailable)"}, citation impact, and publication recency.
      </p>
      {failures.length > 0 && (
        <div className="partial-warning" role="status">
          <strong>Some sources were unavailable:</strong>{" "}
          {failures.map((name) => `${name}: ${result.sources[name].error || "request failed"}`).join(" · ")}
        </div>
      )}
      <div className="results-toolbar">
        <div className="filter-label"><SlidersHorizontal size={15} /> Filter by source</div>
        <div className="source-filters" role="group" aria-label="Filter papers by source">
          {SOURCE_OPTIONS.map((option) => (
            <button className={`filter-chip ${source === option ? "filter-chip-active" : ""}`} key={option} onClick={() => setSource(option)} type="button">{option}</button>
          ))}
        </div>
        <label className="sort-control">
          <ArrowDownWideNarrow size={15} />
          <span className="sr-only">Sort papers</span>
          <select onChange={(event) => setSort(event.target.value)} value={sort}>
            <option value="relevance">Highest relevance</option>
            <option value="citations">Most cited</option>
            <option value="newest">Newest first</option>
          </select>
        </label>
      </div>
      {result.papers.length === 0 ? (
        <div className="empty-filter">
          <strong>No papers found for this topic.</strong>
          <p>Try a broader query or use different keywords. Source status is shown above.</p>
          <button onClick={onRetry} type="button">Retry search</button>
        </div>
      ) : papers.length ? (
        <div className="paper-list">
          {papers.map((paper, index) => <PaperCard key={paper.paper_id} paper={paper} rank={index + 1} />)}
        </div>
      ) : (
        <div className="empty-filter">
          <p>No papers from {source} made the top results for this search.</p>
          <button onClick={() => setSource("All Sources")} type="button">View all results</button>
        </div>
      )}
    </section>
  );
}
