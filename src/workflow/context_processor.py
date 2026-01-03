from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..state_types import AgentState
from ..tools.embeddings import get_embeddings
from ..tools.vector_store import create_in_memory_chroma



def process_context(state: AgentState) -> AgentState:
    docs = state["context_docs"]
    full_text = "\n\n".join(docs)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
    )
    chunks = splitter.split_text(full_text)

    embeddings = get_embeddings()
    vs = create_in_memory_chroma(embeddings, collection_name="cp_" + str(state["checkpoint"]["id"]))
    vs.add_texts(chunks)

    state["vector_store"] = vs
    return state
