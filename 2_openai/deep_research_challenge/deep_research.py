import gradio as gr
from dotenv import load_dotenv
from research_coordinator import ResearchCoordinator
from config import ResearchConfig
from logging_config import setup_logging
import os

load_dotenv(override=True)

# Setup logging
setup_logging(
    log_level=os.getenv('LOG_LEVEL', 'INFO'),
    log_to_file=True
)

# Create coordinator
config = ResearchConfig.from_env()
coordinator = ResearchCoordinator(config)


async def run_autonomous_research(query: str, mode: str):
    """Run autonomous research with selected mode."""
    # Set budget based on mode
    if mode == "Development (Fast, Limited)":
        from budget import ResearchBudget
        budget = ResearchBudget.create_development()
    elif mode == "Production (Full, Expensive)":
        from budget import ResearchBudget
        budget = ResearchBudget.create_production()
    else:  # Default
        budget = None
    
    async for update in coordinator.conduct_research(query, budget):
        yield update


with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# Autonomous Deep Research")
    gr.Markdown("""
    Enhanced research system with:
    - Autonomous trail following
    - Quality evaluation
    - Multi-agent collaboration
    - Budget management
    """)
    
    with gr.Row():
        query_textbox = gr.Textbox(
            label="What topic would you like to research?",
            placeholder="Enter your research query...",
            scale=3
        )
        mode_dropdown = gr.Dropdown(
            choices=[
                "Default (Balanced)",
                "Development (Fast, Limited)",
                "Production (Full, Expensive)"
            ],
            value="Default (Balanced)",
            label="Research Mode",
            scale=1
        )
    
    run_button = gr.Button("Start Research", variant="primary", size="lg")
    
    with gr.Tabs():
        with gr.Tab("Report"):
            report = gr.Markdown(label="Research Report")
        
        with gr.Tab("Status"):
            status = gr.Markdown(label="Research Status")
    
    run_button.click(
        fn=run_autonomous_research,
        inputs=[query_textbox, mode_dropdown],
        outputs=report
    )
    
    query_textbox.submit(
        fn=run_autonomous_research,
        inputs=[query_textbox, mode_dropdown],
        outputs=report
    )

ui.launch(inbrowser=True)

