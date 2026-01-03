from langchain_community.vectorstores import Chroma

def create_in_memory_chroma(embeddings, collection_name: str = "checkpoint"):
    # persist_directory=None ⇒ in-memory only
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=None,
    )
