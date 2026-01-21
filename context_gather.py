from langchain_tavily import TavilySearch


def gather_context(state):
    print("🔍 Gathering context...")

    checkpoint = state["checkpoint"]
    topic = checkpoint["topic"]
    objectives = checkpoint.get("objectives", [])

    user_notes = state.get("user_notes", "")
    if user_notes and len(user_notes.strip()) > 50:
        state["context"] = user_notes
        state["context_source"] = "user_notes"
        return state

    print("🌐 Using Tavily web search")
    search = TavilySearch(k=3)

    if objectives:
        query = f"{topic}. Learning objectives: {', '.join(objectives)}"
    else:
        query = f"{topic} explanation and complexity"

    results = search.invoke(query)

    texts = []

    if isinstance(results, list):
        for r in results:
            texts.append(r.get("content") or r.get("snippet", ""))
    elif isinstance(results, dict):
        for r in results.get("results", []):
            texts.append(r.get("content") or r.get("snippet", ""))

    state["context"] = "\n".join(texts)
    state["context_source"] = "web_search"

    return state
