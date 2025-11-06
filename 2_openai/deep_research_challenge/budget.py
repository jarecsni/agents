"""
Budget management system for controlling resource usage in autonomous research.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

try:
    from .models import ResourceUsage
except ImportError:
    from models import ResourceUsage


@dataclass
class Operation:
    """Represents a resource-consuming operation."""
    name: str
    estimated_tokens: int
    estimated_api_calls: int = 1
    estimated_time_seconds: float = 0.0
    
    def to_usage(self) -> ResourceUsage:
        """Convert to ResourceUsage."""
        return ResourceUsage(
            tokens_used=self.estimated_tokens,
            api_calls=self.estimated_api_calls,
            time_seconds=self.estimated_time_seconds
        )


@dataclass
class ResearchBudget:
    """
    Manages and enforces resource limits for autonomous research.
    Tracks token usage, API calls, time, and trail depth.
    """
    max_tokens: int
    max_time_seconds: float
    max_api_calls: int
    max_trail_depth: int
    current_usage: ResourceUsage = field(default_factory=ResourceUsage)
    trail_depth: int = 0
    
    def can_afford(self, operation: Operation) -> bool:
        """Check if budget can afford an operation."""
        if self.current_usage.tokens_used + operation.estimated_tokens > self.max_tokens:
            return False
        if self.current_usage.api_calls + operation.estimated_api_calls > self.max_api_calls:
            return False
        if self.current_usage.time_seconds + operation.estimated_time_seconds > self.max_time_seconds:
            return False
        return True
    
    def can_afford_trail(self) -> bool:
        """Check if budget allows another trail depth level."""
        return self.trail_depth < self.max_trail_depth
    
    def consume(self, operation: Operation) -> None:
        """Consume budget for an operation."""
        usage = operation.to_usage()
        self.current_usage.add(usage)
    
    def consume_usage(self, usage: ResourceUsage) -> None:
        """Consume budget from ResourceUsage."""
        self.current_usage.add(usage)
    
    def increment_trail_depth(self) -> None:
        """Increment trail depth counter."""
        self.trail_depth += 1
    
    def decrement_trail_depth(self) -> None:
        """Decrement trail depth counter."""
        if self.trail_depth > 0:
            self.trail_depth -= 1
    
    def remaining(self) -> ResourceUsage:
        """Calculate remaining budget."""
        return ResourceUsage(
            tokens_used=max(0, self.max_tokens - self.current_usage.tokens_used),
            api_calls=max(0, self.max_api_calls - self.current_usage.api_calls),
            time_seconds=max(0.0, self.max_time_seconds - self.current_usage.time_seconds)
        )
    
    def utilization_percent(self) -> Dict[str, float]:
        """Calculate budget utilization percentages."""
        return {
            'tokens': (self.current_usage.tokens_used / self.max_tokens * 100) if self.max_tokens > 0 else 0,
            'api_calls': (self.current_usage.api_calls / self.max_api_calls * 100) if self.max_api_calls > 0 else 0,
            'time': (self.current_usage.time_seconds / self.max_time_seconds * 100) if self.max_time_seconds > 0 else 0,
            'trail_depth': (self.trail_depth / self.max_trail_depth * 100) if self.max_trail_depth > 0 else 0
        }
    
    def is_exhausted(self) -> bool:
        """Check if budget is exhausted."""
        return (
            self.current_usage.tokens_used >= self.max_tokens or
            self.current_usage.api_calls >= self.max_api_calls or
            self.current_usage.time_seconds >= self.max_time_seconds
        )
    
    def is_near_limit(self, threshold: float = 0.9) -> bool:
        """Check if budget is near any limit (default 90%)."""
        util = self.utilization_percent()
        return any(v >= threshold * 100 for v in util.values())
    
    def allocate_for_trail(self, percentage: float = 0.2) -> 'ResearchBudget':
        """
        Allocate a portion of remaining budget for a research trail.
        Returns a new ResearchBudget with allocated resources.
        """
        remaining = self.remaining()
        return ResearchBudget(
            max_tokens=int(remaining.tokens_used * percentage),
            max_time_seconds=remaining.time_seconds * percentage,
            max_api_calls=int(remaining.api_calls * percentage),
            max_trail_depth=max(1, self.max_trail_depth - self.trail_depth - 1)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'max_tokens': self.max_tokens,
            'max_time_seconds': self.max_time_seconds,
            'max_api_calls': self.max_api_calls,
            'max_trail_depth': self.max_trail_depth,
            'current_usage': self.current_usage.to_dict(),
            'trail_depth': self.trail_depth
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResearchBudget':
        """Deserialize from dictionary."""
        data['current_usage'] = ResourceUsage.from_dict(data.get('current_usage', {}))
        return cls(**data)
    
    @classmethod
    def create_default(cls) -> 'ResearchBudget':
        """Create a default budget for development."""
        return cls(
            max_tokens=50000,
            max_time_seconds=300.0,
            max_api_calls=50,
            max_trail_depth=3
        )
    
    @classmethod
    def create_development(cls) -> 'ResearchBudget':
        """Create a tight budget for development/testing."""
        return cls(
            max_tokens=10000,
            max_time_seconds=60.0,
            max_api_calls=10,
            max_trail_depth=1
        )
    
    @classmethod
    def create_production(cls) -> 'ResearchBudget':
        """Create a production budget."""
        return cls(
            max_tokens=200000,
            max_time_seconds=600.0,
            max_api_calls=200,
            max_trail_depth=5
        )
    
    def __str__(self) -> str:
        """String representation."""
        util = self.utilization_percent()
        return (
            f"Budget(tokens: {self.current_usage.tokens_used}/{self.max_tokens} ({util['tokens']:.1f}%), "
            f"calls: {self.current_usage.api_calls}/{self.max_api_calls} ({util['api_calls']:.1f}%), "
            f"time: {self.current_usage.time_seconds:.1f}/{self.max_time_seconds}s ({util['time']:.1f}%), "
            f"trail_depth: {self.trail_depth}/{self.max_trail_depth})"
        )
