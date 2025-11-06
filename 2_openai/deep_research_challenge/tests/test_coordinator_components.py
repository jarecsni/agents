"""Unit tests for coordinator components."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from models import ResearchContext, ResearchState, ResearchTrail, TrailStatus
from state_machine import ResearchStateMachine, StateTransitionError
from trail_manager import TrailManager
from budget import ResearchBudget


class TestStateMachine:
    """Test state machine transitions."""
    
    def test_initial_state(self):
        context = ResearchContext(query="test")
        sm = ResearchStateMachine(context)
        assert context.state == ResearchState.INITIALIZING
    
    def test_valid_transition(self):
        context = ResearchContext(query="test")
        sm = ResearchStateMachine(context)
        
        assert sm.can_transition(ResearchState.PLANNING)
        sm.transition(ResearchState.PLANNING)
        assert context.state == ResearchState.PLANNING
    
    def test_invalid_transition(self):
        context = ResearchContext(query="test")
        sm = ResearchStateMachine(context)
        
        assert not sm.can_transition(ResearchState.COMPLETED)
        with pytest.raises(StateTransitionError):
            sm.transition(ResearchState.COMPLETED)
    
    def test_state_history(self):
        context = ResearchContext(query="test")
        sm = ResearchStateMachine(context)
        
        sm.transition(ResearchState.PLANNING)
        sm.transition(ResearchState.SEARCHING)
        
        history = sm.get_state_history()
        assert len(history) == 3  # INITIALIZING, PLANNING, SEARCHING
        assert history[0] == ResearchState.INITIALIZING
        assert history[2] == ResearchState.SEARCHING
    
    def test_terminal_states(self):
        context = ResearchContext(query="test")
        sm = ResearchStateMachine(context)
        
        assert not sm.is_terminal_state()
        
        # Navigate to completed
        sm.transition(ResearchState.PLANNING)
        sm.transition(ResearchState.SEARCHING)
        sm.transition(ResearchState.EVALUATING)
        sm.transition(ResearchState.SYNTHESIZING)
        sm.transition(ResearchState.COMPLETED)
        
        assert sm.is_terminal_state()
    
    def test_force_fail(self):
        context = ResearchContext(query="test")
        sm = ResearchStateMachine(context)
        
        sm.force_fail("Test failure")
        assert context.state == ResearchState.FAILED
        assert context.metadata['failure_reason'] == "Test failure"


class TestTrailManager:
    """Test trail management."""
    
    def setup_method(self):
        self.manager = TrailManager(max_concurrent_trails=2)
        self.budget = ResearchBudget.create_development()
    
    def test_create_trail(self):
        trail = self.manager.create_trail(
            trail_query="test trail",
            relevance_score=0.8,
            budget=self.budget
        )
        
        assert trail is not None
        assert trail.trail_query == "test trail"
        assert trail.status == TrailStatus.PENDING
    
    def test_duplicate_trail_prevention(self):
        trail1 = self.manager.create_trail(
            trail_query="test trail",
            relevance_score=0.8,
            budget=self.budget
        )
        
        # Try to create duplicate
        trail2 = self.manager.create_trail(
            trail_query="test trail",
            relevance_score=0.7,
            budget=self.budget
        )
        
        assert trail1 is not None
        assert trail2 is None  # Should be rejected
    
    def test_concurrent_trail_limit(self):
        trail1 = self.manager.create_trail("trail1", 0.8, self.budget)
        trail2 = self.manager.create_trail("trail2", 0.7, self.budget)
        trail3 = self.manager.create_trail("trail3", 0.6, self.budget)
        
        assert trail1 is not None
        assert trail2 is not None
        assert trail3 is None  # Exceeds limit of 2
    
    def test_start_trail(self):
        trail = self.manager.create_trail("test", 0.8, self.budget)
        assert self.manager.start_trail(trail.id)
        assert trail.status == TrailStatus.ACTIVE
    
    def test_complete_trail(self):
        trail = self.manager.create_trail("test", 0.8, self.budget)
        self.manager.start_trail(trail.id)
        assert self.manager.complete_trail(trail.id)
        assert trail.status == TrailStatus.COMPLETED
    
    def test_abandon_trail(self):
        trail = self.manager.create_trail("test", 0.8, self.budget)
        assert self.manager.abandon_trail(trail.id, "test reason")
        assert trail.status == TrailStatus.ABANDONED
    
    def test_get_trails_by_status(self):
        trail1 = self.manager.create_trail("trail1", 0.8, self.budget)
        trail2 = self.manager.create_trail("trail2", 0.7, self.budget)
        
        self.manager.start_trail(trail1.id)
        
        active = self.manager.get_active_trails()
        pending = self.manager.get_pending_trails()
        
        assert len(active) == 1
        assert len(pending) == 1
    
    def test_prioritize_trails(self):
        trail1 = self.manager.create_trail("low", 0.5, self.budget)
        trail2 = self.manager.create_trail("high", 0.9, self.budget)
        
        prioritized = self.manager.prioritize_trails()
        assert prioritized[0].relevance_score > prioritized[1].relevance_score
    
    def test_statistics(self):
        self.manager.create_trail("trail1", 0.8, self.budget)
        trail2 = self.manager.create_trail("trail2", 0.7, self.budget)
        self.manager.start_trail(trail2.id)
        self.manager.complete_trail(trail2.id)
        
        stats = self.manager.get_statistics()
        assert stats['total_trails'] == 2
        assert stats['pending_trails'] == 1
        assert stats['completed_trails'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
