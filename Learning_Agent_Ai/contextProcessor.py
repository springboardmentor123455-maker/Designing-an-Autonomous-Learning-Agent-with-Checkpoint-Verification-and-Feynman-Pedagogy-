from typing import List

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langsmith import traceable

load_dotenv()


class ContextProcessor:
    @traceable(name="chunk")
    def chunk(self, text):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=50
        )
        return splitter.split_text(text)
    
class SessionVectorStore:
    """
    Temporary vector store for a single learning session.

    Responsibilities:
    - Convert text chunks into embeddings
    - Store embeddings in memory
    - Support similarity search (optional, future use)
    """
    def __init__(self):
        self.store = None

    @traceable(name="create")
    def create(self, chunks: List[str]) -> None:
        """
        Create a FAISS vector store from text chunks.

        Args:
            chunks (List[str]): Chunked context text
        """
        if not chunks:
            raise ValueError("Cannot create vector store with empty chunks.")

        embeddings = NVIDIAEmbeddings(model="nvidia/nv-embed-v1")
        self.store = FAISS.from_texts(chunks, embeddings)
        return self.store

    @traceable(name="similarity_search")
    def similarity_search(self, query: str, k: int = 3) -> List[str]:
        """
        Retrieve top-k most relevant chunks.

        Args:
            query (str): Search query
            k (int): Number of results

        Returns:
            List[str]: Relevant text chunks
        """
        if not self.store:
            return []

        docs = self.store.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]