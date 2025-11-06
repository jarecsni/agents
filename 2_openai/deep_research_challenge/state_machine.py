"""
Research state machine for managing workflow transitions.
"""
from typing import Dict, Set, Optional
try:
    from .models import ResearchState, ResearchContext
except ImportError:
    from models import ResearchState, ResearchContext
import logging

logger = logging.getLogger(__name__)


class StateTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


class ResearchStateMachine:
    """
    Manages research workflow states and valid transitions.
    Ensures research progresses through proper phases.
    """
    
    # Define valid state transitions
    TRANSITIONS: Dict[ResearchState, Set[ResearchState]] = {
        ResearchState.INITIALIZING: {
            ResearchState.CLARIFYING,
            ResearchState.PLANNING,
            ResearchState.FAILED
        },
        ResearchState.CLARIFYING: {
            ResearchState.PLANNING,
            ResearchState.FAILED
        },
        ResearchState.PLANNING: {
            ResearchState.SEARCHING,
            ResearchState.FAILED
        },
        ResearchState.SEARCHING: {
            ResearchState.EVALUATING,
            ResearchState.FAILED
        },
        ResearchState.EVALUATING: {
            ResearchState.TRAIL_FOLLOWING,
            ResearchState.SYNTHESIZING,
            ResearchState.SEARCHING,  # Can go back for more searches
            ResearchState.FAILED
        },
        ResearchState.TRAIL_FOLLOWING: {
            ResearchState.EVALUATING,
            ResearchState.SYNTHESIZING,
            ResearchState.FAILED
        },
        ResearchState.SYNTHESIZING: {
            ResearchState.COMPLETED,
            ResearchState.FAILED
        },
        ResearchState.COMPLETED: set(),  # Terminal state
        ResearchState.FAILED: set()  # Terminal state
    }
    
    def __init__(self, context: ResearchContext):
        self.context = context
        self._state_history: list[ResearchState] = [context.state]
    
    def can_transition(self, to_state: ResearchState) -> bool:
        """Check if transition to new state is valid."""
        current_state = self.context.state
        return to_state in self.TRANSITIONS.get(current_state, set())
    
    def transition(self, to_state: ResearchState, reason: str = "") -> None:
        """
        Transition to a new state.
        Raises StateTransitionError if transition is invalid.
        """
        current_state = self.context.state
        
        if not self.can_transition(to_state):
            raise StateTransitionError(
                f"Invalid transition from {current_state.value} to {to_state.value}"
            )
        
        logger.info(
            f"State transition: {current_state.value} -> {to_state.value}"
            + (f" (reason: {reason})" if reason else "")
        )
        
        self.context.update_state(to_state)
        self._state_history.append(to_state)
    
    def get_valid_transitions(self) -> Set[ResearchState]:
        """Get all valid transitions from current state."""
        return self.TRANSITIONS.get(self.context.state, set())
    
    def is_terminal_state(self) -> bool:
        """Check if current state is terminal."""
        return self.context.state in {ResearchState.COMPLETED, ResearchState.FAILED}
    
    def get_state_history(self) -> list[ResearchState]:
        """Get history of state transitions."""
        return self._state_history.copy()
    
    def force_fail(self, reason: str) -> None:
        """Force transition to FAILED state from any state."""
        logger.error(f"Forcing failure: {reason}")
        self.context.update_state(ResearchState.FAILED)
        self.context.metadata['failure_reason'] = reason
        self._state_history.append(ResearchState.FAILED)
    
    def get_state_description(self, state: Optional[ResearchState] = None) -> str:
        """Get human-readable description of a state."""
        if state is None:
            state = self.context.state
        
        descriptions = {
            ResearchState.INITIALIZING: "Setting up research context and budget",
            ResearchState.CLARIFYING: "Gathering clarifications from user",
            ResearchState.PLANNING: "Creating research plan",
            ResearchState.SEARCHING: "Executing search operations",
            ResearchState.EVALUATING: "Assessing research quality and gaps",
            ResearchState.TRAIL_FOLLOWING: "Exploring interesting research trails",
            ResearchState.SYNTHESIZING: "Combining findings into report",
            ResearchState.COMPLETED: "Research completed successfully",
            ResearchState.FAILED: "Research failed"
        }
        
        return descriptions.get(state, "Unknown state")
    
    def __str__(self) -> str:
        """String representation."""
        return f"StateMachine(current={self.context.state.value}, history={len(self._state_history)} states)"
