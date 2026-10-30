import { ArrowUpRight, BookOpen, Download, Quote } from "lucide-react";
import { useState } from "react";

const sourceClasses = { OpenAlex: "source-openalex", "arXiv": "source-arxiv", IEEE: "source-ieee" };

export default function PaperCard({ paper, rank }) {
  const [expanded, setExpanded] = useState(false);
  const abstract = paper.abstract || "No abstract was provided by this source.";
  const longAbstract = abstract.length > 260;
  return (
    <article className="paper-card">
      <div className="paper-rank">#{rank}</div>
      <div className="paper-main">
        <div className="paper-meta-top">
          <span className={`source-badge ${sourceClasses[paper.source] || "source-openalex"}`}>
            <span className="source-dot" />{paper.source}
          </span>
          {paper.publication_year && <span className="paper-year">{paper.publication_year}</span>}
          {paper.publication_venue && <span className="paper-venue">{paper.publication_venue}</span>}
        </div>
        <h3 className="paper-title">{paper.title}</h3>
        <p className="paper-authors">
          {paper.authors?.length ? paper.authors.slice(0, 5).join(", ") : "Authors not listed"}
          {paper.authors?.length > 5 ? ` +${paper.authors.length - 5} more` : ""}
        </p>
        <p className="paper-abstract">
          {longAbstract && !expanded ? `${abstract.slice(0, 260).trimEnd()}…` : abstract}
          {longAbstract && (
            <button className="read-more" onClick={() => setExpanded(!expanded)} type="button">
              {expanded ? " Show less" : " Read more"}
            </button>
          )}
        </p>
        <div className="paper-footer">
          <div className="paper-stats">
            <span><Quote size={14} /> {paper.citation_count == null ? "Citations n/a" : `${paper.citation_count.toLocaleString()} citations`}</span>
            <span><BookOpen size={14} /> {Math.round(paper.relevance_score)}% relevance</span>
            <span>{Math.round(paper.citation_score)}% citation impact</span>
            <span>{Math.round(paper.recency_score)}% recency</span>
            <span className="overall-score">{Math.round(paper.final_score)} <small>score</small></span>
          </div>
          <div className="paper-actions">
            {paper.doi && <a className="doi-link" href={`https://doi.org/${paper.doi.replace(/^https?:\/\/doi\.org\//i, "")}`} rel="noreferrer" target="_blank">DOI</a>}
            {paper.pdf_url && <a className="paper-button paper-button-secondary" href={paper.pdf_url} rel="noreferrer" target="_blank"><Download size={14} /> PDF</a>}
            {paper.paper_url && <a className="paper-button" href={paper.paper_url} rel="noreferrer" target="_blank">View paper <ArrowUpRight size={14} /></a>}
          </div>
        </div>
      </div>
    </article>
  );
}
