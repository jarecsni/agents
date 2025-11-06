"""
Integration tests for the Autonomous Deep Research System.
Tests infrastructure without expensive LLM calls.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Test imports
import models
import budget
import config
import state_machine
import agent_registry
import trail_manager
import trail_discovery
import clarification_engine

from models import (
    ResearchContext, ResearchState, Finding, Gap, QualityScore,
    HandoffRecord, ResearchTrail, TrailStatus, Capability, ResourceUsage
)
from budget import ResearchBudget, Operation
from config import ResearchConfig
from state_machine import ResearchStateMachine, StateTransitionError
from agent_registry import AgentRegistry
from trail_manager import TrailManager
from trail_discovery import TrailDiscovery
from clarification_engine import ClarificationEngine


def test_models():
    """Test core data models."""
    print("Testing models...")
    
    # Test ResearchContext
    context = ResearchContext(query="test query")
    assert context.query == "test query"
    assert context.state == ResearchState.INITIALIZING
    
    # Test serialization
    context_dict = context.to_dict()
    context_restored = ResearchContext.from_dict(context_dict)
    assert context_restored.query == context.query
    
    # Test adding findings
    finding = Finding(
        id="test-1",
        content="test content",
        source="test source",
        timestamp=datetime.now()
    )
    context.add_finding(finding)
    assert len(context.findings) == 1
    
    print("✓ Models test passed")


def test_budget():
    """Test budget management."""
    print("Testing budget...")
    
    budget = ResearchBudget(
        max_tokens=1000,
        max_time_seconds=60.0,
        max_api_calls=10,
        max_trail_depth=2
    )
    
    # Test can_afford
    op = Operation("test", estimated_tokens=100)
    assert budget.can_afford(op)
    
    # Test consume
    budget.consume(op)
    assert budget.current_usage.tokens_used == 100
    
    # Test utilization
    util = budget.utilization_percent()
    assert util['tokens'] == 10.0  # 100/1000 = 10%
    
    # Test remaining
    remaining = budget.remaining()
    assert remaining.tokens_used == 900
    
    # Test trail allocation
    trail_budget = budget.allocate_for_trail(percentage=0.2)
    assert trail_budget.max_tokens == int(900 * 0.2)
    
    print("✓ Budget test passed")


def test_state_machine():
    """Test state machine transitions."""
    print("Testing state machine...")
    
    context = ResearchContext(query="test")
    sm = ResearchStateMachine(context)
    
    # Test valid transition
    assert sm.can_transition(ResearchState.PLANNING)
    sm.transition(ResearchState.PLANNING)
    assert context.state == ResearchState.PLANNING
    
    # Test invalid transition
    assert not sm.can_transition(ResearchState.COMPLETED)
    try:
        sm.transition(ResearchState.COMPLETED)
        assert False, "Should have raised StateTransitionError"
    except StateTransitionError:
        pass
    
    # Test terminal state
    sm.transition(ResearchState.SEARCHING)
    sm.transition(ResearchState.EVALUATING)
    sm.transition(ResearchState.SYNTHESIZING)
    sm.transition(ResearchState.COMPLETED)
    assert sm.is_terminal_state()
    
    print("✓ State machine test passed")


def test_agent_registry():
    """Test agent registry."""
    print("Testing agent registry...")
    
    from agents import Agent
    
    registry = AgentRegistry()
    
    # Create mock agent
    test_agent = Agent(
        name="TestAgent",
        instructions="Test instructions",
        model="gpt-4o-mini"
    )
    
    # Test registration
    registry.register_agent(
        "test_agent",
        test_agent,
        [Capability.SEARCHING],
        "Test agent"
    )
    
    assert len(registry) == 1
    assert "test_agent" in registry
    
    # Test capability lookup
    agent_info = registry.get_agent_for_capability(Capability.SEARCHING)
    assert agent_info is not None
    assert agent_info.agent_id == "test_agent"
    
    # Test health status
    health = registry.get_health_status()
    assert "test_agent" in health
    assert health["test_agent"]["available"]
    
    print("✓ Agent registry test passed")


def test_trail_manager():
    """Test trail management."""
    print("Testing trail manager...")
    
    manager = TrailManager(max_concurrent_trails=2)
    
    budget = ResearchBudget.create_development()
    
    # Test trail creation
    trail = manager.create_trail(
        trail_query="test trail",
        relevance_score=0.8,
        budget=budget
    )
    
    assert trail is not None
    assert trail.status == TrailStatus.PENDING
    
    # Test starting trail
    assert manager.start_trail(trail.id)
    assert trail.status == TrailStatus.ACTIVE
    
    # Test loop prevention
    trail2 = manager.create_trail(
        trail_query="test trail",  # Same query
        relevance_score=0.7,
        budget=budget
    )
    assert trail2 is None  # Should be rejected as duplicate
    
    # Test completing trail
    assert manager.complete_trail(trail.id)
    assert trail.status == TrailStatus.COMPLETED
    
    # Test statistics
    stats = manager.get_statistics()
    assert stats['total_trails'] == 1
    assert stats['completed_trails'] == 1
    
    print("✓ Trail manager test passed")


def test_trail_discovery():
    """Test trail discovery."""
    print("Testing trail discovery...")
    
    discovery = TrailDiscovery(min_relevance=0.5)
    
    # Create test findings
    findings = [
        Finding(
            id="f1",
            content="This is related to quantum computing and AI",
            source="test",
            timestamp=datetime.now()
        ),
        Finding(
            id="f2",
            content="See also machine learning applications",
            source="test",
            timestamp=datetime.now()
        )
    ]
    
    # Test trail discovery
    trails = discovery.discover_trails(
        query="quantum computing",
        findings=findings,
        max_trails=2
    )
    
    # Should find some trails based on keywords
    assert isinstance(trails, list)
    
    # Test relevance scoring
    score = discovery.score_trail_relevance(
        "quantum AI",
        "quantum computing",
        findings
    )
    assert 0.0 <= score <= 1.0
    
    # Test novelty detection
    novelty = discovery.detect_novelty("new topic", findings)
    assert 0.0 <= novelty <= 1.0
    
    print("✓ Trail discovery test passed")


async def test_clarification_engine():
    """Test clarification engine."""
    print("Testing clarification engine...")
    
    engine = ClarificationEngine(max_questions=5)
    
    # Test ambiguity detection
    ambiguous_query = "tell me about stuff"
    clear_query = "What are the specific applications of quantum computing in cryptography?"
    
    assert engine.needs_clarification(ambiguous_query)
    assert not engine.needs_clarification(clear_query)
    
    # Test question generation
    ambiguity_score, questions = await engine.analyze_query(ambiguous_query)
    assert ambiguity_score > 0.3
    assert isinstance(questions, list)
    
    # Test clarification processing
    clarifications = {
        "What aspects?": "Technical details",
        "What depth?": "High-level overview"
    }
    enhanced = engine.process_clarifications(ambiguous_query, clarifications)
    assert "Technical details" in enhanced
    
    print("✓ Clarification engine test passed")


def test_config():
    """Test configuration system."""
    print("Testing configuration...")
    
    # Test default config
    config = ResearchConfig.create_default()
    assert config.budget.max_tokens == 50000
    
    # Test development config
    dev_config = ResearchConfig.create_development()
    assert dev_config.development_mode
    assert dev_config.budget.max_tokens == 10000
    
    # Test production config
    prod_config = ResearchConfig.create_production()
    assert not prod_config.development_mode
    assert prod_config.budget.max_tokens == 200000
    
    print("✓ Configuration test passed")


def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("Running Integration Tests")
    print("=" * 60)
    print()
    
    try:
        # Synchronous tests
        test_models()
        test_budget()
        test_state_machine()
        test_agent_registry()
        test_trail_manager()
        test_trail_discovery()
        test_config()
        
        # Async tests
        asyncio.run(test_clarification_engine())
        
        print()
        print("=" * 60)
        print("✅ All Integration Tests Passed!")
        print("=" * 60)
        print()
        print("Infrastructure is working correctly.")
        print("Ready for LLM agent testing.")
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Test Failed: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
