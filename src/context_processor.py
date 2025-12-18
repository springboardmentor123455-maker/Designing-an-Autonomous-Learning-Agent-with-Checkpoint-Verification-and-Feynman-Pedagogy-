"""
Context processing utilities for the Learning Agent System.

This module handles text chunking, embedding generation, and vector database
operations using ChromaDB and HuggingFace sentence transformers.
"""

import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from .models import ProcessedContext

logger = logging.getLogger(__name__)

class ContextProcessor:
    """Handles context processing, chunking, and embedding generation."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize the context processor."""
        self.embedding_model = SentenceTransformer(model_name)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
    def chunk_text(self, text: str) -> List[str]:
        """Split text into manageable chunks."""
        return self.text_splitter.split_text(text)
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks."""
        embeddings = self.embedding_model.encode(texts)
        return embeddings.tolist()
    
    def store_in_vector_db(self, chunks: List[str], embeddings: List[List[float]], 
                          metadata: List[Dict[str, Any]], collection_name: str):
        """Store chunks and embeddings in ChromaDB."""
        try:
            # Get or create collection
            collection = self.chroma_client.get_or_create_collection(name=collection_name)
            
            # Generate IDs
            ids = [f"chunk_{i}" for i in range(len(chunks))]
            
            # Store in ChromaDB
            collection.add(
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadata,
                ids=ids
            )
            
            logger.info(f"Stored {len(chunks)} chunks in collection '{collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error storing in vector DB: {e}")
            return False
    
    async def process_context(self, content: str, checkpoint_id: str) -> List[ProcessedContext]:
        """Process content into chunks with embeddings."""
        try:
            # Chunk the text
            chunks = self.chunk_text(content)
            logger.info(f"Created {len(chunks)} chunks from content")
            
            # Generate embeddings
            embeddings = self.generate_embeddings(chunks)
            logger.info(f"Generated embeddings with dimension {len(embeddings[0]) if embeddings else 0}")
            
            # Prepare metadata
            metadata = [{"checkpoint_id": checkpoint_id, "chunk_index": i} for i in range(len(chunks))]
            
            # Store in vector database
            collection_name = f"checkpoint_{checkpoint_id}"
            self.store_in_vector_db(chunks, embeddings, metadata, collection_name)
            
            # Create processed context objects
            processed_context = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                processed_context.append({
                    "chunk_id": f"chunk_{i}",
                    "text": chunk,
                    "embedding": embedding,
                    "metadata": metadata[i]
                })
            
            return processed_context
            
        except Exception as e:
            logger.error(f"Error processing context: {e}")
            raise