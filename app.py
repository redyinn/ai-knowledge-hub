"""
AI Knowledge Hub — Streamlit Application

Intelligent document analysis platform with:
- RAG Pipeline (Upload → Chunk → Embed → Retrieve → Generate)
- Multi-Model Routing (automatic model selection by query complexity)
- Agent Mode (autonomous multi-step research)
- Evaluation Dashboard (retrieval quality, latency, cost tracking)

Author: Ertugrul Korkmaz
"""
import streamlit as st

st.set_page_config(
    page_title="AI Knowledge Hub",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

from config import MODELS, get_api_key
from ui.styles import CUSTOM_CSS
from ui.components import (
    render_3d_hero,
    render_header,
    render_metric_card,
    render_source_badges,
    render_routing_badge,
    render_agent_step,
    render_arch_card,
    render_section_label,
)
from rag.loader import load_document
from rag.pipeline import RAGPipeline
from agents.router import route_query
from agents.researcher import ResearchAgent
from evaluation.tracker import PerformanceTracker
from evaluation.metrics import evaluate_retrieval


# ── Inject CSS ───────────────────────────────────────────────────────
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ── Session State ────────────────────────────────────────────────────
def init_state():
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = RAGPipeline()
    if "tracker" not in st.session_state:
        st.session_state.tracker = PerformanceTracker()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "documents" not in st.session_state:
        st.session_state.documents = []
    if "agent_mode" not in st.session_state:
        st.session_state.agent_mode = False
    if "auto_routing" not in st.session_state:
        st.session_state.auto_routing = True

init_state()

pipeline: RAGPipeline = st.session_state.pipeline
tracker: PerformanceTracker = st.session_state.tracker


# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:1.5rem;">
        <div style="width:28px;height:28px;border:1px solid #1C1917;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;">
            <div style="position:absolute;width:100%;height:1px;background:#1C1917;transform:rotate(45deg);"></div>
            <div style="position:absolute;width:100%;height:1px;background:#1C1917;transform:rotate(-45deg);"></div>
        </div>
        <span style="font-family:'Cormorant Garamond',serif;font-size:1.2rem;color:#1C1917;font-weight:500;letter-spacing:-0.01em;">Knowledge Hub</span>
    </div>
    """, unsafe_allow_html=True)

    # API Key
    api_key = get_api_key()
    if api_key:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:0.5rem;">
            <div style="width:6px;height:6px;border-radius:50%;background:#16a34a;box-shadow:0 0 6px rgba(22,163,74,0.3);"></div>
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#57534E;text-transform:uppercase;letter-spacing:0.1em;">API Connected</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        api_input = st.text_input(
            "OpenRouter API Key",
            type="password",
            help="Get a free key at openrouter.ai",
        )
        if api_input:
            import os
            os.environ["OPENROUTER_API_KEY"] = api_input
            st.rerun()

    st.divider()

    # Document Upload
    st.markdown("### Documents")
    uploaded_files = st.file_uploader(
        "Drop files here",
        type=["pdf", "txt", "md", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    strategy = st.selectbox(
        "Chunking Strategy",
        options=["recursive", "fixed", "semantic"],
        format_func=lambda s: {
            "recursive": "Recursive (recommended)",
            "fixed": "Fixed-Size",
            "semantic": "Semantic",
        }[s],
    )

    # Process uploads
    if uploaded_files:
        new_files = [
            f for f in uploaded_files
            if f.name not in [d["name"] for d in st.session_state.documents]
        ]
        if new_files:
            with st.spinner(f"Processing {len(new_files)} document(s)..."):
                for file in new_files:
                    try:
                        doc = load_document(file, filename=file.name)
                        chunks = pipeline.ingest(doc, strategy=strategy)
                        st.session_state.documents.append({
                            "name": file.name,
                            "type": doc.file_type,
                            "words": doc.num_words,
                            "chunks": len(chunks),
                            "strategy": strategy,
                        })
                        st.success(f"{file.name} — {len(chunks)} chunks")
                    except Exception as e:
                        st.error(f"{file.name}: {e}")

    if st.session_state.documents:
        st.divider()
        st.markdown("### Loaded")
        for doc in st.session_state.documents:
            st.markdown(
                f"**{doc['name']}**  \n"
                f"`{doc['words']:,} words` · `{doc['chunks']} chunks`"
            )

        stats = pipeline.store.get_stats()
        st.markdown(
            f"<div style='font-family:JetBrains Mono,monospace;font-size:0.7rem;color:#A8A29E;"
            f"text-transform:uppercase;letter-spacing:0.08em;margin-top:0.5rem;'>"
            f"{stats['total_chunks']} chunks · {stats['num_sources']} sources"
            f"</div>",
            unsafe_allow_html=True,
        )

        if st.button("Clear All"):
            pipeline.store.clear()
            st.session_state.documents = []
            st.session_state.chat_history = []
            st.rerun()

    st.divider()

    # Mode Selection
    st.markdown("### Query Mode")
    st.session_state.agent_mode = st.toggle(
        "Agent Mode",
        value=st.session_state.agent_mode,
        help="Break complex questions into sub-questions and research autonomously.",
    )

    st.session_state.auto_routing = st.toggle(
        "Auto Routing",
        value=st.session_state.auto_routing,
        help="Automatically select the best model based on query complexity.",
    )

    if not st.session_state.auto_routing:
        manual_tier = st.selectbox(
            "Model",
            options=list(MODELS.keys()),
            format_func=lambda t: f"{MODELS[t]['name']} ({t})",
        )
        pipeline.set_model(manual_tier)

    # Footer
    st.divider()
    st.markdown(
        "<div style='text-align:center;font-family:JetBrains Mono,monospace;"
        "font-size:0.6rem;color:#A8A29E;text-transform:uppercase;letter-spacing:0.08em;'>"
        "Built by Ertugrul Korkmaz<br>"
        "Custom RAG · No LangChain"
        "</div>",
        unsafe_allow_html=True,
    )


# ── Main Content ─────────────────────────────────────────────────────

# 3D Hero
render_3d_hero()

# Tabs
tab_chat, tab_dashboard = st.tabs(["CHAT", "EVALUATION DASHBOARD"])


# ── TAB: Chat ────────────────────────────────────────────────────────
with tab_chat:
    if not st.session_state.documents:
        # Architecture overview
        render_section_label("THE PIPELINE")

        st.markdown("""
        <div style="margin-bottom:2rem;">
            <h2 style="font-family:'Cormorant Garamond',serif;font-size:2.8rem;font-weight:400;color:#1C1917;
                       line-height:1.1;letter-spacing:-0.02em;margin:0;">
                Five Pillars.
            </h2>
            <h2 style="font-family:'Cormorant Garamond',serif;font-size:2.8rem;font-weight:300;font-style:italic;
                       color:#78716C;line-height:1.1;letter-spacing:-0.02em;margin:0;">
                One Seamless Flow.
            </h2>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3, gap="medium")
        render_arch_card(
            "01", "UPLOAD & CHUNK",
            "Documents are split into chunks using recursive, fixed-size, or semantic strategies. "
            "Each strategy optimizes for different document structures and lengths.",
            col1,
        )
        render_arch_card(
            "02", "EMBED & STORE",
            "Chunks are converted to 384-dimensional vectors using sentence-transformers "
            "and stored in ChromaDB for millisecond-fast similarity search.",
            col2,
        )
        render_arch_card(
            "03", "RETRIEVE & GENERATE",
            "Questions trigger semantic search across all stored vectors. "
            "The most relevant context is fed to the LLM for grounded, cited answers.",
            col3,
        )

        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

        col4, col5 = st.columns(2, gap="medium")
        render_arch_card(
            "04", "MULTI-MODEL ROUTING",
            "Query complexity is analyzed using heuristic scoring. Simple questions route to fast models, "
            "complex multi-step reasoning automatically uses powerful models. Zero wasted compute.",
            col4,
        )
        render_arch_card(
            "05", "AGENT MODE",
            "Complex questions are decomposed into sub-questions by an autonomous research agent. "
            "Each sub-question is searched independently, then all findings are synthesized into one answer.",
            col5,
        )

        # Technical flow diagram
        st.markdown("""
        <div style="margin:3rem 0;padding:2rem;border:1px solid rgba(28,25,23,0.06);
                    background:rgba(255,255,255,0.4);display:flex;align-items:center;
                    justify-content:center;gap:2rem;flex-wrap:wrap;">
            <div style="padding:1rem 1.5rem;border:1px solid rgba(28,25,23,0.1);background:#FDFCF8;text-align:center;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:#A8A29E;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px;">YOUR DOCUMENTS</div>
                <div style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:1.3rem;color:#1C1917;">PDF, TXT, MD</div>
            </div>
            <div style="color:#9A3412;font-family:'JetBrains Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.1em;text-align:center;">
                <div style="margin-bottom:4px;opacity:0.6;">CHUNKS</div>
                <div style="font-size:1.2rem;">&#8594;</div>
            </div>
            <div style="padding:1.2rem 1.8rem;background:#1C1917;color:#FDFCF8;text-align:center;transform:scale(1.05);box-shadow:0 8px 24px rgba(28,25,23,0.15);">
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:rgba(253,252,248,0.5);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px;">INTELLIGENCE</div>
                <div style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:1.4rem;">RAG Pipeline</div>
            </div>
            <div style="color:#9A3412;font-family:'JetBrains Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.1em;text-align:center;">
                <div style="margin-bottom:4px;opacity:0.6;">GENERATES</div>
                <div style="font-size:1.2rem;">&#8594;</div>
            </div>
            <div style="padding:1rem 1.5rem;border:1px solid rgba(28,25,23,0.1);background:#FDFCF8;text-align:center;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:#A8A29E;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px;">EXPERIENCE</div>
                <div style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:1.3rem;color:#1C1917;">Cited Answers</div>
            </div>
        </div>

        <div style="margin:3rem 0 2rem;text-align:center;">
            <span style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:1.5rem;color:#78716C;letter-spacing:-0.01em;">
                Upload documents in the sidebar to begin
            </span>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("routing"):
                    render_routing_badge(
                        msg["routing"]["tier"],
                        msg["routing"]["model"],
                        msg["routing"]["reason"],
                    )
                if msg.get("sources"):
                    render_source_badges(msg["sources"])
                if msg.get("metrics"):
                    m = msg["metrics"]
                    st.caption(
                        f"Retrieval: {m.get('avg_relevance', 'N/A')} avg · "
                        f"{m.get('coverage', 'N/A')} coverage"
                    )

        # Chat input
        if question := st.chat_input("Ask a question about your documents..."):
            with st.chat_message("user"):
                st.markdown(question)
            st.session_state.chat_history.append({"role": "user", "content": question})

            with st.chat_message("assistant"):
                tracker.start_timer()

                routing = route_query(question)
                if st.session_state.auto_routing:
                    pipeline.set_model(routing.tier)

                render_routing_badge(routing.tier, routing.model_name, routing.reason)

                if st.session_state.agent_mode and routing.complexity.value == "complex":
                    # Agent Mode
                    st.markdown("""
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;
                         color:#9A3412;text-transform:uppercase;letter-spacing:0.08em;margin:0.5rem 0;">
                         Agent Mode — Autonomous Research
                    </div>
                    """, unsafe_allow_html=True)

                    agent = ResearchAgent(pipeline.store)
                    step_container = st.container()
                    final_answer = ""

                    gen = agent.research(question)
                    try:
                        while True:
                            step = next(gen)
                            with step_container:
                                render_agent_step(step.step_num, step.action, step.description, step.status)
                    except StopIteration as e:
                        if e.value:
                            final_answer = e.value.answer

                    latency = tracker.stop_timer()
                    st.markdown("---")
                    st.markdown(final_answer)

                    results = pipeline.retrieve(question)
                    ret_metrics = evaluate_retrieval(results)
                    sources_list = list({r.source for r in results})
                    render_source_badges(sources_list)

                    tracker.record(
                        query=question, model_name=routing.model_name,
                        model_tier=routing.tier, latency_ms=latency,
                        num_chunks=len(results), num_sources=len(sources_list),
                        complexity=routing.complexity.value,
                    )

                    st.session_state.chat_history.append({
                        "role": "assistant", "content": final_answer,
                        "routing": {"tier": routing.tier, "model": routing.model_name, "reason": routing.reason},
                        "sources": sources_list, "metrics": ret_metrics.to_dict(),
                    })

                else:
                    # Standard RAG
                    results = pipeline.retrieve(question)
                    ret_metrics = evaluate_retrieval(results)

                    if not results:
                        answer = "No relevant information found in the uploaded documents."
                        st.markdown(answer)
                        latency = tracker.stop_timer()
                    else:
                        answer_placeholder = st.empty()
                        full_answer = ""

                        for chunk in pipeline.query_stream(
                            question,
                            model_tier=routing.tier if st.session_state.auto_routing else None,
                        ):
                            full_answer += chunk
                            answer_placeholder.markdown(full_answer + "▌")

                        answer_placeholder.markdown(full_answer)
                        answer = full_answer
                        latency = tracker.stop_timer()

                        sources_list = list({r.source for r in results})
                        render_source_badges(sources_list)

                        st.caption(
                            f"Retrieval: {ret_metrics.avg_relevance:.0%} avg relevance · "
                            f"{ret_metrics.coverage_estimate} coverage · "
                            f"{latency:.0f}ms"
                        )

                    sources_list = list({r.source for r in results}) if results else []

                    tracker.record(
                        query=question, model_name=routing.model_name,
                        model_tier=routing.tier, latency_ms=latency,
                        num_chunks=len(results), num_sources=len(sources_list),
                        complexity=routing.complexity.value,
                    )

                    st.session_state.chat_history.append({
                        "role": "assistant", "content": answer,
                        "routing": {"tier": routing.tier, "model": routing.model_name, "reason": routing.reason},
                        "sources": sources_list,
                        "metrics": ret_metrics.to_dict() if results else {},
                    })


# ── TAB: Evaluation Dashboard ────────────────────────────────────────
with tab_dashboard:
    render_section_label("PERFORMANCE METRICS")

    if tracker.total_queries == 0:
        st.markdown("""
        <div style="text-align:center;padding:3rem;border:1px solid rgba(28,25,23,0.06);background:rgba(255,255,255,0.4);">
            <span style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:1.3rem;color:#78716C;">
                No queries yet — start chatting to see metrics
            </span>
        </div>
        """, unsafe_allow_html=True)
    else:
        col1, col2, col3, col4 = st.columns(4)
        render_metric_card("Total Queries", tracker.total_queries, col1)
        render_metric_card("Avg Latency", f"{tracker.avg_latency:.0f}ms", col2)
        render_metric_card("Documents", len(st.session_state.documents), col3)
        render_metric_card("Chunks Stored", pipeline.store.count, col4)

        st.markdown("---")

        col_left, col_right = st.columns(2)

        with col_left:
            render_section_label("MODEL DISTRIBUTION")
            model_dist = tracker.get_model_distribution()
            if model_dist:
                import pandas as pd
                df_model = pd.DataFrame(list(model_dist.items()), columns=["Model Tier", "Queries"])
                st.bar_chart(df_model.set_index("Model Tier"))

        with col_right:
            render_section_label("COMPLEXITY DISTRIBUTION")
            complexity_dist = tracker.get_complexity_distribution()
            if complexity_dist:
                import pandas as pd
                df_c = pd.DataFrame(list(complexity_dist.items()), columns=["Complexity", "Queries"])
                st.bar_chart(df_c.set_index("Complexity"))

        render_section_label("QUERY HISTORY")
        history_data = tracker.to_dataframe_data()
        if history_data:
            import pandas as pd
            df = pd.DataFrame(history_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

        if len(history_data) >= 2:
            render_section_label("LATENCY OVER TIME")
            import pandas as pd
            st.line_chart(pd.DataFrame(history_data)[["latency_ms"]])
