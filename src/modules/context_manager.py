"""Context management module for gathering and validating learning materials."""
from typing import List, Tuple, Optional
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.models.checkpoint import Checkpoint, GatheredContext
from src.utils.llm_provider import get_llm, get_reasoning_llm, get_validation_llm
from src.utils.search_tools import search_for_learning_content


class ContextManager:
    """
    Manages gathering and validation of learning context.
    
    Prioritizes user-provided notes, then falls back to web search.
    Validates that gathered content is relevant to checkpoint objectives.
    Includes deduplication to prevent duplicate results across retries.
    """
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        """
        Initialize the context manager.
        
        Args:
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between chunks
        """
        self.llm = get_llm()
        self.reasoning_llm = get_reasoning_llm()
        self.validation_llm = get_validation_llm()  # Fast model for scoring
        self._seen_urls = set()  # Track seen URLs for deduplication
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def gather_context(
        self,
        checkpoint: Checkpoint,
        user_notes: Optional[str] = None,
        max_web_results: int = 6
    ) -> List[GatheredContext]:
        """
        Gather learning context from available sources.
        
        Prioritizes user notes, then performs web search if needed.
        
        Args:
            checkpoint: The checkpoint to gather context for
            user_notes: Optional user-provided notes
            max_web_results: Maximum number of web search results
            
        Returns:
            List of GatheredContext objects
        """
        contexts = []
        
        # 1. Process user notes if provided
        if user_notes and user_notes.strip():
            print("Processing user-provided notes...")
            contexts.append(GatheredContext(
                source="user_notes",
                content=user_notes,
                gathered_at=datetime.now(),
                metadata={"length": len(user_notes)}
            ))
        
        # 2. Perform web search with deduplication
        print(f"Searching web for: {checkpoint.topic}")
        search_results = search_for_learning_content(
            topic=checkpoint.topic,
            objectives=checkpoint.objectives,
            max_results=max_web_results
        )
        
        # Filter out duplicate URLs we've seen before
        unique_results = 0
        for result in search_results:
            url = result.get('url', '')
            content = result.get('content', '')
            
            # Skip if we've seen this URL or if there's no content
            if not content:
                continue
            if url and url in self._seen_urls:
                print(f"  Skipping duplicate: {url[:50]}...")
                continue
                
            # Add to seen URLs and contexts
            if url:
                self._seen_urls.add(url)
            
            contexts.append(GatheredContext(
                source="web_search",
                content=content,
                url=url,
                gathered_at=datetime.now(),
                metadata={
                    'title': result.get('title', ''),
                    'search_score': result.get('score', 0.0)
                }
            ))
            unique_results += 1
        
        print(f"  Added {unique_results} new unique results ({len(self._seen_urls)} total URLs seen)")
        
        print(f"Gathered {len(contexts)} context sources")
        return contexts
    
    def reset_deduplication_cache(self):
        """Reset the deduplication cache for fresh searches."""
        self._seen_urls.clear()
        print("Deduplication cache cleared")
    
    def validate_context(
        self,
        checkpoint: Checkpoint,
        contexts: List[GatheredContext]
    ) -> Tuple[bool, str, List[GatheredContext]]:
        """
        Validate that gathered context is relevant to checkpoint objectives.
        
        Uses LLM to assess relevance and assign scores.
        
        Args:
            checkpoint: The checkpoint being studied
            contexts: List of gathered contexts
            
        Returns:
            Tuple of (is_valid, message, scored_contexts)
            - is_valid: Whether context is sufficient and relevant
            - message: Explanation of validation result
            - scored_contexts: Contexts with relevance scores assigned
        """
        if not contexts:
            return False, "No context gathered", []
        
        print("Validating context relevance...")
        
        # Score each context for relevance
        scored_contexts = []
        for context in contexts:
            score = self._score_context_relevance(checkpoint, context)
            context.relevance_score = score
            scored_contexts.append(context)
        
        # Calculate average relevance
        avg_relevance = sum(c.relevance_score for c in scored_contexts) / len(scored_contexts)
        
        # Check if we have sufficient relevant content (lowered threshold)
        relevant_contexts = [c for c in scored_contexts if c.relevance_score >= 0.4]
        
        if len(relevant_contexts) == 0:
            return (
                False,
                f"No sufficiently relevant content found (avg relevance: {avg_relevance:.2f})",
                scored_contexts
            )
        
        if avg_relevance < 0.35:
            return (
                False,
                f"Context relevance too low (avg: {avg_relevance:.2f}). Need more relevant sources.",
                scored_contexts
            )
        
        return (
            True,
            f"Context validated successfully (avg relevance: {avg_relevance:.2f}, {len(relevant_contexts)} relevant sources)",
            scored_contexts
        )
    
    def _score_context_relevance(
        self,
        checkpoint: Checkpoint,
        context: GatheredContext
    ) -> float:
        """
        Score a single context for relevance to checkpoint objectives.
        
        Args:
            checkpoint: The checkpoint
            context: The context to score
            
        Returns:
            Relevance score (0-1)
        """
        # Create prompt for relevance scoring
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at assessing educational content relevance.
            
Score how useful this content is for learning the topic and objectives.
Be generous - if content has ANY useful information related to the topic, give a decent score.

Provide ONLY a number from 0.0 to 1.0 where:
- 0.0-0.2: Completely unrelated
- 0.3-0.5: Marginally relevant, mentions topic briefly
- 0.6-0.8: Relevant, provides useful information
- 0.9-1.0: Highly relevant, directly addresses objectives

Respond with ONLY the numeric score, nothing else."""),
            ("user", """Topic: {topic}

Learning Objectives:
{objectives}

Content to Score:
{content}

Score (0.0-1.0):""")
        ])
        
        chain = prompt | self.validation_llm | StrOutputParser()
        
        try:
            # Truncate content if too long
            content_preview = context.content[:1500]
            if len(context.content) > 1500:
                content_preview += "...[truncated]"
            
            objectives_text = "\n".join(f"- {obj}" for obj in checkpoint.objectives)
            
            result = chain.invoke({
                "topic": checkpoint.topic,
                "objectives": objectives_text,
                "content": content_preview
            })
            
            # Extract score from result
            score_text = result.strip()
            score = float(score_text)
            
            # Clamp to 0-1 range
            score = max(0.0, min(1.0, score))
            
            print(f"  Scored {context.source}: {score:.2f}")
            return score
            
        except Exception as e:
            print(f"Error scoring context: {e}")
            # Default to moderate score on error
            return 0.5
    
    def chunk_contexts(
        self,
        contexts: List[GatheredContext]
    ) -> List[str]:
        """
        Chunk contexts into smaller pieces for processing.
        
        Args:
            contexts: List of contexts to chunk
            
        Returns:
            List of text chunks
        """
        all_chunks = []
        
        for context in contexts:
            # Only chunk relevant contexts (lowered threshold)
            if context.relevance_score and context.relevance_score >= 0.4:
                chunks = self.text_splitter.split_text(context.content)
                all_chunks.extend(chunks)
        
        print(f"Created {len(all_chunks)} text chunks from contexts")
        return all_chunks
    
    def summarize_context(
        self,
        contexts: List[GatheredContext],
        checkpoint: Checkpoint
    ) -> str:
        """
        Create a summary of the gathered context relevant to the checkpoint.
        
        Args:
            contexts: List of gathered contexts
            checkpoint: The checkpoint
            
        Returns:
            Summary text
        """
        # Filter to relevant contexts (lowered threshold)
        relevant_contexts = [c for c in contexts if c.relevance_score and c.relevance_score >= 0.4]
        
        if not relevant_contexts:
            return "No relevant context available."
        
        # Combine content
        combined_content = "\n\n".join(
            f"Source: {c.source}\n{c.content[:500]}..."
            for c in relevant_contexts[:3]  # Use top 3 most relevant
        )
        
        # Create summary prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert educator creating a concise summary of learning materials.
            
Create a clear, focused summary that covers the key points relevant to the learning objectives.
Keep the summary concise but informative (3-5 paragraphs)."""),
            ("user", """Topic: {topic}

Learning Objectives:
{objectives}

Source Materials:
{content}

Create a summary focusing on the learning objectives:""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            objectives_text = "\n".join(f"- {obj}" for obj in checkpoint.objectives)
            
            summary = chain.invoke({
                "topic": checkpoint.topic,
                "objectives": objectives_text,
                "content": combined_content
            })
            
            return summary
            
        except Exception as e:
            print(f"Error creating summary: {e}")
            return "Error creating context summary."
