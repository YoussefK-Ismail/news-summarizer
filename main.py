"""
main.py
Entry point for the News Summarizer CLI.

Usage:
    python main.py

Environment variables needed (or pass via prompt):
    NEWS_API_KEY   — from https://newsapi.org
    GROQ_API_KEY   — from https://console.groq.com
"""

import os
import sys

from dotenv import load_dotenv
load_dotenv()  # loads .env file automatically

import user_manager as um
from news_retriever import fetch_articles, format_article_for_display
from embedding_engine import build_vector_store, semantic_search, articles_to_documents
from summarizer import summarize


# ── helpers ────────────────────────────────────────────────────────────────────

def _get_env_key(env_var: str, prompt_label: str) -> str:
    """Return value from env variable, or ask the user to type it."""
    val = os.environ.get(env_var, "").strip()
    if not val:
        val = input(f"Enter your {prompt_label}: ").strip()
    return val


def _pick_mode() -> str:
    """Ask the user to pick brief or detailed, with the default pre-selected."""
    default = um.get_default_mode()
    choice = input(f"Summary mode — [b]rief / [d]etailed (default: {default}): ").strip().lower()
    if choice in ("d", "detailed"):
        return "detailed"
    if choice in ("b", "brief"):
        return "brief"
    return default


def _print_separator(char: str = "─", width: int = 52) -> None:
    print(char * width)


# ── main menu actions ──────────────────────────────────────────────────────────

def action_search(news_key: str, groq_key: str) -> None:
    """Search for news on a topic and show a summary."""
    topic = input("Enter topic to search: ").strip()
    if not topic:
        print("No topic entered.")
        return

    max_n = um.get_max_articles()
    print(f"\nFetching up to {max_n} articles about '{topic}'…")
    articles = fetch_articles(topic, news_key, max_results=max_n)

    if not articles:
        print("No articles found. Try a different topic or check your API key.")
        return

    print(f"\nFound {len(articles)} article(s):\n")
    for i, art in enumerate(articles, start=1):
        print(format_article_for_display(art, i))

    mode = _pick_mode()
    print(f"\nGenerating {mode} summary…\n")

    # build embeddings and pull the most relevant docs
    store = build_vector_store(articles)
    relevant_docs = semantic_search(store, topic, top_k=min(3, len(articles)))

    summary_text = summarize(relevant_docs, mode, groq_key)

    _print_separator()
    print(f"  {mode.upper()} SUMMARY — {topic.upper()}")
    _print_separator()
    print(summary_text)
    _print_separator()

    um.log_search(topic, mode, len(articles))


def action_save_topic() -> None:
    """Save a topic to the user's favourites."""
    topic = input("Topic to save: ").strip()
    if topic:
        um.save_topic(topic)


def action_view_saved() -> None:
    """List all saved topics."""
    topics = um.get_saved_topics()
    if topics:
        print("\nSaved topics:")
        for i, t in enumerate(topics, 1):
            print(f"  {i}. {t}")
        print()
    else:
        print("No saved topics yet.")


def action_search_saved(news_key: str, groq_key: str) -> None:
    """Pick from saved topics and run a search on it."""
    topics = um.get_saved_topics()
    if not topics:
        print("No saved topics. Use option 2 to save one first.")
        return

    print("\nYour saved topics:")
    for i, t in enumerate(topics, 1):
        print(f"  {i}. {t}")

    raw = input("Pick a number: ").strip()
    try:
        idx = int(raw) - 1
        topic = topics[idx]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    # temporarily override topic for the search flow
    max_n = um.get_max_articles()
    print(f"\nFetching up to {max_n} articles about '{topic}'…")
    articles = fetch_articles(topic, news_key, max_results=max_n)

    if not articles:
        print("No articles found.")
        return

    mode = _pick_mode()
    print(f"\nGenerating {mode} summary…\n")

    store = build_vector_store(articles)
    relevant_docs = semantic_search(store, topic, top_k=min(3, len(articles)))
    summary_text = summarize(relevant_docs, mode, groq_key)

    _print_separator()
    print(f"  {mode.upper()} SUMMARY — {topic.upper()}")
    _print_separator()
    print(summary_text)
    _print_separator()

    um.log_search(topic, mode, len(articles))


def action_view_history() -> None:
    """Display the last 10 searches."""
    history = um.get_history(limit=10)
    if not history:
        print("No search history yet.")
        return

    print("\nRecent searches:")
    for entry in reversed(history):
        print(f"  [{entry['timestamp']}]  {entry['topic']}  ({entry['mode']}, {entry['articles_fetched']} articles)")
    print()


def action_settings() -> None:
    """Let the user change preferences."""
    print("\nSettings")
    print("  1. Change default summary mode")
    print("  2. Change max articles per search")
    print("  3. Remove a saved topic")
    print("  4. Back")

    choice = input("Choose: ").strip()
    if choice == "1":
        mode = input("New default mode (brief/detailed): ").strip().lower()
        um.set_default_mode(mode)
    elif choice == "2":
        raw = input("Max articles (1-20): ").strip()
        try:
            um.set_max_articles(int(raw))
        except ValueError:
            print("Please enter a number.")
    elif choice == "3":
        action_view_saved()
        topic = input("Topic to remove: ").strip()
        if topic:
            um.remove_topic(topic)


# ── main loop ──────────────────────────────────────────────────────────────────

def main() -> None:
    print("\n╔══════════════════════════════════════════╗")
    print("║       News Summarizer — powered by Groq  ║")
    print("╚══════════════════════════════════════════╝\n")

    news_key = _get_env_key("NEWS_API_KEY", "NewsAPI key")
    groq_key = _get_env_key("GROQ_API_KEY", "Groq API key")

    if not news_key or not groq_key:
        print("Both API keys are required. Exiting.")
        sys.exit(1)

    um.display_profile()

    while True:
        print("Main Menu")
        print("  1. Search news on a topic")
        print("  2. Save a topic")
        print("  3. View saved topics")
        print("  4. Search from saved topics")
        print("  5. View search history")
        print("  6. Settings")
        print("  7. Exit")
        _print_separator()

        choice = input("Choose an option: ").strip()
        print()

        if choice == "1":
            action_search(news_key, groq_key)
        elif choice == "2":
            action_save_topic()
        elif choice == "3":
            action_view_saved()
        elif choice == "4":
            action_search_saved(news_key, groq_key)
        elif choice == "5":
            action_view_history()
        elif choice == "6":
            action_settings()
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid option, try again.\n")


if __name__ == "__main__":
    main()
