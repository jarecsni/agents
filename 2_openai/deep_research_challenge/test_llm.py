#!/usr/bin/env python
"""
Test script for LLM calls with development budget.
This will make actual API calls and incur costs (~$0.10-0.30).
"""
import asyncio
import sys
import os

# Ensure we can import from current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

load_dotenv(override=True)

# Now import our modules (after path is set)
from research_coordinator import ResearchCoordinator
from budget import ResearchBudget
from config import ResearchConfig
from logging_config import setup_logging


async def test_llm_calls():
    """Test with actual LLM calls using development budget."""
    print("=" * 60)
    print("LLM Integration Test - Development Mode")
    print("=" * 60)
    print()
    print("⚠️  This will make actual API calls")
    print("Estimated cost: $0.10 - $0.30")
    print()
    
    # Setup
    setup_logging(log_level='INFO', log_to_file=True)
    
    config = ResearchConfig.create_development()
    coordinator = ResearchCoordinator(config)
    budget = ResearchBudget.create_development()
    
    print(f"Budget: {budget}")
    print("=" * 60)
    print()
    
    # Simple test query
    query = "What is quantum computing?"
    print(f"Query: {query}")
    print("=" * 60)
    print()
    
    try:
        async for update in coordinator.conduct_research(query, budget):
            print(update)
            print("-" * 60)
            print()
        
        print()
        print("=" * 60)
        print("✅ Test Complete!")
        print("=" * 60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Test Failed: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print()
    response = input("Run LLM test? This will cost ~$0.10-0.30 (yes/no): ")
    if response.lower() == 'yes':
        asyncio.run(test_llm_calls())
    else:
        print("Test cancelled.")
