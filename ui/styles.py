"""
UI Styles — Premium warm theme inspired by Shashi.ai aesthetic.

Paper-like warmth, serif typography, vellum-glass panels, Da Vinci grid.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400;1,500&family=Inter:wght@200;300;400;500&family=JetBrains+Mono:wght@200;300;400&display=swap');

:root {
    --paper: #FDFCF8;
    --ink: #1C1917;
    --sepia: #78350F;
    --rust: #9A3412;
    --stone: #E7E5E4;
    --warm-50: #FAFAF9;
    --warm-100: #F5F5F4;
    --warm-200: #E7E5E4;
    --warm-300: #D6D3D1;
    --warm-400: #A8A29E;
    --warm-500: #78716C;
    --warm-600: #57534E;
    --warm-700: #44403C;
    --warm-800: #292524;
    --warm-900: #1C1917;
}

/* ── Global ──────────────────────────────────────────────────────── */
.stApp {
    background-color: var(--paper) !important;
    color: var(--ink);
    font-family: 'Inter', sans-serif;
    font-weight: 300;
}

/* Da Vinci Grid Overlay */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background-size: 40px 40px;
    background-image:
        linear-gradient(to right, rgba(28, 25, 23, 0.025) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(28, 25, 23, 0.025) 1px, transparent 1px);
}

/* ── Sidebar ─────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(253, 252, 248, 0.92) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-right: 1px solid rgba(28, 25, 23, 0.06) !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
    font-family: 'Cormorant Garamond', serif !important;
    color: var(--ink) !important;
    font-weight: 500;
    letter-spacing: -0.01em;
}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown span {
    font-family: 'Inter', sans-serif !important;
    font-weight: 300;
    color: var(--warm-600);
}

[data-testid="stSidebar"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--warm-500) !important;
}

/* ── Vellum Glass Cards ──────────────────────────────────────────── */
.vellum-glass {
    background: rgba(253, 252, 248, 0.85);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(28, 25, 23, 0.08);
    border-radius: 2px;
    box-shadow:
        0 4px 6px -1px rgba(0, 0, 0, 0.02),
        0 20px 40px -4px rgba(28, 25, 23, 0.05);
}

/* ── Architecture Cards ──────────────────────────────────────────── */
.arch-card {
    background: rgba(253, 252, 248, 0.85);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(28, 25, 23, 0.08);
    border-top: 2px solid var(--ink);
    padding: 2rem;
    min-height: 180px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.arch-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 32px -4px rgba(28, 25, 23, 0.08);
}

.arch-card .card-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--warm-400);
    margin-bottom: 0.5rem;
}

.arch-card .card-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--ink);
    padding-bottom: 0.8rem;
    margin-bottom: 0.8rem;
    border-bottom: 1px solid rgba(28, 25, 23, 0.08);
}

.arch-card .card-body {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    font-weight: 300;
    color: var(--warm-600);
    line-height: 1.6;
}

/* ── Metric Cards ────────────────────────────────────────────────── */
.metric-card {
    background: rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(28, 25, 23, 0.06);
    padding: 1.5rem 1.2rem;
    text-align: center;
    min-height: 100px;
}

.metric-card .metric-value {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.4rem;
    font-weight: 400;
    color: var(--ink);
    letter-spacing: -0.02em;
}

.metric-card .metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--warm-400);
    margin-top: 0.3rem;
}

/* ── Chat ────────────────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: rgba(253, 252, 248, 0.6) !important;
    border: 1px solid rgba(28, 25, 23, 0.06) !important;
    border-radius: 2px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 300;
}

.stChatInputContainer {
    border-color: rgba(28, 25, 23, 0.12) !important;
    background: rgba(253, 252, 248, 0.9) !important;
}

[data-testid="stChatInput"] textarea {
    font-family: 'Inter', sans-serif !important;
    font-weight: 300 !important;
}

/* ── Routing Badge ───────────────────────────────────────────────── */
.routing-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    border: 1px solid;
    margin: 0.5rem 0;
}

.routing-badge.simple {
    background: rgba(22, 163, 74, 0.05);
    border-color: rgba(22, 163, 74, 0.2);
    color: #15803d;
}

.routing-badge.medium {
    background: rgba(154, 52, 18, 0.05);
    border-color: rgba(154, 52, 18, 0.2);
    color: var(--rust);
}

.routing-badge.complex {
    background: rgba(120, 53, 15, 0.05);
    border-color: rgba(120, 53, 15, 0.2);
    color: var(--sepia);
}

/* ── Source Badges ───────────────────────────────────────────────── */
.source-badge {
    display: inline-block;
    background: rgba(28, 25, 23, 0.04);
    border: 1px solid rgba(28, 25, 23, 0.1);
    color: var(--warm-600);
    padding: 0.15rem 0.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0.15rem;
}

/* ── Agent Steps ─────────────────────────────────────────────────── */
.agent-step {
    padding: 0.6rem 1rem;
    margin: 0.3rem 0;
    border-left: 2px solid var(--warm-300);
    background: rgba(253, 252, 248, 0.6);
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    font-weight: 300;
    color: var(--warm-600);
}

.agent-step.running {
    border-left-color: var(--rust);
    animation: pulse-step 1.5s ease-in-out infinite;
}

.agent-step.done {
    border-left-color: var(--ink);
}

@keyframes pulse-step {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

/* ── Tabs ────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid rgba(28, 25, 23, 0.08);
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--warm-400) !important;
    padding: 0.8rem 1.5rem !important;
}

.stTabs [aria-selected="true"] {
    border-bottom: 2px solid var(--ink) !important;
    color: var(--ink) !important;
}

/* ── Buttons ─────────────────────────────────────────────────────── */
.stButton > button {
    background: var(--ink) !important;
    color: var(--paper) !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.3s !important;
}

.stButton > button:hover {
    background: var(--sepia) !important;
    transform: translateY(-1px);
    box-shadow: 0 8px 24px -4px rgba(28, 25, 23, 0.15);
}

/* ── File Uploader ───────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    border: 1px dashed rgba(28, 25, 23, 0.15) !important;
    border-radius: 2px;
    background: rgba(255, 255, 255, 0.3);
}

[data-testid="stFileUploader"]:hover {
    border-color: rgba(28, 25, 23, 0.3) !important;
}

/* ── Select boxes ────────────────────────────────────────────────── */
[data-baseweb="select"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Expander ────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--warm-500) !important;
    border: 1px solid rgba(28, 25, 23, 0.06);
    background: rgba(255, 255, 255, 0.4);
}

/* ── Toggle ──────────────────────────────────────────────────────── */
[data-testid="stToggle"] label span {
    font-family: 'Inter', sans-serif !important;
    font-weight: 300 !important;
    font-size: 0.85rem !important;
}

/* ── Divider ─────────────────────────────────────────────────────── */
hr {
    border-color: rgba(28, 25, 23, 0.06) !important;
}

/* ── Info/Success/Error boxes ────────────────────────────────────── */
[data-testid="stAlert"] {
    font-family: 'Inter', sans-serif;
    font-weight: 300;
    border-radius: 2px;
}

/* ── Scrollbar ───────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--paper); }
::-webkit-scrollbar-thumb { background: var(--warm-300); }
::-webkit-scrollbar-thumb:hover { background: var(--warm-400); }

/* ── Dataframe ───────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
}

/* ── Selection ───────────────────────────────────────────────────── */
::selection {
    background: var(--stone);
    color: var(--ink);
}

/* ── Caption ─────────────────────────────────────────────────────── */
.stCaption, [data-testid="stCaptionContainer"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
</style>
"""
