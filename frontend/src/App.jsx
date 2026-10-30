import { AlertCircle, ArrowRight, BookOpen, CircleHelp, FileSearch, RotateCw, ShieldCheck, X } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import SearchBar, { EXAMPLES } from "./components/SearchBar.jsx";
import SearchStrategy from "./components/SearchStrategy.jsx";
import ResultsSection from "./components/ResultsSection.jsx";
import { research } from "./services/researchApi.js";

export default function App() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [aboutOpen, setAboutOpen] = useState(false);

  const runSearch = useCallback(async (value = query) => {
    const clean = value.trim();
    if (clean.length < 3 || busy) return;
    setQuery(clean);
    setBusy(true);
    setError("");
    setNotice("");
    setResult(null);
    try {
      setResult(await research(clean));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The search could not be completed.");
    } finally {
      setBusy(false);
    }
  }, [busy, query]);

  const reset = useCallback(() => {
    setQuery("");
    setResult(null);
    setError("");
    setNotice("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  useEffect(() => {
    function onKeyDown(event) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        reset();
        document.querySelector("textarea[aria-label='Research topic']")?.focus();
      }
      if (event.key === "Escape") setAboutOpen(false);
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [reset]);

  function handleSidebarAction(action) {
    if (action === "new") return reset();
    if (action === "about") return setAboutOpen(true);
    setNotice(action === "history"
      ? "Research history is not available in this MVP. Your searches are not stored."
      : "Saved papers are not available in this MVP.");
  }

  return (
    <div className="app-shell">
      <Sidebar onAction={handleSidebarAction} />
      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb"><span>Workspace</span><span className="breadcrumb-slash">/</span><strong>New research</strong></div>
          <div className="topbar-right"><span className="secure-label"><ShieldCheck size={14} /> Academic sources</span><span className="avatar">R</span></div>
        </header>
        <div className="content">
          <section className={`hero ${result ? "hero-compact" : ""}`}>
            <div className="hero-kicker"><span className="kicker-star">✳</span> YOUR PERSONAL LITERATURE SCOUT</div>
            <h1>Your AI Research<br className="hero-break" /> Assistant<span className="title-period">.</span></h1>
            <p className="hero-subtitle">Discover research papers, explore scientific literature, and<br className="desktop-break" /> uncover research opportunities with AI.</p>
            <SearchBar
              busy={busy}
              onChange={setQuery}
              onExample={(example) => { setQuery(example); runSearch(example); }}
              onSubmit={(event) => { event.preventDefault(); runSearch(); }}
              query={query}
            />
            {busy && (
              <div className="loading-panel" role="status">
                <span className="loader" />
                <span><strong>Scanning the literature</strong><small>Searching OpenAlex, arXiv, and IEEE</small></span>
                <div className="loading-dots"><i /><i /><i /></div>
              </div>
            )}
            {error && !busy && (
              <div className="error-panel" role="alert">
                <span className="error-icon"><AlertCircle size={18} /></span>
                <div><strong>We couldn’t complete that search</strong><p>{error}</p></div>
                <button className="retry-button" onClick={() => runSearch()} type="button"><RotateCw size={14} /> Retry</button>
              </div>
            )}
            {notice && <div className="notice-panel"><CircleHelp size={16} />{notice}<button onClick={() => setNotice("")} aria-label="Dismiss" type="button"><X size={14} /></button></div>}
          </section>

          {!result && !busy && !error && (
            <section className="welcome-grid" aria-label="Research assistant capabilities">
              <div className="welcome-card welcome-card-large">
                <span className="welcome-icon welcome-icon-lilac"><FileSearch size={19} /></span>
                <span className="welcome-overline">START WITH A QUESTION</span>
                <h2>Good research starts<br />with a better search.</h2>
                <p>Tell us what you’re exploring. We’ll search trusted scholarly indexes and surface the most relevant work.</p>
                <span className="welcome-arrow"><ArrowRight size={16} /></span>
              </div>
              <div className="welcome-card welcome-card-source">
                <span className="welcome-icon welcome-icon-blue"><BookOpen size={18} /></span>
                <span className="welcome-overline">ONE SEARCH, THREE SOURCES</span>
                <h3>Literature, brought together.</h3>
                <div className="source-pills"><span className="source-badge source-openalex"><i className="source-dot" />OpenAlex</span><span className="source-badge source-arxiv"><i className="source-dot" />arXiv</span><span className="source-badge source-ieee"><i className="source-dot" />IEEE</span></div>
              </div>
              <div className="welcome-note"><span className="note-line" /><span>Real papers. Transparent sources. Ranked for relevance.</span></div>
            </section>
          )}

          {result && !busy && (
            <div className="results-content">
              <SearchStrategy result={result} />
              <ResultsSection onRetry={() => runSearch()} result={result} />
            </div>
          )}
          <footer className="main-footer"><span>ResearchAI <span className="footer-dot">·</span> Literature discovery, thoughtfully designed.</span><span>Results sourced from scholarly databases</span></footer>
        </div>
      </main>
      {aboutOpen && (
        <div className="modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setAboutOpen(false); }}>
          <section aria-labelledby="about-title" aria-modal="true" className="about-modal" role="dialog">
            <button aria-label="Close dialog" className="modal-close" onClick={() => setAboutOpen(false)} type="button"><X size={18} /></button>
            <span className="about-icon"><BookOpen size={19} /></span>
            <div className="eyebrow">ABOUT THIS PROJECT</div>
            <h2 id="about-title">Research starts with discovery.</h2>
            <p>ResearchAI is an MVP for scientific literature analysis. It searches OpenAlex, arXiv, and IEEE Xplore, removes duplicate records, and ranks available papers by relevance, citation impact, and recency.</p>
            <div className="about-disclaimer">Search results depend on source availability and API access. IEEE results require a server-side API key. This tool does not generate or invent papers.</div>
            <button className="modal-done" onClick={() => setAboutOpen(false)} type="button">Got it</button>
          </section>
        </div>
      )}
    </div>
  );
}
