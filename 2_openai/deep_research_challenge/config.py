"""
Configuration system for the Autonomous Deep Research System.
"""
from dataclasses import dataclass
from typing import Dict, Any
import os


@dataclass
class BudgetConfig:
    """Budget configuration."""
    max_tokens: int = 50000
    max_time_seconds: float = 300.0
    max_api_calls: int = 50
    max_trail_depth: int = 3
    trail_budget_percentage: float = 0.2
    
    @classmethod
    def from_env(cls) -> 'BudgetConfig':
        """Load from environment variables."""
        return cls(
            max_tokens=int(os.getenv('RESEARCH_MAX_TOKENS', 50000)),
            max_time_seconds=float(os.getenv('RESEARCH_MAX_TIME', 300.0)),
            max_api_calls=int(os.getenv('RESEARCH_MAX_API_CALLS', 50)),
            max_trail_depth=int(os.getenv('RESEARCH_MAX_TRAIL_DEPTH', 3)),
            trail_budget_percentage=float(os.getenv('RESEARCH_TRAIL_BUDGET_PCT', 0.2))
        )


@dataclass
class QualityConfig:
    """Quality assessment configuration."""
    min_completeness: float = 0.7
    min_credibility: float = 0.6
    min_relevance: float = 0.7
    min_confidence: float = 0.6
    min_overall: float = 0.65
    
    @classmethod
    def from_env(cls) -> 'QualityConfig':
        """Load from environment variables."""
        return cls(
            min_completeness=float(os.getenv('QUALITY_MIN_COMPLETENESS', 0.7)),
            min_credibility=float(os.getenv('QUALITY_MIN_CREDIBILITY', 0.6)),
            min_relevance=float(os.getenv('QUALITY_MIN_RELEVANCE', 0.7)),
            min_confidence=float(os.getenv('QUALITY_MIN_CONFIDENCE', 0.6)),
            min_overall=float(os.getenv('QUALITY_MIN_OVERALL', 0.65))
        )


@dataclass
class ClarificationConfig:
    """Clarification engine configuration."""
    max_questions: int = 5
    ambiguity_threshold: float = 0.5
    enable_follow_up_questions: bool = True
    
    @classmethod
    def from_env(cls) -> 'ClarificationConfig':
        """Load from environment variables."""
        return cls(
            max_questions=int(os.getenv('CLARIFICATION_MAX_QUESTIONS', 5)),
            ambiguity_threshold=float(os.getenv('CLARIFICATION_AMBIGUITY_THRESHOLD', 0.5)),
            enable_follow_up_questions=os.getenv('CLARIFICATION_FOLLOW_UP', 'true').lower() == 'true'
        )


@dataclass
class TrailConfig:
    """Research trail configuration."""
    min_relevance_score: float = 0.6
    max_concurrent_trails: int = 3
    enable_autonomous_trails: bool = True
    
    @classmethod
    def from_env(cls) -> 'TrailConfig':
        """Load from environment variables."""
        return cls(
            min_relevance_score=float(os.getenv('TRAIL_MIN_RELEVANCE', 0.6)),
            max_concurrent_trails=int(os.getenv('TRAIL_MAX_CONCURRENT', 3)),
            enable_autonomous_trails=os.getenv('TRAIL_ENABLE_AUTONOMOUS', 'true').lower() == 'true'
        )


@dataclass
class ResearchConfig:
    """Main research system configuration."""
    budget: BudgetConfig
    quality: QualityConfig
    clarification: ClarificationConfig
    trail: TrailConfig
    development_mode: bool = False
    enable_logging: bool = True
    log_level: str = "INFO"
    
    @classmethod
    def create_default(cls) -> 'ResearchConfig':
        """Create default configuration."""
        return cls(
            budget=BudgetConfig(),
            quality=QualityConfig(),
            clarification=ClarificationConfig(),
            trail=TrailConfig()
        )
    
    @classmethod
    def create_development(cls) -> 'ResearchConfig':
        """Create development configuration with tight limits."""
        return cls(
            budget=BudgetConfig(
                max_tokens=10000,
                max_time_seconds=60.0,
                max_api_calls=10,
                max_trail_depth=1
            ),
            quality=QualityConfig(
                min_completeness=0.6,
                min_credibility=0.5,
                min_relevance=0.6,
                min_confidence=0.5,
                min_overall=0.55
            ),
            clarification=ClarificationConfig(max_questions=3),
            trail=TrailConfig(
                max_concurrent_trails=1,
                enable_autonomous_trails=False
            ),
            development_mode=True,
            log_level="DEBUG"
        )
    
    @classmethod
    def create_production(cls) -> 'ResearchConfig':
        """Create production configuration."""
        return cls(
            budget=BudgetConfig(
                max_tokens=200000,
                max_time_seconds=600.0,
                max_api_calls=200,
                max_trail_depth=5
            ),
            quality=QualityConfig(),
            clarification=ClarificationConfig(),
            trail=TrailConfig(),
            development_mode=False,
            log_level="INFO"
        )
    
    @classmethod
    def from_env(cls) -> 'ResearchConfig':
        """Load configuration from environment variables."""
        mode = os.getenv('RESEARCH_MODE', 'default').lower()
        
        if mode == 'development':
            return cls.create_development()
        elif mode == 'production':
            return cls.create_production()
        else:
            return cls(
                budget=BudgetConfig.from_env(),
                quality=QualityConfig.from_env(),
                clarification=ClarificationConfig.from_env(),
                trail=TrailConfig.from_env(),
                development_mode=os.getenv('RESEARCH_DEV_MODE', 'false').lower() == 'true',
                enable_logging=os.getenv('RESEARCH_ENABLE_LOGGING', 'true').lower() == 'true',
                log_level=os.getenv('RESEARCH_LOG_LEVEL', 'INFO')
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'budget': self.budget.__dict__,
            'quality': self.quality.__dict__,
            'clarification': self.clarification.__dict__,
            'trail': self.trail.__dict__,
            'development_mode': self.development_mode,
            'enable_logging': self.enable_logging,
            'log_level': self.log_level
        }
