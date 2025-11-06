"""
Agent Registry system for managing agent capabilities and tool wrapping.
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from agents import Agent
try:
    from .models import Capability
except ImportError:
    from models import Capability
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentInfo:
    """Information about a registered agent."""
    agent_id: str
    agent: Agent
    capabilities: List[Capability]
    description: str
    is_available: bool = True
    call_count: int = 0
    failure_count: int = 0
    
    def record_call(self) -> None:
        """Record a successful call."""
        self.call_count += 1
    
    def record_failure(self) -> None:
        """Record a failed call."""
        self.failure_count += 1
    
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.call_count + self.failure_count
        if total == 0:
            return 1.0
        return self.call_count / total


class AgentRegistry:
    """
    Central registry for managing agents and their capabilities.
    Provides agent discovery, tool wrapping, and health monitoring.
    """
    
    def __init__(self):
        self._agents: Dict[str, AgentInfo] = {}
        self._capability_map: Dict[Capability, List[str]] = {cap: [] for cap in Capability}
    
    def register_agent(
        self,
        agent_id: str,
        agent: Agent,
        capabilities: List[Capability],
        description: str = ""
    ) -> None:
        """Register an agent with its capabilities."""
        if agent_id in self._agents:
            logger.warning(f"Agent {agent_id} already registered, updating...")
        
        agent_info = AgentInfo(
            agent_id=agent_id,
            agent=agent,
            capabilities=capabilities,
            description=description
        )
        
        self._agents[agent_id] = agent_info
        
        # Update capability map
        for capability in capabilities:
            if agent_id not in self._capability_map[capability]:
                self._capability_map[capability].append(agent_id)
        
        logger.info(f"Registered agent {agent_id} with capabilities: {[c.value for c in capabilities]}")
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent."""
        if agent_id not in self._agents:
            logger.warning(f"Agent {agent_id} not found in registry")
            return
        
        agent_info = self._agents[agent_id]
        
        # Remove from capability map
        for capability in agent_info.capabilities:
            if agent_id in self._capability_map[capability]:
                self._capability_map[capability].remove(agent_id)
        
        del self._agents[agent_id]
        logger.info(f"Unregistered agent {agent_id}")
    
    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent info by ID."""
        return self._agents.get(agent_id)
    
    def get_agent_for_capability(self, capability: Capability) -> Optional[AgentInfo]:
        """
        Get the best available agent for a capability.
        Prioritizes agents with higher success rates.
        """
        agent_ids = self._capability_map.get(capability, [])
        
        if not agent_ids:
            logger.warning(f"No agents found for capability: {capability.value}")
            return None
        
        # Filter available agents and sort by success rate
        available_agents = [
            self._agents[aid] for aid in agent_ids
            if self._agents[aid].is_available
        ]
        
        if not available_agents:
            logger.warning(f"No available agents for capability: {capability.value}")
            return None
        
        # Sort by success rate (descending)
        available_agents.sort(key=lambda a: a.success_rate(), reverse=True)
        
        return available_agents[0]
    
    def get_all_agents_for_capability(self, capability: Capability) -> List[AgentInfo]:
        """Get all available agents for a capability."""
        agent_ids = self._capability_map.get(capability, [])
        return [
            self._agents[aid] for aid in agent_ids
            if self._agents[aid].is_available
        ]
    
    def get_available_agents(self) -> List[AgentInfo]:
        """Get all available agents."""
        return [info for info in self._agents.values() if info.is_available]
    
    def set_agent_availability(self, agent_id: str, is_available: bool) -> None:
        """Set agent availability status."""
        if agent_id in self._agents:
            self._agents[agent_id].is_available = is_available
            logger.info(f"Agent {agent_id} availability set to {is_available}")
    
    def wrap_agent_as_tool(self, agent_id: str) -> Optional[Callable]:
        """
        Wrap an agent as a callable tool function.
        Returns a function that can be used by other agents.
        """
        agent_info = self.get_agent(agent_id)
        if not agent_info:
            logger.error(f"Cannot wrap agent {agent_id}: not found")
            return None
        
        async def agent_tool(input_text: str) -> str:
            """Wrapped agent tool function."""
            try:
                from agents import Runner
                result = await Runner.run(agent_info.agent, input_text)
                agent_info.record_call()
                return str(result.final_output)
            except Exception as e:
                agent_info.record_failure()
                logger.error(f"Agent tool {agent_id} failed: {e}")
                raise
        
        # Set function metadata
        agent_tool.__name__ = f"{agent_id}_tool"
        agent_tool.__doc__ = f"Tool wrapper for {agent_id}: {agent_info.description}"
        
        return agent_tool
    
    async def invoke_agent_tool(
        self,
        agent_id: str,
        input_data: Any,
        timeout: Optional[float] = None
    ) -> Any:
        """
        Invoke an agent as a tool with timeout and error handling.
        """
        agent_info = self.get_agent(agent_id)
        if not agent_info:
            raise ValueError(f"Agent {agent_id} not found in registry")
        
        if not agent_info.is_available:
            raise RuntimeError(f"Agent {agent_id} is not available")
        
        try:
            from agents import Runner
            
            if timeout:
                result = await asyncio.wait_for(
                    Runner.run(agent_info.agent, str(input_data)),
                    timeout=timeout
                )
            else:
                result = await Runner.run(agent_info.agent, str(input_data))
            
            agent_info.record_call()
            return result.final_output
        
        except asyncio.TimeoutError:
            agent_info.record_failure()
            logger.error(f"Agent {agent_id} timed out after {timeout}s")
            raise
        
        except Exception as e:
            agent_info.record_failure()
            logger.error(f"Agent {agent_id} failed: {e}")
            raise
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all agents."""
        return {
            agent_id: {
                'available': info.is_available,
                'call_count': info.call_count,
                'failure_count': info.failure_count,
                'success_rate': info.success_rate(),
                'capabilities': [c.value for c in info.capabilities]
            }
            for agent_id, info in self._agents.items()
        }
    
    def get_capability_coverage(self) -> Dict[str, int]:
        """Get count of agents per capability."""
        return {
            cap.value: len([aid for aid in agent_ids if self._agents[aid].is_available])
            for cap, agent_ids in self._capability_map.items()
        }
    
    def __len__(self) -> int:
        """Return number of registered agents."""
        return len(self._agents)
    
    def __contains__(self, agent_id: str) -> bool:
        """Check if agent is registered."""
        return agent_id in self._agents
