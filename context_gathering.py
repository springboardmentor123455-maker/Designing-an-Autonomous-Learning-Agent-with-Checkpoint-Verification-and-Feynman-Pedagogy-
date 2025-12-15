# context_gathering.py

def get_context_from_user_notes(notes):
    if notes:
        return notes
    return None


def get_context_from_web(topic):
    # Dummy web search (real API later)
    return f"Web information about {topic}: This topic covers basic concepts."


def gather_context(topic, user_notes=None):
    context = get_context_from_user_notes(user_notes)
    
    if context:
        source = "User Notes"
    else:
        context = get_context_from_web(topic)
        source = "Web Search"

    return {
        "topic": topic,
        "context": context,
        "source": source
    }
