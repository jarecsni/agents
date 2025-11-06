"""
Main Research Coordinator orchestrating the autonomous research workflow.
"""
from typing import Optional, AsyncGenerator
from datetime import datetime
import uuid
from agents import Runner

try:
    from .models import (
        ResearchContext, ResearchState, Finding, Capability
    )
    from .budget import ResearchBudget, Operation
    from .config import ResearchConfig
    from .state_machine import ResearchStateMachine
    from .agent_registry import AgentRegistry
    from .handoff_controller import HandoffController, HandoffContext
    from .trail_manager import TrailManager
    from .trail_discovery import TrailDiscovery
    from .trail_execution import TrailExecutionEngine
    from .evaluation_engine import EvaluationEngine
    from .clarification_engine import ClarificationEngine
    from .progress_monitor import ProgressMonitor, StatusFormatter
    from .planner_agent import planner_agent, dynamic_planner_agent
    from .search_agent import search_agent, enhanced_search_agent
    from .writer_agent import writer_agent, enhanced_writer_agent
    from .email_agent import email_agent
except ImportError:
    from models import (
        ResearchContext, ResearchState, Finding, Capability
    )
    from budget import ResearchBudget, Operation
    from config import ResearchConfig
    from state_machine import ResearchStateMachine
    from agent_registry import AgentRegistry
    from handoff_controller import HandoffController, HandoffContext
    from trail_manager import TrailManager
    from trail_discovery import TrailDiscovery
    from trail_execution import TrailExecutionEngine
    from evaluation_engine import EvaluationEngine
    from clarification_engine import ClarificationEngine
    from progress_monitor import ProgressMonitor, StatusFormatter
    from planner_agent import planner_agent, dynamic_planner_agent
    from search_agent import search_agent, enhanced_search_agent
    from writer_agent import writer_agent, enhanced_writer_agent
    from email_agent import email_agent

import logging

logger = logging.getLogger(__name__)


class ResearchCoordinator:
    """
    Main coordinator for autonomous deep research.
    Orchestrates all components and manages research workflow.
    """
    
    def __init__(self, config: Optional[ResearchConfig] = None):
        self.config = config or ResearchConfig.create_default()
        
        # Initialize core components
        self.agent_registry = AgentRegistry()
        self.handoff_controller = HandoffController(self.agent_registry)
        self.trail_manager = TrailManager(
            max_concurrent_trails=self.config.trail.max_concurrent_trails
        )
        self.trail_discovery = TrailDiscovery(
            min_relevance=self.config.trail.min_relevance_score
        )
        self.trail_execution = TrailExecutionEngine(
            self.trail_manager,
            self.agent_registry
        )
        self.evaluation_engine = EvaluationEngine()
        self.clarification_engine = ClarificationEngine(
            max_questions=self.config.clarification.max_questions,
            ambiguity_threshold=self.config.clarification.ambiguity_threshold,
            enable_followup=self.config.clarification.enable_follow_up_questions
        )
        self.progress_monitor = ProgressMonitor()
        
        # Register agents
        self._register_agents()
    
    def _register_agents(self) -> None:
        """Register all available agents."""
        self.agent_registry.register_agent(
            "planner",
            planner_agent,
            [Capability.PLANNING],
            "Plans research searches"
        )
        
        self.agent_registry.register_agent(
            "dynamic_planner",
            dynamic_planner_agent,
            [Capability.PLANNING],
            "Dynamic adaptive research planner"
        )
        
        self.agent_registry.register_agent(
            "search",
            search_agent,
            [Capability.SEARCHING],
            "Searches web and summarizes results"
        )
        
        self.agent_registry.register_agent(
            "enhanced_search",
            enhanced_search_agent,
            [Capability.SEARCHING],
            "Enhanced search with quality metrics"
        )
        
        self.agent_registry.register_agent(
            "writer",
            writer_agent,
            [Capability.WRITING],
            "Writes research reports"
        )
        
        self.agent_registry.register_agent(
            "enhanced_writer",
            enhanced_writer_agent,
            [Capability.WRITING],
            "Enhanced writer with multi-stream synthesis"
        )
        
        self.agent_registry.register_agent(
            "email",
            email_agent,
            [Capability.EMAIL],
            "Sends email reports"
        )
        
        logger.info(f"Registered {len(self.agent_registry)} agents")
    
    async def conduct_research(
        self,
        query: str,
        budget: Optional[ResearchBudget] = None
    ) -> AsyncGenerator[str, None]:
        """
        Conduct autonomous research for a query.
        Yields status updates throughout the process.
        """
        # Initialize
        if budget is None:
            if self.config.development_mode:
                budget = ResearchBudget.create_development()
            else:
                budget = ResearchBudget.create_default()
        
        context = ResearchContext(query=query)
        state_machine = ResearchStateMachine(context)
        
        self.progress_monitor.log_status("Starting research", context, budget)
        yield self.progress_monitor.format_status_message(context, budget)
        
        try:
            # Phase 1: Clarification (if needed)
            if self.clarification_engine.needs_clarification(query):
                state_machine.transition(ResearchState.CLARIFYING)
                yield "Analyzing query for clarifications..."
                # In production, would interact with user here
                # For now, skip clarification
            
            # Phase 2: Planning
            state_machine.transition(ResearchState.PLANNING)
            self.progress_monitor.log_status("Planning research", context, budget)
            yield self.progress_monitor.format_status_message(context, budget)
            
            search_plan = await self._plan_research(context, budget)
            
            # Phase 3: Searching
            state_machine.transition(ResearchState.SEARCHING)
            self.progress_monitor.log_status("Executing searches", context, budget)
            yield self.progress_monitor.format_status_message(context, budget)
            
            await self._execute_searches(context, search_plan, budget)
            
            # Phase 4: Evaluation
            state_machine.transition(ResearchState.EVALUATING)
            self.progress_monitor.log_status("Evaluating quality", context, budget)
            yield self.progress_monitor.format_status_message(context, budget)
            
            quality_score = await self.evaluation_engine.evaluate(
                context.query,
                context.findings
            )
            context.quality_scores.append(quality_score)
            
            # Phase 5: Trail Following (if enabled and budget allows)
            if (self.config.trail.enable_autonomous_trails and 
                budget.can_afford_trail() and
                quality_score.gaps_identified):
                
                state_machine.transition(ResearchState.TRAIL_FOLLOWING)
                self.progress_monitor.log_status("Following research trails", context, budget)
                yield self.progress_monitor.format_status_message(context, budget)
                
                await self._follow_trails(context, budget)
            
            # Phase 6: Synthesizing
            state_machine.transition(ResearchState.SYNTHESIZING)
            self.progress_monitor.log_status("Synthesizing report", context, budget)
            yield self.progress_monitor.format_status_message(context, budget)
            
            report = await self._synthesize_report(context, budget)
            
            # Phase 7: Complete
            state_machine.transition(ResearchState.COMPLETED)
            self.progress_monitor.log_status("Research completed", context, budget)
            
            final_status = self.progress_monitor.get_current_status(
                context, budget, self.trail_manager
            )
            yield StatusFormatter.format_for_gradio(final_status)
            yield report
            
        except Exception as e:
            logger.error(f"Research failed: {e}")
            state_machine.force_fail(str(e))
            yield f"Research failed: {e}"
    
    async def _plan_research(
        self,
        context: ResearchContext,
        budget: ResearchBudget
    ):
        """Plan research searches."""
        result = await Runner.run(dynamic_planner_agent, f"Query: {context.query}")
        
        # Consume budget
        budget.consume(Operation("planning", estimated_tokens=500))
        
        return result.final_output
    
    async def _execute_searches(
        self,
        context: ResearchContext,
        search_plan,
        budget: ResearchBudget
    ) -> None:
        """Execute planned searches."""
        import asyncio
        
        searches = search_plan.searches[:5]  # Limit searches
        
        for search_item in searches:
            if not budget.can_afford(Operation("search", estimated_tokens=2000)):
                logger.warning("Budget exhausted, stopping searches")
                break
            
            try:
                result = await Runner.run(
                    enhanced_search_agent,
                    f"Search term: {search_item.query}\nReason: {search_item.reason}"
                )
                
                # Create finding
                finding = Finding(
                    id=str(uuid.uuid4()),
                    content=str(result.final_output),
                    source=f"search:{search_item.query}",
                    timestamp=datetime.now(),
                    confidence=0.8
                )
                
                context.add_finding(finding)
                budget.consume(Operation("search", estimated_tokens=2000))
                
            except Exception as e:
                logger.error(f"Search failed: {e}")
    
    async def _follow_trails(
        self,
        context: ResearchContext,
        budget: ResearchBudget
    ) -> None:
        """Follow autonomous research trails."""
        # Discover trails
        trail_suggestions = self.trail_discovery.discover_trails(
            context.query,
            context.findings,
            max_trails=2  # Limit for development
        )
        
        # Create and execute trails
        for suggestion in trail_suggestions:
            if not budget.can_afford_trail():
                break
            
            trail_budget = budget.allocate_for_trail(percentage=0.15)
            budget.increment_trail_depth()
            
            trail = self.trail_manager.create_trail(
                trail_query=suggestion.trail_query,
                relevance_score=suggestion.relevance_score,
                budget=trail_budget
            )
            
            if trail:
                context.add_trail(trail)
                await self.trail_execution.execute_trail(trail)
                
                # Add trail findings to context
                for finding in trail.findings:
                    context.add_finding(finding)
            
            budget.decrement_trail_depth()
    
    async def _synthesize_report(
        self,
        context: ResearchContext,
        budget: ResearchBudget
    ) -> str:
        """Synthesize final report."""
        findings_summary = "\n\n".join([
            f"Finding {i+1}: {f.content[:200]}..."
            for i, f in enumerate(context.findings[:10])
        ])
        
        input_text = f"Original query: {context.query}\n\nFindings:\n{findings_summary}"
        
        result = await Runner.run(enhanced_writer_agent, input_text)
        
        budget.consume(Operation("synthesis", estimated_tokens=3000))
        
        return result.final_output.markdown_report
