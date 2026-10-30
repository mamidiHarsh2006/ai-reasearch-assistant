import { ArrowUp, Sparkles } from "lucide-react";

export const EXAMPLES = [
  "Deep learning for deepfake detection",
  "Explainable AI in medical diagnosis",
  "Graph neural networks for drug discovery",
];

export default function SearchBar({ query, onChange, onSubmit, busy, onExample }) {
  return (
    <div className="search-wrap">
      <form className="search-box" onSubmit={onSubmit}>
        <textarea
          aria-label="Research topic"
          autoComplete="off"
          maxLength={500}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              onSubmit(event);
            }
          }}
          placeholder="Enter your research topic... e.g., Deep Learning for Deepfake Detection"
          rows={2}
          value={query}
        />
        <div className="search-box-footer">
          <span className="search-hint"><Sparkles size={14} /> Search across academic literature</span>
          <button className="search-submit" disabled={busy || query.trim().length < 3} type="submit">
            {busy ? "Searching..." : "Search papers"}
            <span className="submit-icon"><ArrowUp size={15} /></span>
          </button>
        </div>
      </form>
      <div className="examples">
        <span className="examples-label">TRY</span>
        {EXAMPLES.map((example) => (
          <button className="example-chip" key={example} onClick={() => onExample(example)} type="button">
            {example}
          </button>
        ))}
      </div>
    </div>
  );
}
