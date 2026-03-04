"""
embedding_engine.py
Handles article vectorization using HuggingFace embeddings and FAISS.
All heavy imports are deferred inside functions so torch loads only when needed.
"""

import os


FAISS_INDEX_PATH = "faiss_index"


def _build_embedder():
    """Return a HuggingFace embedding model (CPU only, no GPU needed)."""
    from langchain_community.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def articles_to_documents(articles: list) -> list:
    """Convert raw article dicts into LangChain Document objects."""
    from langchain_core.documents import Document
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


def build_vector_store(articles: list):
    """Create a FAISS vector store from a list of articles."""
    from langchain_community.vectorstores import FAISS
    embedder = _build_embedder()
    docs = articles_to_documents(articles)
    if not docs:
        raise ValueError("No articles provided.")
    return FAISS.from_documents(docs, embedder)


def semantic_search(store, query: str, top_k: int = 3) -> list:
    """Semantic similarity search against stored articles."""
    return store.similarity_search(query, k=top_k)
