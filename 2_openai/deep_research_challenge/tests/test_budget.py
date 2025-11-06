"""Unit tests for budget management."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from budget import ResearchBudget, Operation
from models import ResourceUsage


class TestOperation:
    """Test Operation model."""
    
    def test_creation(self):
        op = Operation("test_op", estimated_tokens=1000, estimated_api_calls=2)
        assert op.name == "test_op"
        assert op.estimated_tokens == 1000
        assert op.estimated_api_calls == 2
    
    def test_to_usage(self):
        op = Operation("test", estimated_tokens=500, estimated_api_calls=1, estimated_time_seconds=5.0)
        usage = op.to_usage()
        assert usage.tokens_used == 500
        assert usage.api_calls == 1
        assert usage.time_seconds == 5.0


class TestResearchBudget:
    """Test ResearchBudget model."""
    
    def test_creation(self):
        budget = ResearchBudget(
            max_tokens=10000,
            max_time_seconds=60.0,
            max_api_calls=10,
            max_trail_depth=2
        )
        assert budget.max_tokens == 10000
        assert budget.max_api_calls == 10
        assert budget.current_usage.tokens_used == 0
    
    def test_can_afford(self):
        budget = ResearchBudget(
            max_tokens=1000,
            max_time_seconds=60.0,
            max_api_calls=10,
            max_trail_depth=2
        )
        
        # Should afford small operation
        op = Operation("small", estimated_tokens=100)
        assert budget.can_afford(op) is True
        
        # Should not afford large operation
        op_large = Operation("large", estimated_tokens=2000)
        assert budget.can_afford(op_large) is False
    
    def test_consume(self):
        budget = ResearchBudget(
            max_tokens=1000,
            max_time_seconds=60.0,
            max_api_calls=10,
            max_trail_depth=2
        )
        
        op = Operation("test", estimated_tokens=100, estimated_api_calls=1)
        budget.consume(op)
        
        assert budget.current_usage.tokens_used == 100
        assert budget.current_usage.api_calls == 1
    
    def test_remaining(self):
        budget = ResearchBudget(
            max_tokens=1000,
            max_time_seconds=60.0,
            max_api_calls=10,
            max_trail_depth=2
        )
        
        budget.consume(Operation("test", estimated_tokens=300, estimated_api_calls=3))
        
        remaining = budget.remaining()
        assert remaining.tokens_used == 700
        assert remaining.api_calls == 7
    
    def test_utilization_percent(self):
        budget = ResearchBudget(
            max_tokens=1000,
            max_time_seconds=60.0,
            max_api_calls=10,
            max_trail_depth=2
        )
        
        budget.consume(Operation("test", estimated_tokens=500, estimated_api_calls=5))
        
        util = budget.utilization_percent()
        assert util['tokens'] == 50.0
        assert util['api_calls'] == 50.0
    
    def test_is_exhausted(self):
        budget = ResearchBudget(
            max_tokens=1000,
            max_time_seconds=60.0,
            max_api_calls=10,
            max_trail_depth=2
        )
        
        assert budget.is_exhausted() is False
        
        budget.consume(Operation("test", estimated_tokens=1000))
        assert budget.is_exhausted() is True
    
    def test_is_near_limit(self):
        budget = ResearchBudget(
            max_tokens=1000,
            max_time_seconds=60.0,
            max_api_calls=10,
            max_trail_depth=2
        )
        
        assert budget.is_near_limit() is False
        
        budget.consume(Operation("test", estimated_tokens=950))
        assert budget.is_near_limit() is True
    
    def test_trail_depth(self):
        budget = ResearchBudget(
            max_tokens=1000,
            max_time_seconds=60.0,
            max_api_calls=10,
            max_trail_depth=2
        )
        
        assert budget.can_afford_trail() is True
        budget.increment_trail_depth()
        assert budget.trail_depth == 1
        
        budget.increment_trail_depth()
        assert budget.can_afford_trail() is False
        
        budget.decrement_trail_depth()
        assert budget.trail_depth == 1
    
    def test_allocate_for_trail(self):
        budget = ResearchBudget(
            max_tokens=10000,
            max_time_seconds=60.0,
            max_api_calls=10,
            max_trail_depth=2
        )
        
        trail_budget = budget.allocate_for_trail(percentage=0.2)
        assert trail_budget.max_tokens == 2000  # 20% of 10000
        assert trail_budget.max_trail_depth == 1  # One less than parent
    
    def test_serialization(self):
        budget = ResearchBudget(
            max_tokens=1000,
            max_time_seconds=60.0,
            max_api_calls=10,
            max_trail_depth=2
        )
        budget.consume(Operation("test", estimated_tokens=100))
        
        data = budget.to_dict()
        restored = ResearchBudget.from_dict(data)
        
        assert restored.max_tokens == budget.max_tokens
        assert restored.current_usage.tokens_used == 100
    
    def test_preset_budgets(self):
        dev = ResearchBudget.create_development()
        assert dev.max_tokens == 10000
        assert dev.max_trail_depth == 1
        
        default = ResearchBudget.create_default()
        assert default.max_tokens == 50000
        
        prod = ResearchBudget.create_production()
        assert prod.max_tokens == 200000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
