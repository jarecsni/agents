"""
Handoff controller for orchestrating agent-to-agent handoffs.
"""
from typing import Optional, Any
from datetime import datetime
try:
    from .models import HandoffRecord, ResearchContext, Capability
except ImportError:
    from models import HandoffRecord, ResearchContext, Capability
try:
    from .agent_registry import AgentRegistry
except ImportError:
    from agent_registry import AgentRegistry
import logging

logger = logging.getLogger(__name__)


class HandoffContext:
    """Context passed during agent handoffs."""
    
    def __init__(
        self,
        task_description: str,
        input_data: Any,
        research_context: ResearchContext,
        metadata: dict = None
    ):
        self.task_description = task_description
        self.input_data = input_data
        self.research_context = research_context
        self.metadata = metadata or {}
    
    def to_prompt(self) -> str:
        """Convert handoff context to prompt for next agent."""
        prompt_parts = [
            f"Task: {self.task_description}",
            f"\nInput: {self.input_data}",
            f"\nOriginal Query: {self.research_context.query}"
        ]
        
        if self.research_context.clarifications:
            clarifications_str = "\n".join(
                f"- {q}: {a}" for q, a in self.research_context.clarifications.items()
            )
            prompt_parts.append(f"\nClarifications:\n{clarifications_str}")
        
        if self.research_context.findings:
            findings_count = len(self.research_context.findings)
            prompt_parts.append(f"\nPrevious findings: {findings_count} items collected")
        
        if self.metadata:
            metadata_str = "\n".join(f"- {k}: {v}" for k, v in self.metadata.items())
            prompt_parts.append(f"\nAdditional context:\n{metadata_str}")
        
        return "\n".join(prompt_parts)


class HandoffController:
    """
    Orchestrates agent-to-agent handoffs with context preservation.
    Maintains audit trail of all handoffs.
    """
    
    def __init__(self, agent_registry: AgentRegistry):
        self.agent_registry = agent_registry
        self._handoff_count = 0
    
    async def handoff_to_agent(
        self,
        from_agent_id: str,
        to_agent_id: str,
        handoff_context: HandoffContext,
        reason: str
    ) -> Any:
        """
        Hand off task from one agent to another.
        Returns the result from the target agent.
        """
        self._handoff_count += 1
        
        logger.info(
            f"Handoff #{self._handoff_count}: {from_agent_id} -> {to_agent_id} "
            f"(reason: {reason})"
        )
        
        # Record handoff
        handoff_record = HandoffRecord(
            from_agent=from_agent_id,
            to_agent=to_agent_id,
            reason=reason,
            timestamp=datetime.now(),
            context_summary=handoff_context.task_description
        )
        handoff_context.research_context.add_handoff(handoff_record)
        
        # Invoke target agent
        try:
            prompt = handoff_context.to_prompt()
            result = await self.agent_registry.invoke_agent_tool(to_agent_id, prompt)
            
            logger.info(f"Handoff #{self._handoff_count} completed successfully")
            return result
        
        except Exception as e:
            logger.error(f"Handoff #{self._handoff_count} failed: {e}")
            raise
    
    async def handoff_to_capability(
        self,
        from_agent_id: str,
        capability: Capability,
        handoff_context: HandoffContext,
        reason: str
    ) -> Any:
        """
        Hand off task to an agent with specific capability.
        Automatically selects best available agent.
        """
        agent_info = self.agent_registry.get_agent_for_capability(capability)
        
        if not agent_info:
            raise RuntimeError(
                f"No available agent found for capability: {capability.value}"
            )
        
        logger.info(
            f"Selected agent {agent_info.agent_id} for capability {capability.value}"
        )
        
        return await self.handoff_to_agent(
            from_agent_id=from_agent_id,
            to_agent_id=agent_info.agent_id,
            handoff_context=handoff_context,
            reason=reason
        )
    
    async def handoff_with_fallback(
        self,
        from_agent_id: str,
        capability: Capability,
        handoff_context: HandoffContext,
        reason: str,
        max_retries: int = 2
    ) -> Optional[Any]:
        """
        Hand off with automatic fallback to alternative agents on failure.
        """
        agents = self.agent_registry.get_all_agents_for_capability(capability)
        
        if not agents:
            logger.error(f"No agents available for capability: {capability.value}")
            return None
        
        last_error = None
        
        for attempt, agent_info in enumerate(agents[:max_retries + 1], 1):
            try:
                logger.info(
                    f"Handoff attempt {attempt}/{min(len(agents), max_retries + 1)} "
                    f"to {agent_info.agent_id}"
                )
                
                result = await self.handoff_to_agent(
                    from_agent_id=from_agent_id,
                    to_agent_id=agent_info.agent_id,
                    handoff_context=handoff_context,
                    reason=reason
                )
                
                return result
            
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Handoff to {agent_info.agent_id} failed: {e}, "
                    f"trying fallback..."
                )
                continue
        
        logger.error(f"All handoff attempts failed. Last error: {last_error}")
        raise last_error if last_error else RuntimeError("Handoff failed")
    
    def get_handoff_statistics(self, context: ResearchContext) -> dict:
        """Get statistics about handoffs in this research session."""
        if not context.handoff_history:
            return {
                'total_handoffs': 0,
                'unique_agents': set(),
                'handoff_chain': []
            }
        
        unique_agents = set()
        for handoff in context.handoff_history:
            unique_agents.add(handoff.from_agent)
            unique_agents.add(handoff.to_agent)
        
        handoff_chain = [
            f"{h.from_agent} -> {h.to_agent}" 
            for h in context.handoff_history
        ]
        
        return {
            'total_handoffs': len(context.handoff_history),
            'unique_agents': unique_agents,
            'handoff_chain': handoff_chain
        }
    
    def get_handoff_count(self) -> int:
        """Get total number of handoffs performed."""
        return self._handoff_count
