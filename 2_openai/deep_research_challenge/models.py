"""
Core data models for the Autonomous Deep Research System.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json


class ResearchState(Enum):
    """Research workflow states."""
    INITIALIZING = "initializing"
    CLARIFYING = "clarifying"
    PLANNING = "planning"
    SEARCHING = "searching"
    EVALUATING = "evaluating"
    TRAIL_FOLLOWING = "trail_following"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"


class TrailStatus(Enum):
    """Research trail status."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Capability(Enum):
    """Agent capabilities."""
    PLANNING = "planning"
    SEARCHING = "searching"
    WRITING = "writing"
    EVALUATION = "evaluation"
    CLARIFICATION = "clarification"
    EMAIL = "email"


@dataclass
class ResourceUsage:
    """Tracks resource consumption."""
    tokens_used: int = 0
    api_calls: int = 0
    time_seconds: float = 0.0
    
    def add(self, other: 'ResourceUsage') -> None:
        """Add another ResourceUsage to this one."""
        self.tokens_used += other.tokens_used
        self.api_calls += other.api_calls
        self.time_seconds += other.time_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'tokens_used': self.tokens_used,
            'api_calls': self.api_calls,
            'time_seconds': self.time_seconds
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourceUsage':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Finding:
    """Represents a research finding."""
    id: str
    content: str
    source: str
    timestamp: datetime
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'content': self.content,
            'source': self.source,
            'timestamp': self.timestamp.isoformat(),
            'confidence': self.confidence,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Finding':
        """Create from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class Gap:
    """Represents an identified research gap."""
    description: str
    priority: float
    suggested_queries: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'description': self.description,
            'priority': self.priority,
            'suggested_queries': self.suggested_queries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Gap':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class QualityScore:
    """Quality assessment scores."""
    completeness: float
    credibility: float
    relevance: float
    confidence: float
    overall: float
    gaps_identified: List[Gap] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'completeness': self.completeness,
            'credibility': self.credibility,
            'relevance': self.relevance,
            'confidence': self.confidence,
            'overall': self.overall,
            'gaps_identified': [g.to_dict() for g in self.gaps_identified]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QualityScore':
        """Create from dictionary."""
        data['gaps_identified'] = [Gap.from_dict(g) for g in data.get('gaps_identified', [])]
        return cls(**data)


@dataclass
class HandoffRecord:
    """Records an agent handoff."""
    from_agent: str
    to_agent: str
    reason: str
    timestamp: datetime
    context_summary: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'from_agent': self.from_agent,
            'to_agent': self.to_agent,
            'reason': self.reason,
            'timestamp': self.timestamp.isoformat(),
            'context_summary': self.context_summary
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HandoffRecord':
        """Create from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class ResearchTrail:
    """Represents an autonomous research trail."""
    id: str
    origin_finding_id: Optional[str]
    trail_query: str
    relevance_score: float
    budget_allocated: 'ResearchBudget'
    findings: List[Finding] = field(default_factory=list)
    status: TrailStatus = TrailStatus.PENDING
    breadcrumbs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'origin_finding_id': self.origin_finding_id,
            'trail_query': self.trail_query,
            'relevance_score': self.relevance_score,
            'budget_allocated': self.budget_allocated.to_dict(),
            'findings': [f.to_dict() for f in self.findings],
            'status': self.status.value,
            'breadcrumbs': self.breadcrumbs
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResearchTrail':
        """Create from dictionary."""
        from .budget import ResearchBudget
        data['budget_allocated'] = ResearchBudget.from_dict(data['budget_allocated'])
        data['findings'] = [Finding.from_dict(f) for f in data.get('findings', [])]
        data['status'] = TrailStatus(data['status'])
        return cls(**data)


@dataclass
class ResearchContext:
    """
    Maintains complete research context across agent handoffs.
    Supports serialization for persistence and state recovery.
    """
    query: str
    state: ResearchState = ResearchState.INITIALIZING
    clarifications: Dict[str, str] = field(default_factory=dict)
    findings: List[Finding] = field(default_factory=list)
    research_trails: List[ResearchTrail] = field(default_factory=list)
    budget_used: ResourceUsage = field(default_factory=ResourceUsage)
    quality_scores: List[QualityScore] = field(default_factory=list)
    handoff_history: List[HandoffRecord] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_finding(self, finding: Finding) -> None:
        """Add a finding to the context."""
        self.findings.append(finding)
        self.updated_at = datetime.now()
    
    def add_trail(self, trail: ResearchTrail) -> None:
        """Add a research trail."""
        self.research_trails.append(trail)
        self.updated_at = datetime.now()
    
    def add_handoff(self, handoff: HandoffRecord) -> None:
        """Record an agent handoff."""
        self.handoff_history.append(handoff)
        self.updated_at = datetime.now()
    
    def update_state(self, new_state: ResearchState) -> None:
        """Update research state."""
        self.state = new_state
        self.updated_at = datetime.now()
    
    def add_clarification(self, question: str, answer: str) -> None:
        """Add a clarification."""
        self.clarifications[question] = answer
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'query': self.query,
            'state': self.state.value,
            'clarifications': self.clarifications,
            'findings': [f.to_dict() for f in self.findings],
            'research_trails': [t.to_dict() for t in self.research_trails],
            'budget_used': self.budget_used.to_dict(),
            'quality_scores': [q.to_dict() for q in self.quality_scores],
            'handoff_history': [h.to_dict() for h in self.handoff_history],
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResearchContext':
        """Deserialize from dictionary."""
        data['state'] = ResearchState(data['state'])
        data['findings'] = [Finding.from_dict(f) for f in data.get('findings', [])]
        data['research_trails'] = [ResearchTrail.from_dict(t) for t in data.get('research_trails', [])]
        data['budget_used'] = ResourceUsage.from_dict(data.get('budget_used', {}))
        data['quality_scores'] = [QualityScore.from_dict(q) for q in data.get('quality_scores', [])]
        data['handoff_history'] = [HandoffRecord.from_dict(h) for h in data.get('handoff_history', [])]
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ResearchContext':
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    def validate(self) -> bool:
        """Validate context integrity."""
        if not self.query:
            return False
        if not isinstance(self.state, ResearchState):
            return False
        return True
