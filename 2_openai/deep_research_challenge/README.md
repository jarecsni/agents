# Autonomous Deep Research System

An enhanced multi-agent research platform with autonomous decision-making, quality evaluation, and intelligent trail following.

## Features

- **Autonomous Trail Following**: Automatically explores interesting research tangents within budget limits
- **Quality Evaluation**: Assesses research completeness, credibility, and relevance
- **Multi-Agent Collaboration**: Agents work together using handoffs and tool wrapping
- **Budget Management**: Strict resource controls to prevent runaway costs
- **Clarification Engine**: Asks clarifying questions for ambiguous queries
- **Progress Monitoring**: Real-time status updates and quality metrics

## Architecture

```
Research Coordinator (Hub)
├── Agent Registry (manages all agents)
├── State Machine (workflow management)
├── Budget Manager (resource tracking)
├── Handoff Controller (agent orchestration)
├── Trail Manager (autonomous exploration)
├── Evaluation Engine (quality assessment)
├── Clarification Engine (question generation)
└── Progress Monitor (status tracking)
```

## Components

### Core Infrastructure
- `models.py` - Data models (ResearchContext, Finding, QualityScore, etc.)
- `budget.py` - Budget management and resource tracking
- `config.py` - Configuration system with environment support
- `state_machine.py` - Research workflow state management

### Agent System
- `agent_registry.py` - Agent capability mapping and discovery
- `handoff_controller.py` - Agent-to-agent handoffs with context preservation
- `planner_agent.py` - Research planning (basic and dynamic)
- `search_agent.py` - Web search with quality metrics
- `writer_agent.py` - Report synthesis (basic and enhanced)
- `email_agent.py` - Email delivery

### Autonomous Features
- `trail_manager.py` - Trail lifecycle management with loop prevention
- `trail_discovery.py` - Identifies interesting research tangents
- `trail_execution.py` - Executes trails within budget constraints

### Quality & Evaluation
- `evaluation_engine.py` - Quality assessment, gap detection, credibility scoring
- `clarification_engine.py` - Question generation and ambiguity detection

### UI & Monitoring
- `progress_monitor.py` - Real-time progress tracking
- `deep_research.py` - Gradio UI with mode selection

### Orchestration
- `research_coordinator.py` - Main coordinator integrating all components

## Usage

### Basic Usage

```python
from research_coordinator import ResearchCoordinator
from budget import ResearchBudget

# Create coordinator
coordinator = ResearchCoordinator()

# Run research
async for update in coordinator.conduct_research(
    query="What is quantum computing?",
    budget=ResearchBudget.create_default()
):
    print(update)
```

### Running the UI

```bash
python deep_research.py
```

Then open the Gradio interface and select a research mode:
- **Default (Balanced)**: 50k tokens, 50 API calls, 3 trail depth
- **Development (Fast, Limited)**: 10k tokens, 10 API calls, 1 trail depth
- **Production (Full, Expensive)**: 200k tokens, 200 API calls, 5 trail depth

## Configuration

### Environment Variables

```bash
# Research mode
RESEARCH_MODE=default|development|production

# Budget limits
RESEARCH_MAX_TOKENS=50000
RESEARCH_MAX_TIME=300
RESEARCH_MAX_API_CALLS=50
RESEARCH_MAX_TRAIL_DEPTH=3

# Quality thresholds
QUALITY_MIN_COMPLETENESS=0.7
QUALITY_MIN_CREDIBILITY=0.6
QUALITY_MIN_RELEVANCE=0.7

# Clarification settings
CLARIFICATION_MAX_QUESTIONS=5
CLARIFICATION_AMBIGUITY_THRESHOLD=0.5

# Trail settings
TRAIL_MIN_RELEVANCE=0.6
TRAIL_MAX_CONCURRENT=3
TRAIL_ENABLE_AUTONOMOUS=true

# Logging
LOG_LEVEL=INFO
RESEARCH_ENABLE_LOGGING=true
```

### Programmatic Configuration

```python
from config import ResearchConfig, BudgetConfig

config = ResearchConfig(
    budget=BudgetConfig(
        max_tokens=10000,
        max_api_calls=10,
        max_trail_depth=1
    ),
    development_mode=True
)

coordinator = ResearchCoordinator(config)
```

## Cost Management

The system includes multiple cost control mechanisms:

1. **Budget Enforcement**: Hard limits on tokens, API calls, and time
2. **Trail Depth Limits**: Prevents infinite exploration loops
3. **Breadcrumb Tracking**: Detects and prevents circular research paths
4. **Development Mode**: Tight limits for testing (10k tokens, 10 calls)
5. **Real-time Monitoring**: Track budget utilization during research

### Estimated Costs

**Development Mode** (10k tokens, 10 calls):
- Simple query: $0.05 - $0.15
- Complex query: $0.10 - $0.30

**Default Mode** (50k tokens, 50 calls):
- Simple query: $0.25 - $0.75
- Complex query: $0.50 - $1.50

**Production Mode** (200k tokens, 200 calls):
- Simple query: $1.00 - $3.00
- Complex query: $2.00 - $6.00

*Costs are estimates using gpt-4o-mini pricing*

## Research Workflow

1. **Initialization**: Set up context and budget
2. **Clarification** (optional): Ask clarifying questions if query is ambiguous
3. **Planning**: Create dynamic search plan
4. **Searching**: Execute searches in parallel
5. **Evaluation**: Assess quality and identify gaps
6. **Trail Following** (optional): Explore interesting tangents autonomously
7. **Synthesizing**: Combine findings into coherent report
8. **Completion**: Deliver final report

## State Machine

```
INITIALIZING → CLARIFYING (if ambiguous)
           → PLANNING
CLARIFYING → PLANNING
PLANNING → SEARCHING
SEARCHING → EVALUATING
EVALUATING → TRAIL_FOLLOWING (if gaps found and budget allows)
          → SYNTHESIZING (if quality sufficient)
TRAIL_FOLLOWING → EVALUATING
SYNTHESIZING → COMPLETED
Any State → FAILED (on error or budget exhaustion)
```

## Agent Capabilities

- **PLANNING**: Creates research strategies
- **SEARCHING**: Executes web searches
- **WRITING**: Synthesizes reports
- **EVALUATION**: Assesses quality
- **CLARIFICATION**: Generates questions
- **EMAIL**: Sends reports

## Quality Metrics

Research quality is assessed across multiple dimensions:

- **Completeness** (0.0-1.0): How well findings cover the query
- **Credibility** (0.0-1.0): Reliability of sources
- **Relevance** (0.0-1.0): How relevant findings are to query
- **Confidence** (0.0-1.0): Overall confidence in findings
- **Overall** (0.0-1.0): Weighted average of all metrics

## Development

### Project Structure

```
deep_research_challenge/
├── models.py              # Core data models
├── budget.py              # Budget management
├── config.py              # Configuration
├── state_machine.py       # Workflow states
├── agent_registry.py      # Agent management
├── handoff_controller.py  # Agent handoffs
├── trail_manager.py       # Trail lifecycle
├── trail_discovery.py     # Trail identification
├── trail_execution.py     # Trail execution
├── evaluation_engine.py   # Quality assessment
├── clarification_engine.py # Question generation
├── progress_monitor.py    # Status tracking
├── research_coordinator.py # Main orchestrator
├── planner_agent.py       # Planning agents
├── search_agent.py        # Search agents
├── writer_agent.py        # Writing agents
├── email_agent.py         # Email agent
├── deep_research.py       # Gradio UI
├── logging_config.py      # Logging setup
└── cache.py               # Simple caching

logs/                      # Research logs
```

### Adding New Agents

```python
from agents import Agent
from models import Capability

# Create agent
my_agent = Agent(
    name="MyAgent",
    instructions="Agent instructions...",
    model="gpt-4o-mini"
)

# Register with capability
coordinator.agent_registry.register_agent(
    "my_agent",
    my_agent,
    [Capability.SEARCHING],
    "Agent description"
)
```

## Troubleshooting

### Budget Exhausted
- Reduce `max_tokens`, `max_api_calls`, or `max_trail_depth`
- Use Development mode for testing
- Disable autonomous trails with `TRAIL_ENABLE_AUTONOMOUS=false`

### Low Quality Scores
- Increase search count in planner
- Lower quality thresholds in config
- Enable more research trails

### Slow Performance
- Reduce concurrent trail limit
- Decrease search depth
- Use smaller context sizes for web search

## License

MIT

## Credits

Built with OpenAI Agents SDK and Gradio.
