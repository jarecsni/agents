"""
Trail management system for autonomous research exploration.
"""
from typing import List, Set, Optional
try:
    from .models import ResearchTrail, TrailStatus, Finding
except ImportError:
    from models import ResearchTrail, TrailStatus, Finding
try:
    from .budget import ResearchBudget
except ImportError:
    from budget import ResearchBudget
import uuid
import logging

logger = logging.getLogger(__name__)


class TrailManager:
    """
    Manages autonomous research trails with breadcrumb tracking
    to prevent infinite loops and prioritize exploration.
    """
    
    def __init__(self, max_concurrent_trails: int = 3):
        self.max_concurrent_trails = max_concurrent_trails
        self._active_trails: List[ResearchTrail] = []
        self._completed_trails: List[ResearchTrail] = []
        self._visited_queries: Set[str] = set()
        self._breadcrumbs: Set[str] = set()
    
    def create_trail(
        self,
        trail_query: str,
        relevance_score: float,
        budget: ResearchBudget,
        origin_finding_id: Optional[str] = None
    ) -> Optional[ResearchTrail]:
        """
        Create a new research trail if it's not redundant.
        Returns None if trail would create a loop or is redundant.
        """
        # Check for loops
        if self._would_create_loop(trail_query):
            logger.info(f"Skipping trail '{trail_query}' - would create loop")
            return None
        
        # Check if we've already explored this
        if trail_query.lower() in self._visited_queries:
            logger.info(f"Skipping trail '{trail_query}' - already explored")
            return None
        
        # Check concurrent trail limit
        if len(self._active_trails) >= self.max_concurrent_trails:
            logger.warning(
                f"Cannot create trail - at max concurrent limit "
                f"({self.max_concurrent_trails})"
            )
            return None
        
        trail = ResearchTrail(
            id=str(uuid.uuid4()),
            origin_finding_id=origin_finding_id,
            trail_query=trail_query,
            relevance_score=relevance_score,
            budget_allocated=budget,
            status=TrailStatus.PENDING
        )
        
        self._active_trails.append(trail)
        self._visited_queries.add(trail_query.lower())
        
        logger.info(
            f"Created trail '{trail_query}' (relevance: {relevance_score:.2f}, "
            f"id: {trail.id[:8]}...)"
        )
        
        return trail
    
    def start_trail(self, trail_id: str) -> bool:
        """Mark a trail as active."""
        trail = self._find_trail(trail_id)
        if not trail:
            return False
        
        if trail.status != TrailStatus.PENDING:
            logger.warning(f"Trail {trail_id[:8]}... is not pending")
            return False
        
        trail.status = TrailStatus.ACTIVE
        self._add_breadcrumb(trail.trail_query)
        logger.info(f"Started trail {trail_id[:8]}...")
        return True
    
    def complete_trail(self, trail_id: str) -> bool:
        """Mark a trail as completed."""
        trail = self._find_trail(trail_id)
        if not trail:
            return False
        
        trail.status = TrailStatus.COMPLETED
        self._remove_breadcrumb(trail.trail_query)
        
        # Move to completed list
        self._active_trails = [t for t in self._active_trails if t.id != trail_id]
        self._completed_trails.append(trail)
        
        logger.info(
            f"Completed trail {trail_id[:8]}... with {len(trail.findings)} findings"
        )
        return True
    
    def abandon_trail(self, trail_id: str, reason: str = "") -> bool:
        """Abandon a trail."""
        trail = self._find_trail(trail_id)
        if not trail:
            return False
        
        trail.status = TrailStatus.ABANDONED
        self._remove_breadcrumb(trail.trail_query)
        
        # Move to completed list (even though abandoned)
        self._active_trails = [t for t in self._active_trails if t.id != trail_id]
        self._completed_trails.append(trail)
        
        logger.info(
            f"Abandoned trail {trail_id[:8]}..."
            + (f" (reason: {reason})" if reason else "")
        )
        return True
    
    def add_finding_to_trail(self, trail_id: str, finding: Finding) -> bool:
        """Add a finding to a trail."""
        trail = self._find_trail(trail_id)
        if not trail:
            return False
        
        trail.findings.append(finding)
        logger.debug(f"Added finding to trail {trail_id[:8]}...")
        return True
    
    def get_active_trails(self) -> List[ResearchTrail]:
        """Get all active trails."""
        return [t for t in self._active_trails if t.status == TrailStatus.ACTIVE]
    
    def get_pending_trails(self) -> List[ResearchTrail]:
        """Get all pending trails."""
        return [t for t in self._active_trails if t.status == TrailStatus.PENDING]
    
    def get_completed_trails(self) -> List[ResearchTrail]:
        """Get all completed trails."""
        return self._completed_trails.copy()
    
    def get_all_trails(self) -> List[ResearchTrail]:
        """Get all trails (active and completed)."""
        return self._active_trails + self._completed_trails
    
    def prioritize_trails(self) -> List[ResearchTrail]:
        """
        Get pending trails sorted by priority (relevance score).
        Returns trails in order they should be executed.
        """
        pending = self.get_pending_trails()
        return sorted(pending, key=lambda t: t.relevance_score, reverse=True)
    
    def _find_trail(self, trail_id: str) -> Optional[ResearchTrail]:
        """Find a trail by ID."""
        for trail in self._active_trails:
            if trail.id == trail_id:
                return trail
        for trail in self._completed_trails:
            if trail.id == trail_id:
                return trail
        return None
    
    def _would_create_loop(self, query: str) -> bool:
        """Check if query would create a loop."""
        return query.lower() in self._breadcrumbs
    
    def _add_breadcrumb(self, query: str) -> None:
        """Add a breadcrumb for loop detection."""
        self._breadcrumbs.add(query.lower())
    
    def _remove_breadcrumb(self, query: str) -> None:
        """Remove a breadcrumb."""
        self._breadcrumbs.discard(query.lower())
    
    def get_statistics(self) -> dict:
        """Get trail statistics."""
        all_trails = self.get_all_trails()
        
        return {
            'total_trails': len(all_trails),
            'active_trails': len(self.get_active_trails()),
            'pending_trails': len(self.get_pending_trails()),
            'completed_trails': len(self._completed_trails),
            'total_findings': sum(len(t.findings) for t in all_trails),
            'visited_queries': len(self._visited_queries),
            'active_breadcrumbs': len(self._breadcrumbs)
        }
    
    def can_create_more_trails(self) -> bool:
        """Check if more trails can be created."""
        return len(self._active_trails) < self.max_concurrent_trails
    
    def __len__(self) -> int:
        """Return total number of trails."""
        return len(self._active_trails) + len(self._completed_trails)
