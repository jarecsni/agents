# Project Structure

## Top-Level Organization
The repository is organized by weeks/modules, each focusing on different AI agent frameworks:

```
├── 1_foundations/          # Week 1: Basic AI agent concepts
├── 2_openai/              # Week 2: OpenAI Agents SDK
├── 3_crew/                # Week 3: CrewAI framework
├── 4_langgraph/           # Week 4: LangGraph
├── 5_autogen/             # Week 5: AutoGen
├── 6_mcp/                 # Week 6: Model Context Protocol
├── guides/                # Educational guides and tutorials
├── setup/                 # Platform-specific setup instructions
└── assets/                # Images and media files
```

## Module Structure Pattern
Each numbered module follows a consistent pattern:

```
<module>/
├── 1_lab1.ipynb          # Progressive lab exercises
├── 2_lab2.ipynb
├── 3_lab3.ipynb
├── 4_lab4.ipynb
├── app.py                # Main application (if applicable)
├── community_contributions/  # Student submissions and variations
└── <framework_specific>/  # Additional framework files
```

## Key File Types

### Jupyter Notebooks (.ipynb)
- Primary learning material with step-by-step instructions
- Include markdown explanations, code cells, and outputs
- Often contain HTML tables with styled instructions and warnings
- Progressive difficulty from lab1 to lab4

### Python Applications (app.py, *.py)
- Gradio-based web interfaces for demonstrations
- Modular agent implementations
- Tool definitions and helper functions
- Database and API integrations

### Configuration Files
- `pyproject.toml`: Project dependencies and metadata
- `requirements.txt`: Auto-generated dependency list
- `.env`: API keys and environment variables
- `uv.lock`: Locked dependency versions

## Community Contributions
- Each module has a `community_contributions/` folder
- Contains student variations, improvements, and alternative implementations
- Often includes specialized integrations (Slack, Telegram, email services)
- Demonstrates different approaches to the same concepts

## Special Directories

### `/guides`
- Foundational tutorials and reference material
- Covers Python basics, debugging, APIs, and development practices
- Numbered sequentially for progressive learning

### `/setup`
- Platform-specific installation instructions
- Troubleshooting guides and diagnostics
- Separate files for Windows, Mac, Linux, WSL

### Framework-Specific Patterns
- **CrewAI**: Uses `crewai create crew` structure with `src/` directories
- **LangGraph**: Includes memory databases and checkpoint systems
- **AutoGen**: Features distributed agent patterns
- **MCP**: Server-client architecture with protocol implementations

## Naming Conventions
- Lab files: `<number>_lab<number>.ipynb`
- Main apps: `app.py` (consistent across modules)
- Agent files: `<agent_type>_agent.py`
- Utility files: descriptive names like `research_manager.py`, `sidekick_tools.py`