"""Unit tests for core data models."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from datetime import datetime
from models import (
    ResearchContext, ResearchState, Finding, Gap, QualityScore,
    HandoffRecord, ResearchTrail, TrailStatus, ResourceUsage
)
from budget import ResearchBudget


class TestResourceUsage:
    """Test ResourceUsage model."""
    
    def test_creation(self):
        usage = ResourceUsage(tokens_used=100, api_calls=5, time_seconds=10.5)
        assert usage.tokens_used == 100
        assert usage.api_calls == 5
        assert usage.time_seconds == 10.5
    
    def test_add(self):
        usage1 = ResourceUsage(tokens_used=100, api_calls=5, time_seconds=10.0)
        usage2 = ResourceUsage(tokens_used=50, api_calls=2, time_seconds=5.0)
        usage1.add(usage2)
        assert usage1.tokens_used == 150
        assert usage1.api_calls == 7
        assert usage1.time_seconds == 15.0
    
    def test_serialization(self):
        usage = ResourceUsage(tokens_used=100, api_calls=5, time_seconds=10.5)
        data = usage.to_dict()
        restored = ResourceUsage.from_dict(data)
        assert restored.tokens_used == usage.tokens_used
        assert restored.api_calls == usage.api_calls
        assert restored.time_seconds == usage.time_seconds


class TestFinding:
    """Test Finding model."""
    
    def test_creation(self):
        finding = Finding(
            id="test-1",
            content="test content",
            source="test source",
            timestamp=datetime.now(),
            confidence=0.8
        )
        assert finding.id == "test-1"
        assert finding.content == "test content"
        assert finding.confidence == 0.8
    
    def test_serialization(self):
        finding = Finding(
            id="test-1",
            content="test content",
            source="test source",
            timestamp=datetime.now()
        )
        data = finding.to_dict()
        restored = Finding.from_dict(data)
        assert restored.id == finding.id
        assert restored.content == finding.content
        assert restored.source == finding.source


class TestResearchContext:
    """Test ResearchContext model."""
    
    def test_creation(self):
        context = ResearchContext(query="test query")
        assert context.query == "test query"
        assert context.state == ResearchState.INITIALIZING
        assert len(context.findings) == 0
        assert len(context.research_trails) == 0
    
    def test_add_finding(self):
        context = ResearchContext(query="test")
        finding = Finding(
            id="f1",
            content="content",
            source="source",
            timestamp=datetime.now()
        )
        context.add_finding(finding)
        assert len(context.findings) == 1
        assert context.findings[0].id == "f1"
    
    def test_update_state(self):
        context = ResearchContext(query="test")
        initial_time = context.updated_at
        context.update_state(ResearchState.PLANNING)
        assert context.state == ResearchState.PLANNING
        assert context.updated_at > initial_time
    
    def test_add_clarification(self):
        context = ResearchContext(query="test")
        context.add_clarification("What scope?", "Technical details")
        assert "What scope?" in context.clarifications
        assert context.clarifications["What scope?"] == "Technical details"
    
    def test_serialization(self):
        context = ResearchContext(query="test query")
        context.update_state(ResearchState.PLANNING)
        finding = Finding(
            id="f1",
            content="content",
            source="source",
            timestamp=datetime.now()
        )
        context.add_finding(finding)
        
        # Serialize
        data = context.to_dict()
        json_str = context.to_json()
        
        # Deserialize
        restored_from_dict = ResearchContext.from_dict(data)
        restored_from_json = ResearchContext.from_json(json_str)
        
        assert restored_from_dict.query == context.query
        assert restored_from_dict.state == context.state
        assert len(restored_from_dict.findings) == 1
        
        assert restored_from_json.query == context.query
    
    def test_validation(self):
        context = ResearchContext(query="test")
        assert context.validate() is True
        
        context.query = ""
        assert context.validate() is False


class TestQualityScore:
    """Test QualityScore model."""
    
    def test_creation(self):
        score = QualityScore(
            completeness=0.8,
            credibility=0.7,
            relevance=0.9,
            confidence=0.75,
            overall=0.8
        )
        assert score.completeness == 0.8
        assert score.overall == 0.8
    
    def test_with_gaps(self):
        gap = Gap(
            description="Missing information",
            priority=0.8,
            suggested_queries=["query1", "query2"]
        )
        score = QualityScore(
            completeness=0.6,
            credibility=0.7,
            relevance=0.8,
            confidence=0.7,
            overall=0.7,
            gaps_identified=[gap]
        )
        assert len(score.gaps_identified) == 1
        assert score.gaps_identified[0].description == "Missing information"
    
    def test_serialization(self):
        gap = Gap(description="test gap", priority=0.8)
        score = QualityScore(
            completeness=0.8,
            credibility=0.7,
            relevance=0.9,
            confidence=0.75,
            overall=0.8,
            gaps_identified=[gap]
        )
        data = score.to_dict()
        restored = QualityScore.from_dict(data)
        assert restored.completeness == score.completeness
        assert len(restored.gaps_identified) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
