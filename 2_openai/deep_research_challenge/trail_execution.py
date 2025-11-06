"""
Trail execution engine for running autonomous research trails.
"""
from typing import Optional
from datetime import datetime
try:
    from .models import ResearchTrail, TrailStatus, Finding
except ImportError:
    from models import ResearchTrail, TrailStatus, Finding
try:
    from .budget import ResearchBudget, Operation
except ImportError:
    from budget import ResearchBudget, Operation
try:
    from .trail_manager import TrailManager
except ImportError:
    from trail_manager import TrailManager
try:
    from .agent_registry import AgentRegistry
except ImportError:
    from agent_registry import AgentRegistry
try:
    from .models import Capability
except ImportError:
    from models import Capability
import uuid
import logging

logger = logging.getLogger(__name__)


class TrailExecutionEngine:
    """
    Executes research trails with budget awareness and loop prevention.
    """
    
    def __init__(
        self,
        trail_manager: TrailManager,
        agent_registry: AgentRegistry
    ):
        self.trail_manager = trail_manager
        self.agent_registry = agent_registry
    
    async def execute_trail(
        self,
        trail: ResearchTrail
    ) -> ResearchTrail:
        """
        Execute a research trail within its allocated budget.
        Returns updated trail with findings.
        """
        logger.info(
            f"Executing trail: {trail.trail_query} "
            f"(budget: {trail.budget_allocated.max_tokens} tokens)"
        )
        
        # Start the trail
        if not self.trail_manager.start_trail(trail.id):
            logger.error(f"Failed to start trail {trail.id}")
            return trail
        
        try:
            # Check budget before proceeding
            search_op = Operation(
                name="trail_search",
                estimated_tokens=2000,
                estimated_api_calls=1
            )
            
            if not trail.budget_allocated.can_afford(search_op):
                logger.warning(f"Trail {trail.id[:8]}... out of budget")
                self.trail_manager.abandon_trail(trail.id, "budget exhausted")
                return trail
            
            # Execute search for trail
            finding = await self._execute_trail_search(trail)
            
            if finding:
                trail.findings.append(finding)
                self.trail_manager.add_finding_to_trail(trail.id, finding)
                trail.budget_allocated.consume(search_op)
            
            # Complete the trail
            self.trail_manager.complete_trail(trail.id)
            
            logger.info(
                f"Trail completed: {trail.id[:8]}... "
                f"with {len(trail.findings)} findings"
            )
            
        except Exception as e:
            logger.error(f"Trail execution failed: {e}")
            self.trail_manager.abandon_trail(trail.id, str(e))
        
        return trail
    
    async def _execute_trail_search(
        self,
        trail: ResearchTrail
    ) -> Optional[Finding]:
        """Execute a search for the trail."""
        try:
            # Get search agent
            search_agent_info = self.agent_registry.get_agent_for_capability(
                Capability.SEARCHING
            )
            
            if not search_agent_info:
                logger.error("No search agent available")
                return None
            
            # Execute search
            search_input = f"Search term: {trail.trail_query}\nReason: Exploring research trail"
            result = await self.agent_registry.invoke_agent_tool(
                search_agent_info.agent_id,
                search_input
            )
            
            # Create finding
            finding = Finding(
                id=str(uuid.uuid4()),
                content=str(result),
                source=f"trail_search:{trail.trail_query}",
                timestamp=datetime.now(),
                confidence=0.7,
                metadata={
                    'trail_id': trail.id,
                    'trail_query': trail.trail_query
                }
            )
            
            return finding
        
        except Exception as e:
            logger.error(f"Trail search failed: {e}")
            return None
    
    async def execute_trails_parallel(
        self,
        trails: list[ResearchTrail],
        max_concurrent: int = 3
    ) -> list[ResearchTrail]:
        """
        Execute multiple trails in parallel with concurrency limit.
        """
        import asyncio
        
        logger.info(f"Executing {len(trails)} trails (max concurrent: {max_concurrent})")
        
        # Limit concurrent execution
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(trail):
            async with semaphore:
                return await self.execute_trail(trail)
        
        # Execute all trails
        tasks = [execute_with_semaphore(trail) for trail in trails]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        completed_trails = [
            r for r in results
            if isinstance(r, ResearchTrail)
        ]
        
        logger.info(f"Completed {len(completed_trails)} trails")
        return completed_trails
    
    def should_terminate_trail(
        self,
        trail: ResearchTrail,
        min_findings: int = 1
    ) -> tuple[bool, str]:
        """
        Determine if a trail should be terminated.
        Returns (should_terminate, reason).
        """
        # Check budget
        if trail.budget_allocated.is_exhausted():
            return True, "budget exhausted"
        
        # Check if we have minimum findings
        if len(trail.findings) >= min_findings:
            return True, "minimum findings reached"
        
        # Check if trail is taking too long
        if trail.budget_allocated.current_usage.time_seconds > trail.budget_allocated.max_time_seconds * 0.9:
            return True, "time limit approaching"
        
        return False, ""
    
    def get_trail_statistics(self, trail: ResearchTrail) -> dict:
        """Get statistics for a trail."""
        return {
            'trail_id': trail.id,
            'query': trail.trail_query,
            'status': trail.status.value,
            'findings_count': len(trail.findings),
            'budget_used': trail.budget_allocated.current_usage.to_dict(),
            'budget_utilization': trail.budget_allocated.utilization_percent()
        }
