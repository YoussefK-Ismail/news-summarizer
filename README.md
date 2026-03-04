# News Summarizer — LangChain + Groq

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://news-summarizer-gpbfwm4ddcyqxjnbbabrf4.streamlit.app/)

🚀 **Live Demo:** https://news-summarizer-gpbfwm4ddcyqxjnbbabrf4.streamlit.app/

A command-line app that fetches real news articles and generates AI-powered summaries using **LangChain**, **Groq (LLaMA 3)**, and **FAISS** vector search.

---

## Features

- Fetches live articles from [NewsAPI](https://newsapi.org/)
- Two summarization modes: **brief** (1-2 sentences) and **detailed** (full paragraph)
- Semantic search using FAISS + HuggingFace embeddings (`all-MiniLM-L6-v2`)
- Saves your favourite topics and search history to a local JSON file
- Clean command-line menu interface

---

## Project Structure

```
news_summarizer/
├── main.py              # CLI entry point
├── news_retriever.py    # NewsAPI integration
├── embedding_engine.py  # FAISS vector store + HuggingFace embeddings
├── summarizer.py        # LangChain summarization chains (Groq / LLaMA 3)
├── user_manager.py      # User preferences + history (JSON)
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get API keys

| Service | URL | Free tier |
|---------|-----|-----------|
| NewsAPI | https://newsapi.org/register | 100 req/day |
| Groq    | https://console.groq.com     | Free (fast LLaMA 3) |

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables (optional but recommended)

```bash
# Linux / macOS
export NEWS_API_KEY="your_newsapi_key_here"
export GROQ_API_KEY="your_groq_key_here"

# Windows (PowerShell)
$env:NEWS_API_KEY="your_newsapi_key_here"
$env:GROQ_API_KEY="your_groq_key_here"
```

If you skip this step the app will ask for the keys on startup.

### 4. Run

```bash
python main.py
```

---

## Usage Walkthrough

```
Main Menu
  1. Search news on a topic       ← type any topic, pick brief or detailed summary
  2. Save a topic                 ← bookmark topics you follow regularly
  3. View saved topics
  4. Search from saved topics     ← quick search from your bookmarks
  5. View search history
  6. Settings                     ← change default mode, max articles, etc.
  7. Exit
```

### Example session

```
Enter topic to search: artificial intelligence

Found 5 article(s): ...

Summary mode — [b]rief / [d]etailed (default: brief): d

Generating detailed summary…

────────────────────────────────────────────────────
  DETAILED SUMMARY — ARTIFICIAL INTELLIGENCE
────────────────────────────────────────────────────
Recent developments in artificial intelligence have ...
────────────────────────────────────────────────────
```

---

## Dependencies

```
langchain
langchain-community
langchain-groq
faiss-cpu
sentence-transformers
requests
```

Full list in `requirements.txt`.

---

## Notes

- Embeddings run **locally** using `sentence-transformers` — no extra API key needed.
- FAISS index is rebuilt fresh each search session (not persisted between runs by default).
- User preferences are saved in `user_prefs.json` in the current working directory.
- The summarizer uses **LLaMA 3 8B** via Groq's free API, which is very fast.
