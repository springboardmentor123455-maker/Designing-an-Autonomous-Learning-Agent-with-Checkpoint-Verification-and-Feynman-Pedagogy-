from duckduckgo_search import DDGS


def web_search(query: str, max_results: int = 5) -> str:
    """
    Returns concatenated snippets from DuckDuckGo search results.
    Completely free, no API key.
    If DuckDuckGo rate-limits or fails, we just return an empty string
    so the rest of the pipeline can still run.
    """
    texts = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                snippet = r.get("body") or r.get("snippet") or ""
                if snippet:
                    texts.append(snippet)
    except Exception as e:
        # Generic catch so it works across all versions
        print(f"[WEB_SEARCH] DuckDuckGo error: {e}")
        return ""

    return "\n\n".join(texts)
