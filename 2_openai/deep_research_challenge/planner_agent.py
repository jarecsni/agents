from pydantic import BaseModel, Field
from agents import Agent
from typing import Optional

HOW_MANY_SEARCHES = 5

INSTRUCTIONS = f"You are a helpful research assistant. Given a query, come up with a set of web searches \
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."

DYNAMIC_INSTRUCTIONS = """You are an adaptive research planner. Given a query and current research findings,
create a dynamic search plan that:
1. Builds on existing findings
2. Fills identified gaps
3. Respects budget constraints
4. Suggests research trails for interesting tangents

Adjust the number and depth of searches based on budget availability."""


class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")
    priority: float = Field(default=0.5, description="Priority from 0.0 to 1.0")


class ResearchTrailSuggestion(BaseModel):
    trail_query: str = Field(description="Suggested research trail query")
    relevance_score: float = Field(description="Relevance score from 0.0 to 1.0")
    reason: str = Field(description="Why this trail is worth exploring")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")
    suggested_trails: list[ResearchTrailSuggestion] = Field(
        default=[],
        description="Suggested research trails to explore"
    )
    estimated_token_cost: int = Field(default=5000, description="Estimated token cost for this plan")


# Original planner agent
planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=WebSearchPlan,
)

# Enhanced dynamic planner agent
dynamic_planner_agent = Agent(
    name="DynamicPlannerAgent",
    instructions=DYNAMIC_INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=WebSearchPlan,
)