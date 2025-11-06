"""
Trail discovery system for identifying interesting research tangents.
"""
from typing import List, Set
try:
    from .models import Finding
except ImportError:
    from models import Finding
try:
    from .planner_agent import ResearchTrailSuggestion
except ImportError:
    from planner_agent import ResearchTrailSuggestion
import logging

logger = logging.getLogger(__name__)


class TrailDiscovery:
    """
    Discovers interesting research trails from findings.
    Identifies tangents worth exploring autonomously.
    """
    
    def __init__(self, min_relevance: float = 0.6):
        self.min_relevance = min_relevance
        self._discovered_trails: Set[str] = set()
    
    def discover_trails(
        self,
        query: str,
        findings: List[Finding],
        max_trails: int = 3
    ) -> List[ResearchTrailSuggestion]:
        """
        Discover interesting research trails from findings.
        Returns prioritized list of trail suggestions.
        """
        if not findings:
            logger.info("No findings to discover trails from")
            return []
        
        trail_suggestions = []
        
        # Extract potential trails from findings
        for finding in findings:
            trails = self._extract_trails_from_finding(finding, query)
            trail_suggestions.extend(trails)
        
        # Filter out already discovered trails
        trail_suggestions = [
            t for t in trail_suggestions
            if t.trail_query.lower() not in self._discovered_trails
        ]
        
        # Filter by relevance
        trail_suggestions = [
            t for t in trail_suggestions
            if t.relevance_score >= self.min_relevance
        ]
        
        # Sort by relevance and limit
        trail_suggestions.sort(key=lambda t: t.relevance_score, reverse=True)
        trail_suggestions = trail_suggestions[:max_trails]
        
        # Mark as discovered
        for trail in trail_suggestions:
            self._discovered_trails.add(trail.trail_query.lower())
        
        logger.info(f"Discovered {len(trail_suggestions)} research trails")
        return trail_suggestions
    
    def _extract_trails_from_finding(
        self,
        finding: Finding,
        original_query: str
    ) -> List[ResearchTrailSuggestion]:
        """Extract potential research trails from a finding."""
        trails = []
        
        # Look for interesting keywords or concepts
        content_lower = finding.content.lower()
        
        # Identify potential tangents based on keywords
        tangent_indicators = [
            'related to', 'connected to', 'similar to', 'also known as',
            'see also', 'further reading', 'more information',
            'additionally', 'furthermore', 'moreover'
        ]
        
        for indicator in tangent_indicators:
            if indicator in content_lower:
                # Extract context around the indicator
                idx = content_lower.find(indicator)
                context = finding.content[max(0, idx-50):min(len(finding.content), idx+100)]
                
                # Create trail suggestion
                trail = ResearchTrailSuggestion(
                    trail_query=f"More about: {context[:50]}...",
                    relevance_score=0.7,
                    reason=f"Found related concept in finding from {finding.source}"
                )
                trails.append(trail)
        
        return trails
    
    def score_trail_relevance(
        self,
        trail_query: str,
        original_query: str,
        findings: List[Finding]
    ) -> float:
        """
        Score how relevant a trail is to the original research.
        Returns score from 0.0 to 1.0.
        """
        # Simple keyword overlap scoring
        trail_terms = set(trail_query.lower().split())
        query_terms = set(original_query.lower().split())
        
        # Calculate overlap
        overlap = len(trail_terms & query_terms)
        relevance = min(1.0, overlap / max(len(query_terms), 1))
        
        # Boost if trail appears in multiple findings
        mention_count = sum(
            1 for f in findings
            if any(term in f.content.lower() for term in trail_terms)
        )
        
        if mention_count > 1:
            relevance = min(1.0, relevance + 0.2)
        
        return relevance
    
    def detect_novelty(
        self,
        trail_query: str,
        existing_findings: List[Finding]
    ) -> float:
        """
        Detect how novel a trail is compared to existing findings.
        Returns novelty score from 0.0 (redundant) to 1.0 (very novel).
        """
        trail_terms = set(trail_query.lower().split())
        
        # Check overlap with existing findings
        max_overlap = 0.0
        for finding in existing_findings:
            finding_terms = set(finding.content.lower().split())
            overlap = len(trail_terms & finding_terms) / max(len(trail_terms), 1)
            max_overlap = max(max_overlap, overlap)
        
        # Novelty is inverse of overlap
        novelty = 1.0 - max_overlap
        
        return novelty
    
    def prioritize_trails(
        self,
        trails: List[ResearchTrailSuggestion],
        original_query: str,
        findings: List[Finding]
    ) -> List[ResearchTrailSuggestion]:
        """
        Prioritize trails based on relevance and novelty.
        Returns sorted list of trails.
        """
        scored_trails = []
        
        for trail in trails:
            relevance = self.score_trail_relevance(
                trail.trail_query,
                original_query,
                findings
            )
            novelty = self.detect_novelty(trail.trail_query, findings)
            
            # Combined score (weighted)
            combined_score = (relevance * 0.6) + (novelty * 0.4)
            
            # Update trail relevance score
            trail.relevance_score = combined_score
            scored_trails.append(trail)
        
        # Sort by combined score
        scored_trails.sort(key=lambda t: t.relevance_score, reverse=True)
        
        return scored_trails
    
    def get_discovered_count(self) -> int:
        """Get count of discovered trails."""
        return len(self._discovered_trails)
    
    def reset(self) -> None:
        """Reset discovered trails."""
        self._discovered_trails.clear()
        logger.info("Reset trail discovery state")
