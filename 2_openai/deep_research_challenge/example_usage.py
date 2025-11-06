"""
Example usage of the Autonomous Deep Research System.
Run this to test the system with a simple query.
"""
import asyncio
from dotenv import load_dotenv
from research_coordinator import ResearchCoordinator
from budget import ResearchBudget
from config import ResearchConfig
from logging_config import setup_logging

load_dotenv(override=True)


async def simple_research_example():
    """Simple research example with development budget."""
    print("=" * 60)
    print("Autonomous Deep Research - Simple Example")
    print("=" * 60)
    
    # Setup logging
    setup_logging(log_level="INFO", log_to_file=True)
    
    # Create coordinator with development config
    config = ResearchConfig.create_development()
    coordinator = ResearchCoordinator(config)
    
    # Create tight budget for testing
    budget = ResearchBudget.create_development()
    
    print(f"\nBudget: {budget}")
    print(f"Config: Development mode")
    print("\nStarting research...\n")
    
    # Run research
    query = "What is the future of AI agents?"
    
    async for update in coordinator.conduct_research(query, budget):
        print(f"\n{update}\n")
        print("-" * 60)
    
    print("\n" + "=" * 60)
    print("Research Complete!")
    print("=" * 60)


async def custom_budget_example():
    """Example with custom budget settings."""
    print("=" * 60)
    print("Custom Budget Example")
    print("=" * 60)
    
    # Create custom budget
    budget = ResearchBudget(
        max_tokens=5000,      # Very tight for quick test
        max_time_seconds=30.0,
        max_api_calls=5,
        max_trail_depth=0     # No trails
    )
    
    config = ResearchConfig.create_development()
    coordinator = ResearchCoordinator(config)
    
    print(f"\nCustom Budget: {budget}")
    print("\nStarting research...\n")
    
    query = "Explain quantum computing in simple terms"
    
    async for update in coordinator.conduct_research(query, budget):
        print(f"\n{update}\n")


async def production_example():
    """Example with production settings (WARNING: Higher costs)."""
    print("=" * 60)
    print("Production Example - WARNING: Higher Costs!")
    print("=" * 60)
    
    response = input("This will use production budget. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return
    
    config = ResearchConfig.create_production()
    coordinator = ResearchCoordinator(config)
    budget = ResearchBudget.create_production()
    
    print(f"\nProduction Budget: {budget}")
    print("\nStarting comprehensive research...\n")
    
    query = "What are the latest developments in renewable energy?"
    
    async for update in coordinator.conduct_research(query, budget):
        print(f"\n{update}\n")


if __name__ == "__main__":
    print("\nSelect example to run:")
    print("1. Simple research (Development mode, ~$0.10-0.30)")
    print("2. Custom budget (Very tight, ~$0.05-0.15)")
    print("3. Production mode (Full features, ~$2-6)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(simple_research_example())
    elif choice == "2":
        asyncio.run(custom_budget_example())
    elif choice == "3":
        asyncio.run(production_example())
    else:
        print("Invalid choice")
