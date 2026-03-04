"""
app.py  —  Streamlit UI for the News Summarizer
Run with:  streamlit run app.py
"""

import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="News Summarizer",
    page_icon="📰",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .stTextInput > div > div > input {
        background-color: #1e2130;
        color: white;
        border-radius: 10px;
    }
    .article-card {
        background: #1e2130;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border-left: 4px solid #4f8ef7;
    }
    .article-title { font-size: 15px; font-weight: 600; color: #e0e6ff; }
    .article-meta  { font-size: 12px; color: #7a8ba8; margin-top: 4px; }
    .article-desc  { font-size: 13px; color: #b0bdd0; margin-top: 8px; }
    .summary-box {
        background: linear-gradient(135deg, #1a2340, #1e2d50);
        border-radius: 14px;
        padding: 22px 26px;
        border: 1px solid #2e4070;
        color: #dce8ff;
        font-size: 15px;
        line-height: 1.7;
    }
    .tag {
        display: inline-block;
        background: #253050;
        color: #7eb8f7;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 12px;
        margin: 3px;
        cursor: pointer;
    }
    .history-row {
        background: #181e2e;
        border-radius: 8px;
        padding: 10px 16px;
        margin-bottom: 6px;
        font-size: 13px;
        color: #a0b0cc;
    }
</style>
""", unsafe_allow_html=True)

# ── Import app modules ─────────────────────────────────────────────────────────
import user_manager as um
from news_retriever import fetch_articles

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📰 News Summarizer")
    st.markdown("---")

    news_key = st.text_input(
        "NewsAPI Key",
        value=os.environ.get("NEWS_API_KEY", ""),
        type="password",
        placeholder="Paste your NewsAPI key…",
    )
    groq_key = st.text_input(
        "Groq API Key",
        value=os.environ.get("GROQ_API_KEY", ""),
        type="password",
        placeholder="Paste your Groq key…",
    )

    st.markdown("---")
    st.markdown("### ⚙️ Preferences")

    default_mode = um.get_default_mode()
    mode = st.radio(
        "Summary Mode",
        options=["brief", "detailed"],
        index=0 if default_mode == "brief" else 1,
        horizontal=True,
    )
    if mode != default_mode:
        um.set_default_mode(mode)

    max_arts = st.slider("Max articles", 1, 10, um.get_max_articles())
    if max_arts != um.get_max_articles():
        um.set_max_articles(max_arts)

    st.markdown("---")
    st.markdown("### 🔖 Saved Topics")
    saved = um.get_saved_topics()
    if saved:
        for t in saved:
            col1, col2 = st.columns([4, 1])
            col1.markdown(f"<span class='tag'>#{t}</span>", unsafe_allow_html=True)
            if col2.button("✕", key=f"del_{t}"):
                um.remove_topic(t)
                st.rerun()
    else:
        st.caption("No saved topics yet.")

# ── Main area ──────────────────────────────────────────────────────────────────
st.markdown("# 📰 News Summarizer")
st.markdown("Search for any topic and get an AI-powered summary using **Groq + LLaMA 3**.")

tabs = st.tabs(["🔍 Search", "🕓 History"])

# ── Search Tab ─────────────────────────────────────────────────────────────────
with tabs[0]:
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        topic = st.text_input(
            "Topic",
            placeholder="e.g.  artificial intelligence,  climate change,  Bitcoin…",
            label_visibility="collapsed",
        )
    with col_btn:
        search_clicked = st.button("Search 🔎", use_container_width=True)

    # Quick-search from saved topics
    if saved:
        st.markdown("**Quick search:**")
        cols = st.columns(min(len(saved), 6))
        for i, t in enumerate(saved):
            if cols[i % 6].button(f"#{t}", key=f"quick_{t}"):
                topic = t
                search_clicked = True

    if search_clicked:
        if not news_key or not groq_key:
            st.error("⚠️  Please enter both API keys in the sidebar first.")
        elif not topic:
            st.warning("Please enter a topic to search.")
        else:
            with st.spinner(f"Fetching articles about **{topic}**…"):
                articles = fetch_articles(topic, news_key, max_results=max_arts)

            if not articles:
                st.error("No articles found. Try a different topic or check your NewsAPI key.")
            else:
                # Option to save topic
                col_save, _ = st.columns([2, 5])
                if topic.lower() not in um.get_saved_topics():
                    if col_save.button(f"🔖 Save '{topic}'"):
                        um.save_topic(topic)
                        st.success(f"Topic '{topic}' saved!")
                        st.rerun()

                # Show articles
                with st.expander(f"📄 {len(articles)} articles found", expanded=False):
                    for i, art in enumerate(articles, 1):
                        pub = art.get("publishedAt", "")[:10]
                        st.markdown(f"""
                        <div class='article-card'>
                            <div class='article-title'>{i}. {art['title']}</div>
                            <div class='article-meta'>📰 {art['source']} &nbsp;|&nbsp; 📅 {pub}</div>
                            <div class='article-desc'>{art.get('description','')}</div>
                            <div class='article-meta' style='margin-top:8px'>
                                <a href='{art['url']}' target='_blank' style='color:#4f8ef7'>Read full article →</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                # Generate summary
                st.markdown("---")
                mode_label = "Brief Summary ⚡" if mode == "brief" else "Detailed Summary 📝"
                st.markdown(f"### {mode_label}")

                with st.spinner("Generating summary with LLaMA 3…"):
                    try:
                        from embedding_engine import build_vector_store, semantic_search
                        from summarizer import summarize

                        store = build_vector_store(articles)
                        relevant_docs = semantic_search(store, topic, top_k=min(3, len(articles)))
                        summary_text = summarize(relevant_docs, mode, groq_key)

                        st.markdown(
                            f"<div class='summary-box'>{summary_text}</div>",
                            unsafe_allow_html=True,
                        )
                        um.log_search(topic, mode, len(articles))

                    except Exception as e:
                        st.error(f"Summary failed: {e}")

# ── History Tab ────────────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown("### 🕓 Recent Searches")
    history = um.get_history(limit=20)
    if not history:
        st.info("No search history yet. Run a search first!")
    else:
        for entry in reversed(history):
            st.markdown(f"""
            <div class='history-row'>
                🕐 <b>{entry['timestamp']}</b> &nbsp;|&nbsp;
                🔍 <b>{entry['topic']}</b> &nbsp;|&nbsp;
                📋 {entry['mode']} &nbsp;|&nbsp;
                📄 {entry['articles_fetched']} articles
            </div>
            """, unsafe_allow_html=True)
