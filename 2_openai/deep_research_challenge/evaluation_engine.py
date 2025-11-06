"""
Evaluation engine for assessing research quality and identifying gaps.
"""
from typing import List, Dict, Any
try:
    from .models import Finding, Gap, QualityScore
except ImportError:
    from models import Finding, Gap, QualityScore
from agents import Agent
import logging

logger = logging.getLogger(__name__)


class QualityAssessor:
    """Assesses research quality using multiple metrics."""
    
    def __init__(self):
        # Create evaluation agent
        self.evaluation_agent = Agent(
            name="QualityEvaluator",
            instructions="""You are a research quality evaluator. Assess research findings for:
            1. Completeness: How well does the research cover the query?
            2. Credibility: How reliable are the sources?
            3. Relevance: How relevant are findings to the query?
            4. Confidence: How confident can we be in the findings?
            
            Provide scores from 0.0 to 1.0 for each metric and explain your reasoning.""",
            model="gpt-4o-mini"
        )
    
    async def assess_quality(
        self,
        query: str,
        findings: List[Finding]
    ) -> QualityScore:
        """
        Assess overall quality of research findings.
        Returns quality scores across multiple dimensions.
        """
        if not findings:
            logger.warning("No findings to assess")
            return QualityScore(
                completeness=0.0,
                credibility=0.0,
                relevance=0.0,
                confidence=0.0,
                overall=0.0
            )
        
        # Calculate basic metrics
        completeness = self._assess_completeness(query, findings)
        credibility = self._assess_credibility(findings)
        relevance = self._assess_relevance(query, findings)
        confidence = self._calculate_confidence(findings)
        
        # Calculate weighted overall score
        overall = (
            completeness * 0.3 +
            credibility * 0.25 +
            relevance * 0.3 +
            confidence * 0.15
        )
        
        logger.info(
            f"Quality assessment: completeness={completeness:.2f}, "
            f"credibility={credibility:.2f}, relevance={relevance:.2f}, "
            f"confidence={confidence:.2f}, overall={overall:.2f}"
        )
        
        return QualityScore(
            completeness=completeness,
            credibility=credibility,
            relevance=relevance,
            confidence=confidence,
            overall=overall
        )
    
    def _assess_completeness(self, query: str, findings: List[Finding]) -> float:
        """Assess how completely the findings address the query."""
        # Simple heuristic: more findings = more complete (with diminishing returns)
        finding_count = len(findings)
        
        if finding_count == 0:
            return 0.0
        elif finding_count < 3:
            return 0.4
        elif finding_count < 5:
            return 0.6
        elif finding_count < 10:
            return 0.8
        else:
            return 0.9
    
    def _assess_credibility(self, findings: List[Finding]) -> float:
        """Assess credibility of sources."""
        if not findings:
            return 0.0
        
        # Use confidence scores from findings as proxy for credibility
        avg_confidence = sum(f.confidence for f in findings) / len(findings)
        return avg_confidence
    
    def _assess_relevance(self, query: str, findings: List[Finding]) -> float:
        """Assess relevance of findings to query."""
        # Simple keyword-based relevance (could be enhanced with embeddings)
        if not findings:
            return 0.0
        
        query_terms = set(query.lower().split())
        
        relevance_scores = []
        for finding in findings:
            content_terms = set(finding.content.lower().split())
            overlap = len(query_terms & content_terms)
            relevance = min(1.0, overlap / max(len(query_terms), 1))
            relevance_scores.append(relevance)
        
        return sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
    
    def _calculate_confidence(self, findings: List[Finding]) -> float:
        """Calculate overall confidence in findings."""
        if not findings:
            return 0.0
        
        # Average confidence across all findings
        return sum(f.confidence for f in findings) / len(findings)


class GapDetector:
    """Identifies gaps in research coverage."""
    
    def __init__(self):
        self.gap_detection_agent = Agent(
            name="GapDetector",
            instructions="""You are a research gap analyzer. Given a query and current findings,
            identify what's missing or needs more investigation. List specific gaps and suggest
            queries to fill them. Be concise and actionable.""",
            model="gpt-4o-mini"
        )
    
    async def detect_gaps(
        self,
        query: str,
        findings: List[Finding],
        quality_score: QualityScore
    ) -> List[Gap]:
        """
        Identify gaps in research coverage.
        Returns list of gaps with priorities.
        """
        gaps = []
        
        # Check for low completeness
        if quality_score.completeness < 0.7:
            gaps.append(Gap(
                description="Research coverage is incomplete",
                priority=0.9,
                suggested_queries=[f"More information about {query}"]
            ))
        
        # Check for low credibility
        if quality_score.credibility < 0.6:
            gaps.append(Gap(
                description="Source credibility is low",
                priority=0.7,
                suggested_queries=[f"Authoritative sources on {query}"]
            ))
        
        # Check for insufficient findings
        if len(findings) < 5:
            gaps.append(Gap(
                description="Insufficient research depth",
                priority=0.8,
                suggested_queries=[
                    f"Detailed analysis of {query}",
                    f"Expert perspectives on {query}"
                ]
            ))
        
        logger.info(f"Detected {len(gaps)} research gaps")
        return gaps


class CredibilityScorer:
    """Scores source credibility."""
    
    def score_source(self, source: str) -> float:
        """
        Score credibility of a source.
        Returns score from 0.0 to 1.0.
        """
        # Simple heuristic based on source characteristics
        source_lower = source.lower()
        
        # High credibility indicators
        high_cred = ['.edu', '.gov', 'wikipedia', 'scholar', 'research', 'journal']
        # Medium credibility indicators
        med_cred = ['.org', 'news', 'article']
        # Low credibility indicators
        low_cred = ['blog', 'forum', 'social']
        
        if any(indicator in source_lower for indicator in high_cred):
            return 0.9
        elif any(indicator in source_lower for indicator in med_cred):
            return 0.7
        elif any(indicator in source_lower for indicator in low_cred):
            return 0.5
        else:
            return 0.6  # Default moderate credibility
    
    def score_findings(self, findings: List[Finding]) -> Dict[str, float]:
        """Score credibility of all findings."""
        return {
            finding.id: self.score_source(finding.source)
            for finding in findings
        }


class SynthesisValidator:
    """Validates synthesis of research findings."""
    
    def check_coherence(self, findings: List[Finding]) -> float:
        """
        Check if findings are coherent and consistent.
        Returns coherence score from 0.0 to 1.0.
        """
        if len(findings) < 2:
            return 1.0  # Single finding is trivially coherent
        
        # Simple heuristic: assume findings are mostly coherent
        # In production, this would use semantic similarity
        return 0.8
    
    def detect_contradictions(self, findings: List[Finding]) -> List[tuple]:
        """
        Detect contradictions between findings.
        Returns list of (finding1_id, finding2_id, description) tuples.
        """
        # Placeholder - would need semantic analysis in production
        contradictions = []
        logger.debug(f"Checked {len(findings)} findings for contradictions")
        return contradictions


class EvaluationEngine:
    """
    Main evaluation engine coordinating quality assessment,
    gap detection, and credibility scoring.
    """
    
    def __init__(self):
        self.quality_assessor = QualityAssessor()
        self.gap_detector = GapDetector()
        self.credibility_scorer = CredibilityScorer()
        self.synthesis_validator = SynthesisValidator()
    
    async def evaluate(
        self,
        query: str,
        findings: List[Finding]
    ) -> QualityScore:
        """
        Perform complete evaluation of research findings.
        Returns quality score with identified gaps.
        """
        logger.info(f"Evaluating {len(findings)} findings for query: {query}")
        
        # Assess quality
        quality_score = await self.quality_assessor.assess_quality(query, findings)
        
        # Detect gaps
        gaps = await self.gap_detector.detect_gaps(query, findings, quality_score)
        quality_score.gaps_identified = gaps
        
        # Score credibility
        credibility_scores = self.credibility_scorer.score_findings(findings)
        logger.debug(f"Credibility scores: {credibility_scores}")
        
        return quality_score
    
    async def validate_synthesis(self, findings: List[Finding]) -> Dict[str, Any]:
        """Validate synthesis of findings."""
        coherence = self.synthesis_validator.check_coherence(findings)
        contradictions = self.synthesis_validator.detect_contradictions(findings)
        
        return {
            'coherence_score': coherence,
            'contradictions': contradictions,
            'is_valid': coherence > 0.6 and len(contradictions) == 0
        }
