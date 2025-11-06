from agents import Agent, WebSearchTool, ModelSettings
from pydantic import BaseModel, Field

INSTRUCTIONS = (
    "You are a research assistant. Given a search term, you search the web for that term and "
    "produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 "
    "words. Capture the main points. Write succintly, no need to have complete sentences or good "
    "grammar. This will be consumed by someone synthesizing a report, so its vital you capture the "
    "essence and ignore any fluff. Do not include any additional commentary other than the summary itself."
)

ENHANCED_INSTRUCTIONS = (
    "You are an advanced research assistant. Given a search term, you search the web and produce "
    "a structured summary with quality metrics. For each search:\n"
    "1. Provide a concise 2-3 paragraph summary (less than 300 words)\n"
    "2. Assess source credibility (0.0 to 1.0)\n"
    "3. Rate confidence in findings (0.0 to 1.0)\n"
    "4. List key sources used\n"
    "Focus on capturing essence, ignore fluff. Be succinct and actionable."
)


class SearchResult(BaseModel):
    """Structured search result with quality metrics."""
    summary: str = Field(description="Concise summary of search results")
    source_credibility: float = Field(
        default=0.7,
        description="Credibility score of sources (0.0 to 1.0)"
    )
    confidence: float = Field(
        default=0.7,
        description="Confidence in findings (0.0 to 1.0)"
    )
    key_sources: list[str] = Field(
        default=[],
        description="List of key sources used"
    )


# Original search agent
search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required"),
)

# Enhanced search agent with quality metrics
enhanced_search_agent = Agent(
    name="EnhancedSearchAgent",
    instructions=ENHANCED_INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4o-mini",
    output_type=SearchResult,
    model_settings=ModelSettings(tool_choice="required"),
)