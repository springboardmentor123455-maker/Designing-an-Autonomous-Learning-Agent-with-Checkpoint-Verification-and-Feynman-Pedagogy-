#!/usr/bin/env python3
"""
Test script for LangSmith integration validation.

This script tests the LangSmith tracing functionality and validates
that the integration is working properly with the Learning Agent System.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv
load_dotenv()

from src.langsmith_config import langsmith_config, trace_llm_operation, trace_workflow_node
from src.sample_data import create_multiple_checkpoints, create_sample_materials
from src.main import run_learning_session

@trace_llm_operation("test_operation")
async def test_llm_tracing():
    """Test LLM operation tracing."""
    print("Testing LLM operation tracing...")
    await asyncio.sleep(0.1)  # Simulate LLM call
    return {"test": "result"}

@trace_workflow_node("test_node")
async def test_workflow_tracing(state):
    """Test workflow node tracing."""
    print("Testing workflow node tracing...")
    state["test_completed"] = True
    return state

async def test_langsmith_integration():
    """Test LangSmith integration end-to-end."""
    
    print("🧪 LANGSMITH INTEGRATION TEST")
    print("=" * 50)
    
    # Test 1: Configuration validation
    print("\n1️⃣ Testing LangSmith Configuration...")
    print(f"   LangSmith Enabled: {langsmith_config.enabled}")
    print(f"   Project Name: {langsmith_config.project}")
    print(f"   API Key Present: {'✅' if langsmith_config.api_key else '❌'}")
    
    if not langsmith_config.enabled:
        print("   ⚠️ LangSmith is disabled. Check .env configuration.")
        return False
    
    # Test 2: Tracing decorators
    print("\n2️⃣ Testing Tracing Decorators...")
    try:
        # Test LLM operation tracing
        await test_llm_tracing()
        print("   ✅ LLM operation tracing works")
        
        # Test workflow node tracing
        test_state = {"workflow_step": "testing"}
        result = await test_workflow_tracing(test_state)
        print("   ✅ Workflow node tracing works")
        
    except Exception as e:
        print(f"   ❌ Tracing decorator error: {e}")
        return False
    
    # Test 3: Learning session with tracing
    print("\n3️⃣ Testing Learning Session with Tracing...")
    try:
        checkpoints = create_multiple_checkpoints()
        materials = create_sample_materials()
        
        # Run a minimal learning session
        result = await run_learning_session(
            checkpoint=checkpoints[0], 
            materials=materials[:1]  # Use just one material for testing
        )
        
        print("   ✅ Learning session completed with tracing")
        print(f"   📊 Workflow completed: {result.get('workflow_step', 'unknown')}")
        
    except Exception as e:
        print(f"   ❌ Learning session error: {e}")
        return False
    
    print("\n✅ LangSmith integration test completed successfully!")
    print("\n📈 Check your LangSmith dashboard at: https://smith.langchain.com")
    print(f"   Project: {langsmith_config.project}")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_langsmith_integration())
    sys.exit(0 if success else 1)