# src/validator.py

ARRAY_KEYWORDS = [
    "array", "index", "element", "elements",
    "contiguous", "memory", "access",
    "traversal", "size", "length"
]

BINARY_SEARCH_KEYWORDS = [
    "binary search", "sorted", "mid",
    "middle", "divide", "halve", "log"
]

TWO_POINTER_KEYWORDS = [
    "two pointer", "left", "right",
    "start", "end", "move", "increment", "decrement"
]

RELEVANCE_KEYWORD_THRESHOLD = 4


def validate_context(state):
    print("🧪 Validating context...")

    context = state.get("context", "").lower()

    keywords = (
        ARRAY_KEYWORDS +
        BINARY_SEARCH_KEYWORDS +
        TWO_POINTER_KEYWORDS
    )

    matches = sum(1 for kw in keywords if kw in context)

    relevance_score = min(1.0, matches / RELEVANCE_KEYWORD_THRESHOLD)

    state["relevance_score"] = round(relevance_score, 2)

    print(f"📊 Relevance score: {state['relevance_score']}")
    return state
