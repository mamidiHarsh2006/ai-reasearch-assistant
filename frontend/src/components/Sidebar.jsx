import {
  Bookmark,
  FlaskConical,
  History,
  Info,
  Plus,
  Sparkles,
} from "lucide-react";

const items = [
  { label: "New Research", icon: Plus, action: "new" },
  { label: "Research History", icon: History, action: "history" },
  { label: "Saved Papers", icon: Bookmark, action: "saved" },
];

export default function Sidebar({ onAction }) {
  return (
    <aside className="sidebar">
      <a className="brand-lockup" href="#" onClick={(event) => event.preventDefault()}>
        <span className="brand-mark"><FlaskConical size={19} /></span>
        <span className="brand-name">Research<span>AI</span></span>
      </a>
      <div className="sidebar-label">WORKSPACE</div>
      <nav className="sidebar-nav" aria-label="Main navigation">
        {items.map(({ label, icon: Icon, action }, index) => (
          <button
            className={`nav-item ${index === 0 ? "nav-item-active" : ""}`}
            key={action}
            onClick={() => onAction(action)}
            type="button"
          >
            <Icon size={17} strokeWidth={1.8} />
            <span>{label}</span>
            {action === "new" && <span className="nav-shortcut">⌘ K</span>}
          </button>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <div className="sidebar-promo">
          <span className="promo-icon"><Sparkles size={16} /></span>
          <strong>Research, reimagined.</strong>
          <p>Find the work that moves your ideas forward.</p>
        </div>
        <button className="nav-item about-link" onClick={() => onAction("about")} type="button">
          <Info size={17} strokeWidth={1.8} />
          <span>About Project</span>
        </button>
        <div className="sidebar-footnote">BUILT FOR CURIOUS MINDS</div>
      </div>
    </aside>
  );
}
