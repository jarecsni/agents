# Technology Stack

## Build System & Package Management
- **Primary**: `uv` (modern Python package manager)
- **Alternative**: `pip` with requirements.txt
- **Project definition**: pyproject.toml with Python >=3.12 requirement

## Core Frameworks & Libraries
- **AI Agents**: OpenAI Agents SDK, CrewAI, LangGraph, AutoGen, MCP
- **LLM APIs**: OpenAI, Anthropic, Google (Gemini), local models via Ollama
- **Web UI**: Gradio for interactive interfaces
- **Notebooks**: Jupyter/IPython for educational content
- **Data Processing**: pandas, numpy, pypdf, BeautifulSoup4
- **HTTP**: httpx, requests for API calls
- **Database**: SQLite with various checkpoint systems

## Development Environment
- **Python Version**: >=3.12 required
- **IDE**: Cursor (primary), VS Code compatible
- **Environment**: .env files for API keys and configuration
- **Testing**: Playwright for browser automation

## Common Commands

### Setup & Installation
```bash
# Install dependencies
uv sync

# Install CrewAI CLI tools (Week 3)
uv tool install crewai
uv tool upgrade crewai
```

### Running Applications
```bash
# Run Jupyter notebooks
jupyter notebook

# Run Gradio apps
python app.py

# Run CrewAI projects
crewai run

# Create new CrewAI project
crewai create crew <project_name>
```

### Development
```bash
# Install new dependencies
uv add <package_name>

# Run Python scripts
python <script_name>.py

# Launch browser-based interfaces
# Most Gradio apps auto-launch with inbrowser=True
```

## Configuration Patterns
- Environment variables in `.env` files
- API keys for OpenAI, Google, Pushover, etc.
- Gradio themes typically use `gr.themes.Default(primary_hue="sky")`
- `load_dotenv(override=True)` pattern for environment loading