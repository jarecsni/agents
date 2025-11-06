"""
Progress monitoring and visualization for research workflows.
"""
from typing import Dict, Any, List
from datetime import datetime
try:
    from .models import ResearchContext, ResearchState
except ImportError:
    from models import ResearchContext, ResearchState
try:
    from .budget import ResearchBudget
except ImportError:
    from budget import ResearchBudget
try:
    from .trail_manager import TrailManager
except ImportError:
    from trail_manager import TrailManager
import logging

logger = logging.getLogger(__name__)


class ProgressMonitor:
    """
    Monitors and reports research progress in real-time.
    """
    
    def __init__(self):
        self._status_updates: List[Dict[str, Any]] = []
        self._start_time: datetime = datetime.now()
    
    def log_status(
        self,
        message: str,
        context: ResearchContext,
        budget: ResearchBudget,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Log a status update."""
        update = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'state': context.state.value,
            'budget_utilization': budget.utilization_percent(),
            'findings_count': len(context.findings),
            'trails_count': len(context.research_trails),
            'metadata': metadata or {}
        }
        
        self._status_updates.append(update)
        logger.info(f"[{context.state.value}] {message}")
    
    def get_current_status(
        self,
        context: ResearchContext,
        budget: ResearchBudget,
        trail_manager: TrailManager = None
    ) -> Dict[str, Any]:
        """Get current research status."""
        elapsed_time = (datetime.now() - self._start_time).total_seconds()
        
        status = {
            'state': context.state.value,
            'state_description': self._get_state_description(context.state),
            'elapsed_time_seconds': elapsed_time,
            'findings_count': len(context.findings),
            'quality_scores': [q.to_dict() for q in context.quality_scores],
            'budget': {
                'utilization': budget.utilization_percent(),
                'remaining': budget.remaining().to_dict(),
                'is_near_limit': budget.is_near_limit()
            },
            'handoffs': len(context.handoff_history),
            'clarifications': len(context.clarifications)
        }
        
        # Add trail information if available
        if trail_manager:
            trail_stats = trail_manager.get_statistics()
            status['trails'] = trail_stats
        
        return status
    
    def get_progress_percentage(
        self,
        context: ResearchContext
    ) -> float:
        """
        Calculate overall progress percentage.
        Returns value from 0.0 to 100.0.
        """
        state_progress = {
            ResearchState.INITIALIZING: 5,
            ResearchState.CLARIFYING: 15,
            ResearchState.PLANNING: 25,
            ResearchState.SEARCHING: 50,
            ResearchState.EVALUATING: 65,
            ResearchState.TRAIL_FOLLOWING: 75,
            ResearchState.SYNTHESIZING: 90,
            ResearchState.COMPLETED: 100,
            ResearchState.FAILED: 0
        }
        
        return state_progress.get(context.state, 0)
    
    def format_status_message(
        self,
        context: ResearchContext,
        budget: ResearchBudget
    ) -> str:
        """Format a human-readable status message."""
        progress = self.get_progress_percentage(context)
        state_desc = self._get_state_description(context.state)
        
        budget_util = budget.utilization_percent()
        budget_str = f"Budget: {budget_util['tokens']:.0f}% tokens, {budget_util['api_calls']:.0f}% calls"
        
        return (
            f"Progress: {progress:.0f}% | {state_desc} | "
            f"Findings: {len(context.findings)} | {budget_str}"
        )
    
    def get_activity_timeline(self) -> List[Dict[str, Any]]:
        """Get timeline of all status updates."""
        return self._status_updates.copy()
    
    def get_agent_activity(
        self,
        context: ResearchContext
    ) -> List[Dict[str, str]]:
        """Get agent activity from handoff history."""
        return [
            {
                'timestamp': h.timestamp.isoformat(),
                'from_agent': h.from_agent,
                'to_agent': h.to_agent,
                'reason': h.reason
            }
            for h in context.handoff_history
        ]
    
    def get_trail_progress(
        self,
        trail_manager: TrailManager
    ) -> Dict[str, Any]:
        """Get progress of research trails."""
        active_trails = trail_manager.get_active_trails()
        completed_trails = trail_manager.get_completed_trails()
        
        return {
            'active': [
                {
                    'id': t.id[:8],
                    'query': t.trail_query,
                    'relevance': t.relevance_score,
                    'findings': len(t.findings)
                }
                for t in active_trails
            ],
            'completed': [
                {
                    'id': t.id[:8],
                    'query': t.trail_query,
                    'status': t.status.value,
                    'findings': len(t.findings)
                }
                for t in completed_trails
            ]
        }
    
    def _get_state_description(self, state: ResearchState) -> str:
        """Get human-readable state description."""
        descriptions = {
            ResearchState.INITIALIZING: "Initializing research...",
            ResearchState.CLARIFYING: "Asking clarifying questions...",
            ResearchState.PLANNING: "Planning research strategy...",
            ResearchState.SEARCHING: "Searching for information...",
            ResearchState.EVALUATING: "Evaluating research quality...",
            ResearchState.TRAIL_FOLLOWING: "Exploring research trails...",
            ResearchState.SYNTHESIZING: "Synthesizing findings...",
            ResearchState.COMPLETED: "Research completed!",
            ResearchState.FAILED: "Research failed"
        }
        return descriptions.get(state, "Unknown state")
    
    def reset(self) -> None:
        """Reset progress monitor."""
        self._status_updates.clear()
        self._start_time = datetime.now()


class StatusFormatter:
    """Formats status updates for display."""
    
    @staticmethod
    def format_for_gradio(status: Dict[str, Any]) -> str:
        """Format status for Gradio markdown display."""
        lines = [
            f"## Research Status",
            f"",
            f"**State:** {status['state_description']}",
            f"**Progress:** {status.get('progress', 0):.0f}%",
            f"**Elapsed Time:** {status['elapsed_time_seconds']:.1f}s",
            f"",
            f"### Findings",
            f"- Total findings: {status['findings_count']}",
            f"- Handoffs: {status['handoffs']}",
            f"- Clarifications: {status['clarifications']}",
            f"",
            f"### Budget Utilization",
        ]
        
        budget_util = status['budget']['utilization']
        lines.extend([
            f"- Tokens: {budget_util['tokens']:.1f}%",
            f"- API Calls: {budget_util['api_calls']:.1f}%",
            f"- Time: {budget_util['time']:.1f}%",
        ])
        
        if 'trails' in status:
            trails = status['trails']
            lines.extend([
                f"",
                f"### Research Trails",
                f"- Active: {trails['active_trails']}",
                f"- Completed: {trails['completed_trails']}",
                f"- Total findings from trails: {trails['total_findings']}"
            ])
        
        return "\n".join(lines)
    
    @staticmethod
    def format_quality_scores(quality_scores: List[Dict[str, Any]]) -> str:
        """Format quality scores for display."""
        if not quality_scores:
            return "No quality assessments yet"
        
        latest = quality_scores[-1]
        lines = [
            "### Quality Metrics",
            f"- Completeness: {latest['completeness']:.2f}",
            f"- Credibility: {latest['credibility']:.2f}",
            f"- Relevance: {latest['relevance']:.2f}",
            f"- Confidence: {latest['confidence']:.2f}",
            f"- **Overall: {latest['overall']:.2f}**"
        ]
        
        if latest.get('gaps_identified'):
            lines.append(f"\n**Gaps identified:** {len(latest['gaps_identified'])}")
        
        return "\n".join(lines)
