from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


def build_vector_index(text: str):
    """
    Convert study material into a searchable vector index
    using chunking + embeddings + FAISS.
    """

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    documents = [Document(page_content=text)]
    chunks = splitter.split_documents(documents)

    vector_index = FAISS.from_documents(chunks, embeddings)
    return vector_index
