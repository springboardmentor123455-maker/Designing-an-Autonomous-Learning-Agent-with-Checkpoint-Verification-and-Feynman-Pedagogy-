# app/core/context_gatherer.py
from typing import List, Tuple
from langchain_core.documents import Document

from app.rag.vectorstore import build_notes_vectorstore
from app.config import TAVILY_API_KEY
from langchain_tavily import TavilySearch


def gather_from_notes(query: str, k: int = 5) -> List[Document]:
    vs = build_notes_vectorstore()
    if vs is None:
        return []
    return vs.similarity_search(query, k=k)


def gather_from_web(query: str, k: int = 5) -> List[Document]:
    if not TAVILY_API_KEY:
        return []

    search = TavilySearch(max_results=k)
    results = search.invoke(query)

    docs = []
    for text in results:
        if not text:
            continue
        docs.append(Document(page_content=text, metadata={"source": "web"}))
    return docs


# app/core/context_gatherer.py
from typing import List, Tuple
from langchain_core.documents import Document

# existing helpers: gather_from_notes, gather_from_web must already exist

def gather_context_for_checkpoint(topic: str, objectives: List[str], attempt: int, user_query: str = None) -> Tuple[List[Document], str]:
    """
    When user_query is provided, prefer web results first so free-text queries return web facts.
    """
    canonical_q = f"{topic}. Focus on: " + "; ".join(objectives)

    # If user provided a custom query, prefer web first
    if user_query and user_query.strip():
        uq = user_query.strip()
        if attempt == 1:
            web_docs = gather_from_web(uq, k=5)
            if web_docs:
                return web_docs, "web:user"
            notes_docs = gather_from_notes(uq, k=5)
            if notes_docs:
                return notes_docs, "notes:user"
            return [], "none"
        elif attempt == 2:
            notes_docs = gather_from_notes(uq, k=5)
            if notes_docs:
                return notes_docs, "notes:user"
            web_docs = gather_from_web(uq, k=5)
            if web_docs:
                return web_docs, "web:user"
            return [], "none"
        else:
            # mixed: combine web + notes for user query + canonical
            web_docs = gather_from_web(uq, k=5) + gather_from_web(canonical_q, k=3)
            notes_docs = gather_from_notes(uq, k=5) + gather_from_notes(canonical_q, k=3)
            all_docs = web_docs + notes_docs
            return (all_docs, "mixed:user") if all_docs else ([], "none")

    # fallback to original (no user_query) behavior
    query = canonical_q
    notes_docs = gather_from_notes(query, k=5)
    if attempt == 1:
        if notes_docs:
            return notes_docs, "notes"
        web_docs = gather_from_web(query, k=5)
        if web_docs:
            return web_docs, "web"
        return [], "none"
    elif attempt == 2:
        web_docs = gather_from_web(query, k=5)
        if web_docs:
            return web_docs, "web"
        if notes_docs:
            return notes_docs, "notes"
        return [], "none"
    else:
        web_docs = gather_from_web(query, k=5)
        all_docs = (notes_docs or []) + (web_docs or [])
        if all_docs:
            return all_docs, "mixed"
        return [], "none"


    # No user_query: original behavior
    query = canonical_q
    notes_docs = gather_from_notes(query, k=5)
    if attempt == 1:
        if notes_docs:
            return notes_docs, "notes"
        web_docs = gather_from_web(query, k=5)
        if web_docs:
            return web_docs, "web"
        return [], "none"
    elif attempt == 2:
        web_docs = gather_from_web(query, k=5)
        if web_docs:
            return web_docs, "web"
        if notes_docs:
            return notes_docs, "notes"
        return [], "none"
    else:
        web_docs = gather_from_web(query, k=5)
        all_docs = (notes_docs or []) + (web_docs or [])
        if all_docs:
            return all_docs, "mixed"
        return [], "none"
