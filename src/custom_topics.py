"""
Custom Topics Management for Learning Agent System.

Handles creation, storage, and retrieval of custom learning topics
defined by users.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

CUSTOM_TOPICS_FILE = Path(__file__).parent.parent / "custom_topics.json"

def load_custom_topics() -> List[Dict[str, Any]]:
    """Load custom topics from JSON file."""
    if not CUSTOM_TOPICS_FILE.exists():
        return []
    
    try:
        with open(CUSTOM_TOPICS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_custom_topics(topics: List[Dict[str, Any]]) -> bool:
    """Save custom topics to JSON file."""
    try:
        with open(CUSTOM_TOPICS_FILE, 'w', encoding='utf-8') as f:
            json.dump(topics, f, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False

def add_custom_topic(topic: Dict[str, Any]) -> bool:
    """Add a new custom topic."""
    topics = load_custom_topics()
    
    # Check if topic ID already exists
    if any(t['id'] == topic['id'] for t in topics):
        return False
    
    topics.append(topic)
    return save_custom_topics(topics)

def get_custom_topic(topic_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific custom topic by ID."""
    topics = load_custom_topics()
    return next((t for t in topics if t['id'] == topic_id), None)

def delete_custom_topic(topic_id: str) -> bool:
    """Delete a custom topic by ID."""
    topics = load_custom_topics()
    filtered = [t for t in topics if t['id'] != topic_id]
    
    if len(filtered) == len(topics):
        return False  # Topic not found
    
    return save_custom_topics(filtered)

def create_topic_wizard() -> Optional[Dict[str, Any]]:
    """Interactive wizard for creating a custom topic (CLI)."""
    print("\n=== Create Custom Learning Topic ===\n")
    
    topic_id = input("Topic ID (e.g., 'python_basics'): ").strip()
    if not topic_id:
        print("Topic ID is required.")
        return None
    
    title = input("Topic Title: ").strip()
    if not title:
        print("Title is required.")
        return None
    
    description = input("Description: ").strip()
    if not description:
        print("Description is required.")
        return None
    
    print("\nHow many checkpoints? (1-10): ", end="")
    try:
        num_checkpoints = int(input().strip())
        if num_checkpoints < 1 or num_checkpoints > 10:
            print("Please enter a number between 1 and 10.")
            return None
    except ValueError:
        print("Invalid number.")
        return None
    
    checkpoints = []
    for i in range(num_checkpoints):
        print(f"\n--- Checkpoint {i+1} ---")
        cp_title = input("  Title: ").strip()
        cp_desc = input("  Description: ").strip()
        
        print("  Requirements (one per line, empty line to finish):")
        requirements = []
        while True:
            req = input("    > ").strip()
            if not req:
                break
            requirements.append(req)
        
        if cp_title and cp_desc and requirements:
            checkpoints.append({
                "id": f"{topic_id}_cp_{i+1}",
                "title": cp_title,
                "description": cp_desc,
                "requirements": requirements
            })
    
    if len(checkpoints) != num_checkpoints:
        print("Not all checkpoints were completed.")
        return None
    
    return {
        "id": topic_id,
        "title": title,
        "description": description,
        "checkpoints": checkpoints
    }
