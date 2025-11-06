"""
Clarification engine for generating and managing clarifying questions.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from agents import Agent
try:
    from .models import Finding
except ImportError:
    from models import Finding
import logging

logger = logging.getLogger(__name__)


@dataclass
class Question:
    """Represents a clarifying question."""
    question: str
    priority: float
    context: str = ""
    
    def __str__(self) -> str:
        return self.question


class AmbiguityDetector:
    """Detects ambiguities in research queries."""
    
    def __init__(self, ambiguity_threshold: float = 0.5):
        self.ambiguity_threshold = ambiguity_threshold
    
    def detect_ambiguity(self, query: str) -> float:
        """
        Detect ambiguity in a query.
        Returns ambiguity score from 0.0 (clear) to 1.0 (very ambiguous).
        """
        # Simple heuristics for ambiguity detection
        ambiguity_score = 0.0
        
        query_lower = query.lower()
        
        # Short queries are often ambiguous
        if len(query.split()) <= 4:  # Changed from < 3 to <= 4
            ambiguity_score += 0.3
        
        # Vague terms indicate ambiguity (increased weight)
        vague_terms = ['something', 'anything', 'stuff', 'things', 'general', 'overview']
        if any(term in query_lower for term in vague_terms):
            ambiguity_score += 0.4  # Increased from 0.3
        
        # Questions without specifics
        if '?' in query and len(query.split()) < 5:
            ambiguity_score += 0.2
        
        # Broad topics
        broad_terms = ['everything', 'all about', 'comprehensive', 'complete']
        if any(term in query_lower for term in broad_terms):
            ambiguity_score += 0.2
        
        return min(1.0, ambiguity_score)
    
    def is_ambiguous(self, query: str) -> bool:
        """Check if query is ambiguous."""
        return self.detect_ambiguity(query) >= self.ambiguity_threshold


class QuestionGenerator:
    """Generates clarifying questions."""
    
    def __init__(self, max_questions: int = 5):
        self.max_questions = max_questions
        self.question_agent = Agent(
            name="QuestionGenerator",
            instructions="""You are a research assistant that asks clarifying questions.
            Given a research query, generate specific, actionable questions that would help
            narrow down and clarify what the user wants to know. Focus on:
            - Scope and depth of research
            - Specific aspects of interest
            - Time period or context
            - Target audience or purpose
            
            Generate 3-5 concise questions.""",
            model="gpt-4o-mini"
        )
    
    async def generate_questions(
        self,
        query: str,
        ambiguity_score: float
    ) -> List[Question]:
        """
        Generate clarifying questions for a query.
        Returns prioritized list of questions.
        """
        if ambiguity_score < 0.3:
            logger.info("Query is clear, no clarification needed")
            return []
        
        # Generate basic clarifying questions
        questions = self._generate_basic_questions(query)
        
        # Prioritize questions
        for q in questions:
            q.priority = ambiguity_score
        
        # Limit to max questions
        questions = questions[:self.max_questions]
        
        logger.info(f"Generated {len(questions)} clarifying questions")
        return questions
    
    def _generate_basic_questions(self, query: str) -> List[Question]:
        """Generate basic clarifying questions."""
        questions = []
        
        # Scope question
        questions.append(Question(
            question=f"What specific aspects of '{query}' are you most interested in?",
            priority=0.8,
            context="scope"
        ))
        
        # Depth question
        questions.append(Question(
            question="Are you looking for a high-level overview or detailed technical information?",
            priority=0.7,
            context="depth"
        ))
        
        # Purpose question
        questions.append(Question(
            question="What will you use this research for?",
            priority=0.6,
            context="purpose"
        ))
        
        # Time frame question
        if any(word in query.lower() for word in ['history', 'development', 'evolution', 'trend']):
            questions.append(Question(
                question="What time period are you interested in?",
                priority=0.7,
                context="timeframe"
            ))
        
        return questions
    
    async def generate_followup_questions(
        self,
        query: str,
        findings: List[Finding]
    ) -> List[Question]:
        """Generate follow-up questions based on research findings."""
        if not findings:
            return []
        
        questions = []
        
        # Check if findings reveal new areas to explore
        if len(findings) > 5:
            questions.append(Question(
                question="Would you like to explore any specific findings in more depth?",
                priority=0.6,
                context="followup"
            ))
        
        logger.info(f"Generated {len(questions)} follow-up questions")
        return questions


class ResponseProcessor:
    """Processes user responses to clarifying questions."""
    
    def process_response(
        self,
        question: Question,
        answer: str
    ) -> Dict[str, str]:
        """
        Process a user's answer to a clarifying question.
        Returns structured clarification data.
        """
        return {
            'question': question.question,
            'answer': answer,
            'context': question.context
        }
    
    def integrate_clarifications(
        self,
        query: str,
        clarifications: Dict[str, str]
    ) -> str:
        """
        Integrate clarifications into an enhanced query.
        Returns refined query string.
        """
        if not clarifications:
            return query
        
        # Build enhanced query
        enhanced_parts = [f"Original query: {query}"]
        
        for question, answer in clarifications.items():
            enhanced_parts.append(f"- {question}: {answer}")
        
        enhanced_query = "\n".join(enhanced_parts)
        
        logger.info("Integrated clarifications into enhanced query")
        return enhanced_query


class ClarificationEngine:
    """
    Main clarification engine coordinating question generation,
    ambiguity detection, and response processing.
    """
    
    def __init__(
        self,
        max_questions: int = 5,
        ambiguity_threshold: float = 0.5,
        enable_followup: bool = True
    ):
        self.max_questions = max_questions
        self.enable_followup = enable_followup
        self.ambiguity_detector = AmbiguityDetector(ambiguity_threshold)
        self.question_generator = QuestionGenerator(max_questions)
        self.response_processor = ResponseProcessor()
    
    async def analyze_query(self, query: str) -> tuple[float, List[Question]]:
        """
        Analyze query and generate clarifying questions if needed.
        Returns (ambiguity_score, questions).
        """
        logger.info(f"Analyzing query: {query}")
        
        # Detect ambiguity
        ambiguity_score = self.ambiguity_detector.detect_ambiguity(query)
        logger.info(f"Ambiguity score: {ambiguity_score:.2f}")
        
        # Generate questions if ambiguous
        questions = []
        if self.ambiguity_detector.is_ambiguous(query):
            questions = await self.question_generator.generate_questions(
                query,
                ambiguity_score
            )
        
        return ambiguity_score, questions
    
    async def generate_followup_questions(
        self,
        query: str,
        findings: List[Finding]
    ) -> List[Question]:
        """Generate follow-up questions based on findings."""
        if not self.enable_followup:
            return []
        
        return await self.question_generator.generate_followup_questions(
            query,
            findings
        )
    
    def process_clarifications(
        self,
        query: str,
        qa_pairs: Dict[str, str]
    ) -> str:
        """
        Process user clarifications and create enhanced query.
        """
        return self.response_processor.integrate_clarifications(query, qa_pairs)
    
    def needs_clarification(self, query: str) -> bool:
        """Check if query needs clarification."""
        return self.ambiguity_detector.is_ambiguous(query)
