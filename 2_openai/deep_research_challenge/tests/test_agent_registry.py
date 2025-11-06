"""Integration tests for agent registry."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import asyncio
from agents import Agent
from agent_registry import AgentRegistry, AgentInfo
from models import Capability


class TestAgentRegistry:
    """Test AgentRegistry functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = AgentRegistry()
        self.test_agent = Agent(
            name="TestAgent",
            instructions="Test instructions",
            model="gpt-4o-mini"
        )
    
    def test_register_agent(self):
        """Test agent registration."""
        self.registry.register_agent(
            "test_agent",
            self.test_agent,
            [Capability.SEARCHING],
            "Test agent"
        )
        
        assert len(self.registry) == 1
        assert "test_agent" in self.registry
    
    def test_get_agent(self):
        """Test retrieving agent by ID."""
        self.registry.register_agent(
            "test_agent",
            self.test_agent,
            [Capability.SEARCHING],
            "Test agent"
        )
        
        agent_info = self.registry.get_agent("test_agent")
        assert agent_info is not None
        assert agent_info.agent_id == "test_agent"
        assert Capability.SEARCHING in agent_info.capabilities
    
    def test_get_agent_for_capability(self):
        """Test capability-based agent lookup."""
        self.registry.register_agent(
            "search_agent",
            self.test_agent,
            [Capability.SEARCHING],
            "Search agent"
        )
        
        agent_info = self.registry.get_agent_for_capability(Capability.SEARCHING)
        assert agent_info is not None
        assert agent_info.agent_id == "search_agent"
        
        # Non-existent capability
        agent_info = self.registry.get_agent_for_capability(Capability.WRITING)
        assert agent_info is None
    
    def test_get_all_agents_for_capability(self):
        """Test getting all agents with a capability."""
        agent1 = Agent(name="Agent1", instructions="Test", model="gpt-4o-mini")
        agent2 = Agent(name="Agent2", instructions="Test", model="gpt-4o-mini")
        
        self.registry.register_agent("agent1", agent1, [Capability.SEARCHING], "Agent 1")
        self.registry.register_agent("agent2", agent2, [Capability.SEARCHING], "Agent 2")
        
        agents = self.registry.get_all_agents_for_capability(Capability.SEARCHING)
        assert len(agents) == 2
    
    def test_unregister_agent(self):
        """Test agent unregistration."""
        self.registry.register_agent(
            "test_agent",
            self.test_agent,
            [Capability.SEARCHING],
            "Test agent"
        )
        
        assert len(self.registry) == 1
        
        self.registry.unregister_agent("test_agent")
        assert len(self.registry) == 0
        assert "test_agent" not in self.registry
    
    def test_agent_availability(self):
        """Test agent availability management."""
        self.registry.register_agent(
            "test_agent",
            self.test_agent,
            [Capability.SEARCHING],
            "Test agent"
        )
        
        agent_info = self.registry.get_agent("test_agent")
        assert agent_info.is_available is True
        
        self.registry.set_agent_availability("test_agent", False)
        assert agent_info.is_available is False
    
    def test_agent_statistics(self):
        """Test agent call statistics."""
        self.registry.register_agent(
            "test_agent",
            self.test_agent,
            [Capability.SEARCHING],
            "Test agent"
        )
        
        agent_info = self.registry.get_agent("test_agent")
        assert agent_info.call_count == 0
        assert agent_info.failure_count == 0
        
        agent_info.record_call()
        assert agent_info.call_count == 1
        assert agent_info.success_rate() == 1.0
        
        agent_info.record_failure()
        assert agent_info.failure_count == 1
        assert agent_info.success_rate() == 0.5
    
    def test_wrap_agent_as_tool(self):
        """Test wrapping agent as a tool."""
        self.registry.register_agent(
            "test_agent",
            self.test_agent,
            [Capability.SEARCHING],
            "Test agent"
        )
        
        tool = self.registry.wrap_agent_as_tool("test_agent")
        assert tool is not None
        assert callable(tool)
        assert tool.__name__ == "test_agent_tool"
    
    def test_health_status(self):
        """Test health status reporting."""
        self.registry.register_agent(
            "test_agent",
            self.test_agent,
            [Capability.SEARCHING],
            "Test agent"
        )
        
        health = self.registry.get_health_status()
        assert "test_agent" in health
        assert health["test_agent"]["available"] is True
        assert health["test_agent"]["call_count"] == 0
    
    def test_capability_coverage(self):
        """Test capability coverage reporting."""
        self.registry.register_agent(
            "search_agent",
            self.test_agent,
            [Capability.SEARCHING],
            "Search agent"
        )
        
        coverage = self.registry.get_capability_coverage()
        assert coverage["searching"] == 1
        assert coverage["writing"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
