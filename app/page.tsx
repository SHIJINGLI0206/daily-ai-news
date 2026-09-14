"use client";

import { useMemo, useState } from "react";
import {
  ArrowUpRight,
  Bookmark,
  ChevronDown,
  CircleHelp,
  Clock3,
  ExternalLink,
  FileText,
  Flame,
  Github,
  Headphones,
  LayoutDashboard,
  Library,
  Menu,
  Play,
  Radio,
  Search,
  Settings2,
  Sparkles,
  Star,
  Tags,
  TrendingUp,
  Users,
  X,
  Zap,
} from "lucide-react";
import { hotModels, hotPapers, media, risingRepos, topics, trends } from "@/lib/seed-data";
import type { TrendCategory } from "@/lib/types";

const navItems = [
  { label: "Today", icon: LayoutDashboard },
  { label: "Models", icon: Sparkles },
  { label: "Papers", icon: FileText },
  { label: "GitHub", icon: Github },
  { label: "Media", icon: Headphones },
];

const utilityItems = [
  { label: "Topics", icon: Tags },
  { label: "Saved", icon: Bookmark },
  { label: "History", icon: Clock3 },
];

const categories: Array<"All" | TrendCategory> = ["All", "Agents", "Models", "Infrastructure", "Research", "Creative"];

function IconButton({ label, active, children, onClick }: { label: string; active?: boolean; children: React.ReactNode; onClick?: () => void }) {
  return <button aria-label={label} className={`icon-button ${active ? "icon-button-active" : ""}`} onClick={onClick}>{children}</button>;
}

function Sidebar({ active, setActive, savedCount, mobileOpen, closeMobile }: { active: string; setActive: (item: string) => void; savedCount: number; mobileOpen: boolean; closeMobile: () => void }) {
  return (
    <aside className={`sidebar ${mobileOpen ? "sidebar-open" : ""}`}>
      <div className="sidebar-brand">
        <div className="brand-mark"><Radio size={16} strokeWidth={2.5} /></div>
        <span>AI Radar</span>
        <button className="mobile-close" onClick={closeMobile} aria-label="Close menu"><X size={16} /></button>
      </div>

      <div className="workspace-switcher">
        <div className="workspace-avatar">J</div>
        <div><strong>Personal radar</strong><span>Daily workspace</span></div>
        <ChevronDown size={14} className="muted-icon" />
      </div>

      <div className="nav-section-label">Monitor</div>
      <nav className="nav-list" aria-label="Primary navigation">
        {navItems.map(({ label, icon: NavIcon }) => (
          <button key={label} className={`nav-item ${active === label ? "nav-item-active" : ""}`} onClick={() => { setActive(label); closeMobile(); }}>
            <NavIcon size={16} /><span>{label}</span>{label === "Today" && <span className="nav-pulse" />}
          </button>
        ))}
      </nav>

      <div className="nav-section-label nav-label-spaced">Library</div>
      <nav className="nav-list" aria-label="Library navigation">
        {utilityItems.map(({ label, icon: NavIcon }) => (
          <button key={label} className={`nav-item ${active === label ? "nav-item-active" : ""}`} onClick={() => { setActive(label); closeMobile(); }}>
            <NavIcon size={16} /><span>{label}</span>{label === "Saved" && savedCount > 0 && <span className="nav-count">{savedCount}</span>}
          </button>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="coverage-card">
          <div className="coverage-icon"><Zap size={14} /></div>
          <div><strong>Daily coverage</strong><span>8 signals · 32 sources</span></div>
          <span className="live-dot" />
        </div>
        <button className="nav-item"><Settings2 size={16} /><span>Settings</span></button>
        <button className="nav-item"><CircleHelp size={16} /><span>Help center</span></button>
        <div className="sidebar-footer"><span className="status-dot" />Synced just now <span className="version">v0.1</span></div>
      </div>
    </aside>
  );
}

function TrendCard({ trend, saved, onSave }: { trend: typeof trends[number]; saved: boolean; onSave: () => void }) {
  return (
    <article className="trend-card">
      <div className="trend-rank">{String(trend.rank).padStart(2, "0")}</div>
      <div className="trend-main">
        <div className="trend-card-topline"><span className={`source-badge ${trend.sourceKind.toLowerCase().replace(" ", "-")}`}>{trend.sourceKind}</span><span className="published">{trend.published}</span></div>
        <a className="trend-title" href={trend.href} target="_blank" rel="noreferrer">{trend.title}<ExternalLink size={14} /></a>
        <p className="trend-summary">{trend.summary}</p>
        <div className="trend-footer"><span className="signal-label"><TrendingUp size={13} /> {trend.signal}</span><div className="tag-list">{trend.tags.map((tag) => <span key={tag}>{tag}</span>)}</div></div>
      </div>
      <div className="trend-score-wrap"><span className="score-label">signal</span><strong>{trend.score}</strong><div className="score-track"><span style={{ width: `${trend.score}%` }} /></div><IconButton label={saved ? "Remove bookmark" : "Save trend"} active={saved} onClick={onSave}><Bookmark size={15} fill={saved ? "currentColor" : "none"} /></IconButton></div>
    </article>
  );
}

export default function Home() {
  const [activeNav, setActiveNav] = useState("Today");
  const [selectedCategory, setSelectedCategory] = useState<"All" | TrendCategory>("All");
  const [query, setQuery] = useState("");
  const [saved, setSaved] = useState<string[]>([]);
  const [mobileOpen, setMobileOpen] = useState(false);
  const filteredTrends = useMemo(() => trends.filter((trend) => {
    const categoryMatch = selectedCategory === "All" || trend.category === selectedCategory;
    const queryMatch = !query || `${trend.title} ${trend.summary} ${trend.tags.join(" ")}`.toLowerCase().includes(query.toLowerCase());
    return categoryMatch && queryMatch;
  }), [query, selectedCategory]);

  const toggleSave = (id: string) => setSaved((items) => items.includes(id) ? items.filter((item) => item !== id) : [...items, id]);

  return (
    <div className="app-shell">
      <Sidebar active={activeNav} setActive={setActiveNav} savedCount={saved.length} mobileOpen={mobileOpen} closeMobile={() => setMobileOpen(false)} />
      {mobileOpen && <button className="mobile-scrim" onClick={() => setMobileOpen(false)} aria-label="Close navigation" />}

      <main className="main-content">
        <header className="topbar">
          <button className="mobile-menu" onClick={() => setMobileOpen(true)} aria-label="Open menu"><Menu size={19} /></button>
          <div className="breadcrumb"><span>Workspace</span><span className="breadcrumb-separator">/</span><strong>{activeNav === "Today" ? "Today’s radar" : activeNav}</strong></div>
          <div className="topbar-actions">
            <label className="global-search"><Search size={16} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search the radar" /><kbd>⌘ K</kbd></label>
            <span className="topbar-divider" /><button className="date-button"><Clock3 size={15} /> Sep 14, 2026 <ChevronDown size={14} /></button><div className="user-avatar">JS</div>
          </div>
        </header>

        <div className="content-wrap">
          <section className="hero-section">
            <div><div className="eyebrow"><span className="eyebrow-dot" /> Monday, September 14, 2026 <span className="eyebrow-divider" /> Edition 04</div><h1>Good morning, Jing.<br /><em>Here’s what moved.</em></h1><p className="hero-copy">The AI landscape is shifting from model launches to the systems around them. Here are today’s clearest signals — ranked, condensed, and ready to explore.</p></div>
            <div className="hero-meta"><div className="meta-avatar-stack"><span>O</span><span>A</span><span>G</span><span>H</span></div><span>Curated from <strong>32 sources</strong></span><span className="meta-divider" /><span>Updated 08:42</span></div>
          </section>

          <section className="metric-grid" aria-label="Daily overview">
            <div className="metric-card metric-highlight"><div className="metric-icon"><Flame size={16} /></div><div><span>Signals today</span><strong>08</strong><small><b>+3</b> vs yesterday</small></div><div className="mini-bars"><i /><i /><i /><i /><i /><i /></div></div>
            <div className="metric-card"><div className="metric-icon cyan"><Sparkles size={16} /></div><div><span>Hot models</span><strong>12</strong><small><b>+18%</b> momentum</small></div><div className="metric-line"><i /><i /><i /><i /><i /><i /><i /><i /></div></div>
            <div className="metric-card"><div className="metric-icon violet"><FileText size={16} /></div><div><span>Research cuts</span><strong>04</strong><small><b>2</b> worth a deep read</small></div><div className="metric-ring"><span>68%</span></div></div>
            <div className="metric-card"><div className="metric-icon lime"><Users size={16} /></div><div><span>Source health</span><strong>96%</strong><small><b>All clear</b> · no gaps</small></div><div className="health-orb"><span /></div></div>
          </section>

          <div className="section-heading"><div><div className="section-kicker"><span className="section-number">01</span> DAILY SIGNALS</div><h2>Today’s AI trends</h2></div><div className="section-heading-actions"><button className="text-button"><Library size={14} /> View all signals <ArrowUpRight size={14} /></button><button className="filter-button"><Settings2 size={14} /> Customize</button></div></div>
          <div className="category-tabs" role="tablist" aria-label="Trend categories">{categories.map((category) => <button key={category} className={selectedCategory === category ? "category-active" : ""} onClick={() => setSelectedCategory(category)}>{category}{category === "All" && <span>8</span>}</button>)}</div>

          <section className="dashboard-grid">
            <div className="trend-feed">{filteredTrends.length ? filteredTrends.map((trend) => <TrendCard key={trend.id} trend={trend} saved={saved.includes(trend.id)} onSave={() => toggleSave(trend.id)} />) : <div className="empty-state"><Search size={20} /><strong>No signals found</strong><span>Try another category or search term.</span><button onClick={() => { setQuery(""); setSelectedCategory("All"); }}>Clear filters</button></div>}</div>
            <aside className="right-rail">
              <section className="rail-card model-card"><div className="rail-header"><div><div className="section-kicker"><span className="section-number">02</span> MOMENTUM</div><h3>Hot models</h3></div><button className="more-button">•••</button></div><p className="rail-intro">The models gaining attention right now, based on download velocity and community pull.</p><div className="model-list">{hotModels.map((model, index) => <a href="https://huggingface.co/models?sort=trending" target="_blank" rel="noreferrer" className="model-row" key={model.name}><span className={`model-index model-${model.accent}`}>{String(index + 1).padStart(2, "0")}</span><span className="model-orb" /><span className="model-copy"><strong>{model.name}</strong><small>{model.org} · {model.detail}</small></span><span className={`model-momentum ${model.momentum === "new" ? "new" : ""}`}>{model.momentum}</span></a>)}</div><a href="https://huggingface.co/models?sort=trending" target="_blank" rel="noreferrer" className="rail-link">Explore model momentum <ArrowUpRight size={14} /></a></section>
              <section className="rail-card topic-card"><div className="rail-header"><div><div className="section-kicker"><span className="section-number">03</span> YOUR RADAR</div><h3>Topics to follow</h3></div><Tags size={16} className="muted-icon" /></div><div className="topic-cloud">{topics.map((topic, index) => <button key={topic} className={`topic-chip topic-${index % 4}`} onClick={() => { setQuery(topic); setSelectedCategory("All"); }}>{topic}<span>{[18, 14, 11, 9, 8, 7, 6, 5][index]}</span></button>)}</div><div className="topic-footer"><span><span className="status-dot" /> Personalised from your reading</span><ArrowUpRight size={14} /></div></section>
            </aside>
          </section>

          <section className="lower-grid">
            <section className="panel"><div className="panel-header"><div><div className="section-kicker"><span className="section-number">04</span> RESEARCH DESK</div><h3>Worth a closer read</h3></div><a className="panel-action" href="https://arxiv.org/" target="_blank" rel="noreferrer">Open library <ArrowUpRight size={14} /></a></div><div className="paper-list">{hotPapers.map((paper, index) => <a className="paper-row" href={paper.href} target="_blank" rel="noreferrer" key={paper.title}><span className="paper-index">0{index + 1}</span><span className="paper-copy"><strong>{paper.title}</strong><span>{paper.authors}</span><small>{paper.note}</small></span><span className="paper-metric">{paper.metric}</span><ExternalLink size={14} className="paper-link" /></a>)}</div></section>
            <section className="panel"><div className="panel-header"><div><div className="section-kicker"><span className="section-number">05</span> BUILDER SIGNAL</div><h3>Rising on GitHub</h3></div><a className="panel-action" href="https://github.com/trending" target="_blank" rel="noreferrer">See trending <ArrowUpRight size={14} /></a></div><div className="repo-list">{risingRepos.map((repo) => <a href={repo.href} target="_blank" rel="noreferrer" className="repo-row" key={repo.name}><div className="repo-icon"><Github size={16} /></div><div className="repo-copy"><strong>{repo.name}</strong><span>{repo.description}</span></div><div className="repo-stats"><span><Star size={12} /> {repo.stars}</span><small>{repo.language}</small></div></a>)}</div></section>
          </section>

          <section className="media-strip"><div className="media-intro"><div className="section-kicker"><span className="section-number">06</span> LISTEN / WATCH</div><h3>Keep the signal moving.</h3><p>Long-form context for the ideas that deserve more than a headline.</p></div><div className="media-list">{media.map((item, index) => <a className="media-item" href={item.href} target="_blank" rel="noreferrer" key={item.title}><div className={`media-play ${index === 1 ? "podcast" : ""}`}>{index === 1 ? <Headphones size={15} /> : <Play size={15} fill="currentColor" />}</div><div><strong>{item.title}</strong><span>{item.type} · {item.duration} · {item.meta}</span></div><ArrowUpRight size={14} className="media-arrow" /></a>)}</div></section>
          <footer className="page-footer"><span>AI Radar <span className="footer-dot">·</span> A calmer way to keep up.</span><span>Seed edition · September 2026 <span className="footer-dot">·</span> <a href="https://github.com/SHIJINGLI0206/daily-ai-news" target="_blank" rel="noreferrer">View source <ExternalLink size={11} /></a></span></footer>
        </div>
      </main>
    </div>
  );
}
