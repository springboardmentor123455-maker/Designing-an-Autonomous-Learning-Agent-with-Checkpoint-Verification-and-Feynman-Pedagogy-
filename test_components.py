"""Test individual components of the learning agent."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.checkpoint import Checkpoint, GatheredContext
from src.models.state import create_initial_state
from src.modules.context_manager import ContextManager
from datetime import datetime


def test_checkpoint_creation():
    """Test creating a checkpoint."""
    print("Testing checkpoint creation...")
    checkpoint = Checkpoint(
        topic="Test Topic",
        objectives=["Learn A", "Learn B"],
        difficulty_level="beginner"
    )
    assert checkpoint.topic == "Test Topic"
    assert len(checkpoint.objectives) == 2
    print("✓ Checkpoint creation works")


def test_gathered_context():
    """Test GatheredContext model."""
    print("Testing GatheredContext model...")
    context = GatheredContext(
        source="test",
        content="Test content",
        gathered_at=datetime.now(),
        metadata={"key": "value"}
    )
    assert context.source == "test"
    assert context.content == "Test content"
    print("✓ GatheredContext model works")


def test_state_creation():
    """Test creating initial state."""
    print("Testing state creation...")
    checkpoint = Checkpoint(
        topic="Python Basics",
        objectives=["Learn syntax"]
    )
    state = create_initial_state(checkpoint)
    assert state["checkpoint"] == checkpoint
    assert state["retry_count"] == 0
    print("✓ State creation works")


def test_context_manager():
    """Test context manager initialization."""
    print("Testing context manager initialization...")
    manager = ContextManager(chunk_size=1000)
    assert manager.chunk_size == 1000
    print("✓ Context manager initialization works")


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING COMPONENT TESTS")
    print("=" * 60)
    print()
    
    test_checkpoint_creation()
    test_gathered_context()
    test_state_creation()
    test_context_manager()
    
    print()
    print("=" * 60)
    print("✅ ALL COMPONENT TESTS PASSED!")
    print("=" * 60)
