"""
embedding_engine.py
Handles article vectorization using TF-IDF + FAISS (no torch needed).
Falls back to simple keyword matching for semantic search.
"""

import os
import numpy as np
from langchain_core.documents import Document


def articles_to_documents(articles: list) -> list:
    """Convert raw article dicts into LangChain Document objects."""
    docs = []
    for art in articles:
        text = f"{art['title']}\n\n{art['content']}"
        metadata = {
            "title": art["title"],
            "source": art["source"],
            "url": art["url"],
            "publishedAt": art["publishedAt"],
        }
        docs.append(Document(page_content=text, metadata=metadata))
    return docs


class SimpleVectorStore:
    """Lightweight vector store using TF-IDF — no torch, no GPU needed."""

    def __init__(self, docs: list):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.docs = docs
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        texts = [d.page_content for d in docs]
        self.matrix = self.vectorizer.fit_transform(texts)

    def similarity_search(self, query: str, k: int = 3) -> list:
        from sklearn.metrics.pairwise import cosine_similarity
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        top_indices = scores.argsort()[::-1][:k]
        return [self.docs[i] for i in top_indices]


def build_vector_store(articles: list) -> SimpleVectorStore:
    """Build a TF-IDF vector store from articles."""
    docs = articles_to_documents(articles)
    if not docs:
        raise ValueError("No articles provided.")
    return SimpleVectorStore(docs)


def semantic_search(store: SimpleVectorStore, query: str, top_k: int = 3) -> list:
    """Search for most relevant documents."""
    return store.similarity_search(query, k=top_k)
