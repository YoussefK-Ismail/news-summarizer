"""
user_manager.py
Manages user preferences and search history, stored in a local JSON file.
Supports saving favourite topics, history lookup, and preference retrieval.
"""

import json
import os
from datetime import datetime
from typing import Optional

DEFAULT_PREFS_FILE = "user_prefs.json"

_DEFAULT_PROFILE = {
    "saved_topics": [],
    "search_history": [],
    "default_summary_mode": "brief",
    "max_articles": 5,
}


# ── Load / Save ────────────────────────────────────────────────────────────────

def _load_profile(path: str = DEFAULT_PREFS_FILE) -> dict:
    """Read user profile from disk, or return a blank one if it doesn't exist."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return dict(_DEFAULT_PROFILE)


def _save_profile(profile: dict, path: str = DEFAULT_PREFS_FILE) -> None:
    """Write user profile back to disk."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(profile, fh, indent=2, ensure_ascii=False)


# ── Topic management ───────────────────────────────────────────────────────────

def save_topic(topic: str, path: str = DEFAULT_PREFS_FILE) -> None:
    """Add a topic to the saved topics list (no duplicates)."""
    profile = _load_profile(path)
    topic = topic.strip().lower()
    if topic not in profile["saved_topics"]:
        profile["saved_topics"].append(topic)
        _save_profile(profile, path)
        print(f"[Prefs] Topic '{topic}' saved.")
    else:
        print(f"[Prefs] Topic '{topic}' is already in your list.")


def remove_topic(topic: str, path: str = DEFAULT_PREFS_FILE) -> None:
    """Remove a topic from the saved list."""
    profile = _load_profile(path)
    topic = topic.strip().lower()
    if topic in profile["saved_topics"]:
        profile["saved_topics"].remove(topic)
        _save_profile(profile, path)
        print(f"[Prefs] Topic '{topic}' removed.")
    else:
        print(f"[Prefs] Topic '{topic}' not found.")


def get_saved_topics(path: str = DEFAULT_PREFS_FILE) -> list[str]:
    """Return the list of saved topics."""
    return _load_profile(path).get("saved_topics", [])


# ── History management ─────────────────────────────────────────────────────────

def log_search(topic: str, mode: str, article_count: int, path: str = DEFAULT_PREFS_FILE) -> None:
    """Record a search event in the history log."""
    profile = _load_profile(path)
    entry = {
        "topic": topic,
        "mode": mode,
        "articles_fetched": article_count,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    profile["search_history"].append(entry)
    # keep history capped at 50 entries
    profile["search_history"] = profile["search_history"][-50:]
    _save_profile(profile, path)


def get_history(limit: int = 10, path: str = DEFAULT_PREFS_FILE) -> list[dict]:
    """Return the most recent search history entries."""
    history = _load_profile(path).get("search_history", [])
    return history[-limit:]


# ── General preference helpers ─────────────────────────────────────────────────

def set_default_mode(mode: str, path: str = DEFAULT_PREFS_FILE) -> None:
    """Update the preferred summary mode ('brief' or 'detailed')."""
    if mode not in ("brief", "detailed"):
        print("[Prefs] Mode must be 'brief' or 'detailed'.")
        return
    profile = _load_profile(path)
    profile["default_summary_mode"] = mode
    _save_profile(profile, path)
    print(f"[Prefs] Default summary mode set to '{mode}'.")


def get_default_mode(path: str = DEFAULT_PREFS_FILE) -> str:
    return _load_profile(path).get("default_summary_mode", "brief")


def set_max_articles(n: int, path: str = DEFAULT_PREFS_FILE) -> None:
    """Set how many articles to retrieve per search."""
    profile = _load_profile(path)
    profile["max_articles"] = max(1, min(n, 20))
    _save_profile(profile, path)
    print(f"[Prefs] Max articles per search set to {profile['max_articles']}.")


def get_max_articles(path: str = DEFAULT_PREFS_FILE) -> int:
    return _load_profile(path).get("max_articles", 5)


def display_profile(path: str = DEFAULT_PREFS_FILE) -> None:
    """Pretty-print the user's current preferences."""
    profile = _load_profile(path)
    print("\n── Your Profile ──────────────────────────────────")
    print(f"  Default summary mode : {profile.get('default_summary_mode', 'brief')}")
    print(f"  Articles per search  : {profile.get('max_articles', 5)}")
    topics = profile.get("saved_topics", [])
    print(f"  Saved topics ({len(topics)})    : {', '.join(topics) if topics else 'none'}")
    print("──────────────────────────────────────────────────\n")
