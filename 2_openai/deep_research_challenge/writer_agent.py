from pydantic import BaseModel, Field
from agents import Agent

INSTRUCTIONS = (
    "You are a senior researcher tasked with writing a cohesive report for a research query. "
    "You will be provided with the original query, and some initial research done by a research assistant.\n"
    "You should first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output.\n"
    "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
    "for 5-10 pages of content, at least 1000 words."
)

ENHANCED_INSTRUCTIONS = (
    "You are a senior researcher synthesizing findings from multiple research streams. Your task:\n"
    "1. Analyze findings from different research paths and trails\n"
    "2. Identify overlaps, contradictions, and complementary information\n"
    "3. Prioritize information based on source credibility and confidence scores\n"
    "4. Create a cohesive narrative that addresses the original query\n"
    "5. Highlight areas of uncertainty or conflicting information\n"
    "6. Provide confidence levels for key findings\n\n"
    "Generate a comprehensive markdown report (1000+ words) with:\n"
    "- Executive summary with confidence indicators\n"
    "- Main findings organized by theme\n"
    "- Discussion of contradictions or uncertainties\n"
    "- Conclusions with confidence levels\n"
    "- Suggested follow-up research"
)


class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")
    markdown_report: str = Field(description="The final report")
    follow_up_questions: list[str] = Field(description="Suggested topics to research further")


class EnhancedReportData(BaseModel):
    """Enhanced report with confidence and quality metrics."""
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")
    markdown_report: str = Field(description="The final comprehensive report")
    follow_up_questions: list[str] = Field(description="Suggested topics to research further")
    confidence_level: float = Field(
        default=0.7,
        description="Overall confidence in report findings (0.0 to 1.0)"
    )
    contradictions_found: list[str] = Field(
        default=[],
        description="List of contradictions or uncertainties identified"
    )
    key_sources: list[str] = Field(
        default=[],
        description="Most important sources used"
    )


# Original writer agent
writer_agent = Agent(
    name="WriterAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ReportData,
)

# Enhanced writer agent for multi-stream synthesis
enhanced_writer_agent = Agent(
    name="EnhancedWriterAgent",
    instructions=ENHANCED_INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=EnhancedReportData,
)