import html
import re
import time

import streamlit as st

from src.agents.agents import (
    build_reader_agent,
    build_search_agent,
    critic_chain,
    writer_chain,
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DeepScan · Autonomous Research Lab",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Theme ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@300;400;500&display=swap');

:root {
    --bg: #05060d;
    --panel: rgba(255,255,255,0.035);
    --line: rgba(255,255,255,0.08);
    --cyan: #22d3ee;
    --violet: #a78bfa;
    --pink: #f472b6;
    --green: #4ade80;
    --text: #e6ebff;
    --muted: #8b93b7;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--text);
}

/* ── Background: grid + drifting aurora ── */
.stApp {
    background-color: var(--bg);
    background-image:
        linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
    background-size: 48px 48px;
}
.stApp::before {
    content: '';
    position: fixed;
    inset: -20%;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(40% 40% at 20% 20%, rgba(34,211,238,0.16), transparent 70%),
        radial-gradient(35% 35% at 80% 30%, rgba(167,139,250,0.16), transparent 70%),
        radial-gradient(40% 40% at 60% 85%, rgba(244,114,182,0.10), transparent 70%);
    animation: drift 22s ease-in-out infinite alternate;
}
@keyframes drift {
    0%   { transform: translate3d(0,0,0) scale(1); }
    100% { transform: translate3d(3%,-3%,0) scale(1.08); }
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2rem 3rem 4rem;
    max-width: 1200px;
    position: relative;
    z-index: 1;
}

/* ── Hero ── */
.hero { text-align: center; padding: 3rem 0 2rem; }
.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--cyan);
    border: 1px solid rgba(34,211,238,0.3);
    background: rgba(34,211,238,0.06);
    padding: 0.4rem 0.9rem;
    border-radius: 999px;
    margin-bottom: 1.4rem;
}
.hero-pill .dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 10px var(--green);
    animation: blink 1.6s ease-in-out infinite;
}
@keyframes blink { 50% { opacity: 0.25; } }
.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(3rem, 7vw, 5.6rem);
    font-weight: 700;
    line-height: 1;
    letter-spacing: -0.04em;
    color: #fff;
    margin: 0 0 1rem;
}
.hero h1 span {
    background: linear-gradient(110deg, var(--cyan), var(--violet), var(--pink), var(--cyan));
    background-size: 250% 100%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 7s linear infinite;
}
@keyframes shimmer { to { background-position: 250% 0; } }
.hero-sub {
    font-size: 1.05rem;
    font-weight: 300;
    color: var(--muted);
    max-width: 560px;
    margin: 0 auto;
    line-height: 1.7;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(34,211,238,0.4), rgba(167,139,250,0.4), transparent);
    margin: 2rem 0;
}

/* ── Input card: animated gradient border ── */
.st-key-input_card {
    border: 1px solid transparent;
    border-radius: 22px;
    padding: 2rem 2.2rem;
    margin-bottom: 1.2rem;
    background:
        linear-gradient(#0a0c18, #0a0c18) padding-box,
        linear-gradient(120deg, var(--cyan), var(--violet), var(--pink), var(--cyan)) border-box;
    background-size: 100% 100%, 300% 300%;
    animation: borderflow 8s linear infinite;
    box-shadow: 0 20px 60px rgba(0,0,0,0.45);
}
@keyframes borderflow {
    0%   { background-position: 0 0, 0% 50%; }
    100% { background-position: 0 0, 300% 50%; }
}

/* ── Inputs ── */
.stTextInput div[data-baseweb="input"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(34,211,238,0.25) !important;
    border-radius: 12px !important;
    transition: all 0.2s ease !important;
}
.stTextInput div[data-baseweb="input"]:focus-within {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 4px rgba(34,211,238,0.14), 0 0 24px rgba(34,211,238,0.12) !important;
}
.stTextInput input {
    background: transparent !important;
    color: #fff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.8rem 1rem !important;
}
.stTextInput label, .stTextInput label p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    color: var(--cyan) !important;
}

/* ── Primary button ── */
.stButton > button {
    position: relative;
    overflow: hidden;
    background: linear-gradient(120deg, var(--cyan), var(--violet) 60%, var(--pink)) !important;
    background-size: 160% 100% !important;
    color: #05060d !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.98rem !important;
    letter-spacing: 0.03em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.8rem 2rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 8px 30px rgba(34,211,238,0.25) !important;
}
.stButton > button:hover {
    background-position: 100% 0 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 38px rgba(167,139,250,0.4) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Quick-launch chips ── */
.try-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem;
    letter-spacing: 0.2em;
    color: var(--muted);
    text-transform: uppercase;
    margin: 0.4rem 0 0.6rem;
}
.st-key-chips .stButton > button {
    background: rgba(255,255,255,0.04) !important;
    color: #cfd8f5 !important;
    border: 1px solid var(--line) !important;
    box-shadow: none !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 400 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 0.55rem 0.9rem !important;
    border-radius: 10px !important;
}
.st-key-chips .stButton > button:hover {
    border-color: rgba(34,211,238,0.5) !important;
    color: #fff !important;
    background: rgba(34,211,238,0.08) !important;
    transform: translateX(3px) !important;
    box-shadow: none !important;
}

/* ── Pipeline ── */
.section-heading {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 600;
    color: #fff;
    margin: 0.6rem 0 1rem;
}
.progress {
    height: 5px;
    border-radius: 99px;
    background: rgba(255,255,255,0.07);
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, var(--cyan), var(--violet), var(--pink));
    box-shadow: 0 0 14px rgba(34,211,238,0.6);
    transition: width 0.6s ease;
}
.progress-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.64rem;
    letter-spacing: 0.18em;
    color: var(--muted);
    margin: 0.5rem 0 1.2rem;
}

.step-card {
    position: relative;
    overflow: hidden;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 1.15rem 1.4rem;
    margin-bottom: 0.9rem;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: rgba(255,255,255,0.08);
}
.step-card.active {
    border-color: rgba(34,211,238,0.5);
    background: rgba(34,211,238,0.06);
    animation: pulse 2s ease-in-out infinite;
}
.step-card.active::before { background: var(--cyan); }
.step-card.active::after {
    content: '';
    position: absolute;
    left: 0; bottom: 0;
    height: 2px; width: 35%;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
    animation: scan 1.6s linear infinite;
}
.step-card.done {
    border-color: rgba(74,222,128,0.3);
    background: rgba(74,222,128,0.045);
}
.step-card.done::before { background: var(--green); }
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 rgba(34,211,238,0); }
    50%      { box-shadow: 0 0 28px rgba(34,211,238,0.22); }
}
@keyframes scan { 0% { left: -35%; } 100% { left: 100%; } }

.step-header { display: flex; align-items: center; gap: 0.75rem; }
.step-icon { font-size: 1.15rem; }
.step-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.64rem;
    letter-spacing: 0.15em;
    color: var(--cyan);
    opacity: 0.8;
}
.step-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #fff;
}
.step-status {
    margin-left: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.64rem;
    letter-spacing: 0.12em;
}
.status-waiting { color: #5b6485; }
.status-running { color: var(--cyan); }
.status-done    { color: var(--green); }
.step-desc { font-size: 0.8rem; color: var(--muted); margin: 0.35rem 0 0 2rem; }

/* ── Stat tiles ── */
.stats { display: flex; gap: 0.9rem; margin: 0 0 1.6rem; flex-wrap: wrap; }
.stat {
    flex: 1;
    min-width: 140px;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 1rem 1.3rem;
}
.stat-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    background: linear-gradient(110deg, var(--cyan), var(--violet));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.2em;
    color: var(--muted);
}

/* ── Result panels ── */
.result-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin: 0.6rem 0 1rem;
}
.result-panel-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--cyan);
    margin-bottom: 0.9rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid rgba(34,211,238,0.15);
}
.result-content {
    font-size: 0.88rem;
    line-height: 1.75;
    color: #cdd5ee;
    word-break: break-word;
}

.st-key-report_card, .st-key-feedback_card {
    border-radius: 20px;
    padding: 2rem 2.4rem;
    margin-top: 1rem;
    backdrop-filter: blur(14px);
}
.st-key-report_card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(34,211,238,0.25);
    box-shadow: 0 0 50px rgba(34,211,238,0.05);
}
.st-key-feedback_card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(74,222,128,0.25);
    box-shadow: 0 0 50px rgba(74,222,128,0.05);
}
.st-key-report_card h1, .st-key-report_card h2, .st-key-report_card h3,
.st-key-feedback_card h1, .st-key-feedback_card h2, .st-key-feedback_card h3 {
    font-family: 'Space Grotesk', sans-serif;
    letter-spacing: -0.01em;
    color: #fff;
}
.st-key-report_card a { color: var(--cyan); }
.st-key-report_card code { color: var(--pink); }
.st-key-report_card blockquote { border-left: 3px solid var(--violet); color: #b9c2e0; }

.panel-label {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.1rem;
    padding-bottom: 0.7rem;
}
.panel-label.cyan  { color: var(--cyan);  border-bottom: 1px solid rgba(34,211,238,0.18); }
.panel-label.green { color: var(--green); border-bottom: 1px solid rgba(74,222,128,0.18); }
.score-badge {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    padding: 0.25rem 0.8rem;
    border-radius: 999px;
    border: 1px solid currentColor;
}

/* ── Misc ── */
.stSpinner > div { color: var(--cyan) !important; }
details {
    background: rgba(255,255,255,0.02);
    border-radius: 14px;
    border: 1px solid var(--line);
}
details summary {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.74rem !important;
    color: #b8c1de !important;
    letter-spacing: 0.08em !important;
}
.stDownloadButton > button {
    background: rgba(255,255,255,0.05) !important;
    color: #fff !important;
    border: 1px solid rgba(34,211,238,0.4) !important;
    border-radius: 12px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    margin-top: 0.8rem;
}
.stDownloadButton > button:hover {
    background: rgba(34,211,238,0.12) !important;
    border-color: var(--cyan) !important;
}
.notice {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #5b6485;
    text-align: center;
    margin-top: 3rem;
    letter-spacing: 0.12em;
}
</style>
""",
    unsafe_allow_html=True,
)


# ── Helpers ───────────────────────────────────────────────────────────────────
def to_text(content) -> str:
    """Gemini returns a list of blocks; Groq returns a plain string."""
    if isinstance(content, list):
        return "".join(b.get("text", "") for b in content if isinstance(b, dict))
    return str(content)


def safe_html(text: str) -> str:
    """Escape text and turn newlines into <br> (blank lines would break the HTML block)."""
    return html.escape(text).replace("\n", "<br>")


def set_topic(text: str):
    st.session_state.topic_input = text


STEPS = [
    ("search", "01", "🔍", "Search Agent", "Gathers recent web information"),
    ("reader", "02", "📄", "Reader Agent", "Scrapes & extracts deep content"),
    ("writer", "03", "✍️", "Writer Chain", "Drafts the full research report"),
    ("critic", "04", "🧐", "Critic Chain", "Reviews & scores the report"),
]

EXAMPLES = [
    "Future of LLMs in the tech industry",
    "Latest AI agents in 2026",
    "Roadmap for AGI development in the next 5 years",
]


def step_card(num: str, icon: str, title: str, state: str, desc: str):
    label, cls = {
        "waiting": ("WAITING", "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done": ("✓ DONE", "status-done"),
    }[state]
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    st.markdown(
        f'<div class="step-card {card_cls}">'
        f'<div class="step-header"><span class="step-icon">{icon}</span>'
        f'<span class="step-num">{num}</span><span class="step-title">{title}</span>'
        f'<span class="step-status {cls}">{label}</span></div>'
        f'<div class="step-desc">{desc}</div></div>',
        unsafe_allow_html=True,
    )


def progress_html(frac: float) -> str:
    pct = int(frac * 100)
    return (
        f'<div class="progress"><div class="progress-fill" style="width:{pct}%"></div></div>'
        f'<div class="progress-label">{pct}% COMPLETE</div>'
    )


def stats_html(r: dict, elapsed: float) -> str:
    sources = len(set(re.findall(r"https?://[^\s)\]>\"']+", r.get("search", ""))))
    words = len(r.get("writer", "").split())
    tiles = [
        ("SOURCES FOUND", f"{sources}"),
        ("REPORT WORDS", f"{words:,}"),
        ("RUNTIME", f"{elapsed:.0f}s"),
    ]
    inner = "".join(
        f'<div class="stat"><div class="stat-value">{v}</div><div class="stat-label">{k}</div></div>'
        for k, v in tiles
    )
    return f'<div class="stats">{inner}</div>'


def score_badge(critic_text: str) -> str:
    m = re.search(r"Score:\s*\**\s*(\d+(?:\.\d+)?)\s*/\s*10", critic_text)
    if not m:
        return ""
    score = float(m.group(1))
    color = "#4ade80" if score >= 8 else "#fbbf24" if score >= 6 else "#f87171"
    return f'<span class="score-badge" style="color:{color}">{m.group(1)}/10</span>'


# ── Session state ─────────────────────────────────────────────────────────────
st.session_state.setdefault("results", {})
st.session_state.setdefault("running", False)
st.session_state.setdefault("done", False)
st.session_state.setdefault("error", None)
st.session_state.setdefault("elapsed", 0.0)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero">'
    '<div class="hero-pill"><span class="dot"></span>4 agents online</div>'
    "<h1>Deep<span>Scan</span></h1>"
    '<p class="hero-sub">Drop in a topic. A search agent, a reader, a writer and a critic '
    "team up to dig through the web and hand back a reviewed research report.</p>"
    '</div><div class="divider"></div>',
    unsafe_allow_html=True,
)


# ── Layout ────────────────────────────────────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    with st.container(key="input_card"):
        topic = st.text_input(
            "Research Topic",
            placeholder="e.g. Roadmap for AGI development in the next 5 years",
            key="topic_input",
        )
        run_btn = st.button("⚡ Launch Scan", use_container_width=True)

    st.markdown('<div class="try-label">// quick launch</div>', unsafe_allow_html=True)
    with st.container(key="chips"):
        for i, ex in enumerate(EXAMPLES):
            st.button(
                ex,
                key=f"chip_{i}",
                on_click=set_topic,
                args=(ex,),
                use_container_width=True,
            )

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)
    progress_slot = st.empty()
    slots = {key: st.empty() for key, *_ in STEPS}


def render_steps(running_step=None):
    r = st.session_state.results
    done_count = sum(1 for key, *_ in STEPS if key in r)
    frac = (done_count + (0.5 if running_step else 0)) / len(STEPS)
    progress_slot.markdown(progress_html(frac), unsafe_allow_html=True)
    for key, num, icon, title, desc in STEPS:
        state = "done" if key in r else "running" if key == running_step else "waiting"
        with slots[key].container():
            step_card(num, icon, title, state, desc)


render_steps()


# ── Start pipeline ────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.session_state.error = None
        st.rerun()


# ── Run pipeline ──────────────────────────────────────────────────────────────
if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input
    t0 = time.perf_counter()

    try:
        render_steps("search")
        with st.spinner("🔍 Search Agent is working…"):
            search_agent = build_search_agent()
            sr = search_agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Find recent, reliable and detailed information about: {topic_val}",
                        }
                    ]
                }
            )
            results["search"] = to_text(sr["messages"][-1].content)
            st.session_state.results = dict(results)

        render_steps("reader")
        with st.spinner("📄 Reader Agent is scraping top resources…"):
            reader_agent = build_reader_agent()
            rr = reader_agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": (
                                f"Based on the following search results about '{topic_val}', "
                                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                                f"Search Results:\n{results['search'][:800]}"
                            ),
                        }
                    ]
                }
            )
            results["reader"] = to_text(rr["messages"][-1].content)
            st.session_state.results = dict(results)

        render_steps("writer")
        with st.spinner("✍️ Writer is drafting the report…"):
            research_combined = (
                f"SEARCH RESULTS:\n{results['search']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
            )
            results["writer"] = writer_chain.invoke(
                {
                    "topic": topic_val,
                    "research": research_combined,
                }
            )
            st.session_state.results = dict(results)

        render_steps("critic")
        with st.spinner("🧐 Critic is reviewing the report…"):
            results["critic"] = critic_chain.invoke({"report": results["writer"]})
            st.session_state.results = dict(results)

        st.session_state.elapsed = time.perf_counter() - t0
        st.session_state.running = False
        st.session_state.done = True
        st.rerun()

    except Exception as e:
        st.session_state.running = False
        st.session_state.error = str(e)
        render_steps()


if st.session_state.error:
    st.error(f"Pipeline failed: {st.session_state.error}")


# ── Results ───────────────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    if st.session_state.done and "critic" in r:
        st.markdown(stats_html(r, st.session_state.elapsed), unsafe_allow_html=True)

    if "search" in r:
        with st.expander("🔍 Search results (raw)", expanded=False):
            st.markdown(
                f'<div class="result-panel"><div class="result-panel-title">Search Agent Output</div>'
                f'<div class="result-content">{safe_html(r["search"])}</div></div>',
                unsafe_allow_html=True,
            )

    if "reader" in r:
        with st.expander("📄 Scraped content (raw)", expanded=False):
            st.markdown(
                f'<div class="result-panel"><div class="result-panel-title">Reader Agent Output</div>'
                f'<div class="result-content">{safe_html(r["reader"])}</div></div>',
                unsafe_allow_html=True,
            )

    if "writer" in r:
        with st.container(key="report_card"):
            st.markdown(
                '<div class="panel-label cyan">📝 Research Report</div>',
                unsafe_allow_html=True,
            )
            st.markdown(r["writer"])

        st.download_button(
            label="⬇ Download report (.md)",
            data=r["writer"],
            file_name=f"deepscan_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        with st.container(key="feedback_card"):
            st.markdown(
                f'<div class="panel-label green"><span>🧐 Critic Feedback</span>{score_badge(r["critic"])}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(r["critic"])


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="notice">DEEPSCAN · MULTI-AGENT RESEARCH · BUILT WITH LANGCHAIN + STREAMLIT</div>',
    unsafe_allow_html=True,
)
