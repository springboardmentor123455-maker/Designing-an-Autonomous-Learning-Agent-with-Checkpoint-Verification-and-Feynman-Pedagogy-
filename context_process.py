from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import FakeEmbeddings
from langchain_community.vectorstores import FAISS


def process_context(state):
    print("✂️ Processing context...")

    context = state.get("context", "")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )

    chunks = splitter.split_text(context)

    embeddings = FakeEmbeddings(size=384)
    vectorstore = FAISS.from_texts(chunks, embeddings)

    state["chunks"] = chunks
    state["vectorstore"] = vectorstore

    print(f"📦 Chunks created: {len(chunks)}")
    return state
