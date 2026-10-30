import { ChevronDown, Crosshair, Search, Sparkles } from "lucide-react";

export default function SearchStrategy({ result }) {
  return (
    <details className="strategy-card">
      <summary>
        <span className="strategy-icon"><Sparkles size={16} /></span>
        <span className="strategy-heading">
          <strong>AI Search Strategy</strong>
          <small>See how your research topic was interpreted</small>
        </span>
        <ChevronDown className="strategy-chevron" size={18} />
      </summary>
      <div className="strategy-content">
        <div className="strategy-block">
          <div className="strategy-caption"><Crosshair size={14} /> RESEARCH TOPIC</div>
          <p>{result.research_topic}</p>
        </div>
        <div className="strategy-block">
          <div className="strategy-caption"><Sparkles size={14} /> EXPANDED KEYWORDS</div>
          <div className="keyword-list">
            {result.expanded_keywords.map((keyword) => <span className="keyword" key={keyword}>{keyword}</span>)}
          </div>
        </div>
        <div className="strategy-block">
          <div className="strategy-caption"><Search size={14} /> GENERATED SEARCH QUERIES</div>
          <ul className="query-list">
            {result.search_queries.map((query) => <li key={query}>{query}</li>)}
          </ul>
        </div>
      </div>
    </details>
  );
}
