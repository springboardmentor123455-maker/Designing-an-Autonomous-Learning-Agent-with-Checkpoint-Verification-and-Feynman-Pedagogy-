"""Vector store manager for context embedding and similarity search (Milestone 2)."""
from typing import List, Optional
import numpy as np
from langchain_community.vectorstores import FAISS
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document


class VectorStoreManager:
    
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the vector store manager.
        
        Args:
            model_name: HuggingFace model name for embeddings
        """
        print(f"Initializing embeddings with model: {model_name}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("Embeddings initialized successfully")
    
    def create_vector_store(self, text_chunks: List[str]) -> FAISS:
        """
        Create a FAISS vector store from text chunks.
        
        Args:
            text_chunks: List of text chunks to embed
            
        Returns:
            FAISS vector store
        """
        if not text_chunks:
            raise ValueError("No text chunks provided")
        
        print(f"\nEmbedding {len(text_chunks)} chunks...")
        
        # Create documents
        documents = [
            Document(page_content=chunk, metadata={"chunk_id": i})
            for i, chunk in enumerate(text_chunks)
        ]
        
        # Create vector store
        vector_store = FAISS.from_documents(documents, self.embeddings)
        
        print(f"Vector store created with {len(text_chunks)} embeddings")
        return vector_store
    
    def similarity_search(
        self,
        vector_store: FAISS,
        query: str,
        k: int = 3
    ) -> List[Document]:
        """
        Perform similarity search in the vector store.
        
        Args:
            vector_store: FAISS vector store
            query: Query text
            k: Number of results to return
            
        Returns:
            List of most similar documents
        """
        results = vector_store.similarity_search(query, k=k)
        return results
    
    def get_relevant_context(
        self,
        vector_store: FAISS,
        objectives: List[str],
        k_per_objective: int = 2
    ) -> str:
        """
        Get relevant context for multiple objectives.
        
        Args:
            vector_store: FAISS vector store
            objectives: List of learning objectives
            k_per_objective: Number of chunks per objective
            
        Returns:
            Combined relevant context
        """
        all_contexts = []
        seen_contents = set()  # Deduplicate
        
        for objective in objectives:
            results = self.similarity_search(vector_store, objective, k=k_per_objective)
            for doc in results:
                content = doc.page_content
                if content not in seen_contents:
                    all_contexts.append(content)
                    seen_contents.add(content)
        
        return "\n\n".join(all_contexts)
