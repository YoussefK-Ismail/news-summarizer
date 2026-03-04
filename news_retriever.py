"""
news_retriever.py
Fetches news articles from NewsAPI based on a given topic.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Optional


NEWS_API_BASE = "https://newsapi.org/v1"


def fetch_articles(topic: str, api_key: str, max_results: int = 5, days_back: int = 7) -> list[dict]:
    """
    Pull articles from NewsAPI for a given topic.

    Args:
        topic: The keyword or phrase to search for.
        api_key: Your NewsAPI key.
        max_results: How many articles to return (default 5).
        days_back: How many days back to look (default 7).

    Returns:
        A list of article dicts with keys: title, description, content, url, publishedAt, source.
    """
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    params = {
        "q": topic,
        "from": from_date,
        "sortBy": "relevancy",
        "language": "en",
        "pageSize": max_results,
        "apiKey": api_key,
    }

    try:
        resp = requests.get("https://newsapi.org/v2/everything", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as err:
        print(f"[NewsAPI] Request failed: {err}")
        return []

    if data.get("status") != "ok":
        print(f"[NewsAPI] Error response: {data.get('message', 'Unknown error')}")
        return []

    articles = []
    for item in data.get("articles", []):
        articles.append({
            "title": item.get("title", "No title"),
            "description": item.get("description", ""),
            "content": item.get("content", "") or item.get("description", ""),
            "url": item.get("url", ""),
            "publishedAt": item.get("publishedAt", ""),
            "source": item.get("source", {}).get("name", "Unknown"),
        })

    return articles


def format_article_for_display(article: dict, index: int) -> str:
    """Return a simple string preview of an article."""
    pub_date = article.get("publishedAt", "")[:10]
    source = article.get("source", "Unknown")
    title = article.get("title", "No title")
    desc = article.get("description", "No description available.")
    return f"[{index}] {title}\n    Source: {source} | Date: {pub_date}\n    {desc}\n    URL: {article.get('url', '')}\n"
