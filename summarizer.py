"""
summarizer.py
Two summarization chains using LangChain + Groq (LLaMA 3).
  - brief    : stuff chain  -> 1-2 sentence summary
  - detailed : map_reduce   -> full paragraph summary
All heavy imports deferred inside functions.
"""

import os


BRIEF_PROMPT_TEMPLATE = """You are a news editor. Read the article below and write ONE or TWO
clear sentences that capture the main idea. Do not add opinions or extra context.

Article:
{text}

Brief summary:"""

MAP_PROMPT_TEMPLATE = """Summarize the key points from this news article in 3-4 bullet points.
Be factual and concise.

Article:
{text}

Key points:"""

REDUCE_PROMPT_TEMPLATE = """You are a senior journalist. Using the key points below from multiple
articles on the same topic, write a cohesive paragraph summary (5-7 sentences).
Include the most important facts and perspectives. Avoid repetition.

Key points:
{text}

Detailed summary:"""


def _get_llm(groq_api_key: str):
    from langchain_groq import ChatGroq
    return ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.3,
    )


def brief_summary(articles: list, groq_api_key: str) -> str:
    """Stuff chain — best for small number of articles."""
    from langchain_classic.chains.summarize import load_summarize_chain
    from langchain_classic.prompts import PromptTemplate

    prompt = PromptTemplate(template=BRIEF_PROMPT_TEMPLATE, input_variables=["text"])
    llm = _get_llm(groq_api_key)
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt, verbose=False)
    result = chain.invoke({"input_documents": articles})
    return result["output_text"].strip()


def detailed_summary(articles: list, groq_api_key: str) -> str:
    """Map-reduce chain — handles multiple articles well."""
    from langchain_classic.chains.summarize import load_summarize_chain
    from langchain_classic.prompts import PromptTemplate

    map_prompt = PromptTemplate(template=MAP_PROMPT_TEMPLATE, input_variables=["text"])
    reduce_prompt = PromptTemplate(template=REDUCE_PROMPT_TEMPLATE, input_variables=["text"])
    llm = _get_llm(groq_api_key)
    chain = load_summarize_chain(
        llm,
        chain_type="map_reduce",
        map_prompt=map_prompt,
        combine_prompt=reduce_prompt,
        verbose=False,
    )
    result = chain.invoke({"input_documents": articles})
    return result["output_text"].strip()


def summarize(articles: list, mode: str, groq_api_key: str) -> str:
    """Route to the correct summarization chain."""
    if mode == "brief":
        return brief_summary(articles, groq_api_key)
    elif mode == "detailed":
        return detailed_summary(articles, groq_api_key)
    else:
        raise ValueError(f"Unknown mode '{mode}'. Use 'brief' or 'detailed'.")
