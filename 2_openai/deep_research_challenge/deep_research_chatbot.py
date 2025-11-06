import gradio as gr
from dotenv import load_dotenv
from research_coordinator import ResearchCoordinator
from config import ResearchConfig
from budget import ResearchBudget
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


async def chat_interface(message, history, mode):
    """Handle chat messages with clarification support."""
    
    # Parse mode to get budget
    if "Development" in mode:
        budget = ResearchBudget.create_development()
    elif "Production" in mode:
        budget = ResearchBudget.create_production()
    else:
        budget = ResearchBudget.create_default()
    
    # Check if this is first message - history should only have user messages, no bot responses yet
    # Count messages that have bot responses (second element is not None)
    messages_with_responses = sum(1 for h in history if h[1] is not None)
    is_first_message = messages_with_responses == 0
    
    if is_first_message:
        # Check if clarification needed
        ambiguity_score, questions = await coordinator.clarification_engine.analyze_query(message)
        
        if questions and len(questions) > 0:
            # Format questions
            response = "I'd like to clarify a few things before starting the research:\n\n"
            for i, q in enumerate(questions, 1):
                response += f"**{i}.** {q.question}\n\n"
            response += "Please answer these questions to help me focus the research."
            
            return response
        else:
            # No clarification needed, start research
            response = "Starting research...\n\n"
            async for update in coordinator.conduct_research(message, budget):
                response = update  # Keep updating with latest
            return response
    else:
        # This is a clarification response - just start research with original query
        # In a full implementation, we'd parse the answers and enhance the query
        original_query = history[0][0] if history else message
        
        response = f"Thanks for the clarification! Starting research on: {original_query}\n\n"
        async for update in coordinator.conduct_research(original_query, budget):
            response = update
        return response


# Create Gradio Chatbot UI
with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# 🔬 Autonomous Deep Research")
    gr.Markdown("""
    Ask me to research any topic. I'll ask clarifying questions if needed, then conduct autonomous research.
    """)
    
    mode_dropdown = gr.Dropdown(
        choices=[
            "Development (Fast, Limited) - ~$0.10-0.30",
            "Default (Balanced) - ~$0.50-1.50",
            "Production (Full, Expensive) - ~$2-6"
        ],
        value="Development (Fast, Limited) - ~$0.10-0.30",
        label="Research Mode"
    )
    
    chatbot = gr.Chatbot(
        label="Research Assistant",
        height=500,
        type="tuples"
    )
    
    with gr.Row():
        msg = gr.Textbox(
            label="Your message",
            placeholder="What would you like to research?",
            scale=4,
            lines=2
        )
        submit = gr.Button("Submit", variant="primary", scale=1)
    
    clear = gr.Button("New Research Session")
    
    async def respond(message, chat_history, mode):
        if not message.strip():
            yield chat_history, ""
            return
        
        # Add user message immediately
        chat_history = chat_history + [[message, "Processing..."]]
        yield chat_history, ""
        
        # Get bot response
        bot_message = await chat_interface(message, chat_history[:-1], mode)
        
        # Update with final response
        chat_history[-1][1] = bot_message
        yield chat_history, ""
    
    submit.click(respond, [msg, chatbot, mode_dropdown], [chatbot, msg])
    msg.submit(respond, [msg, chatbot, mode_dropdown], [chatbot, msg])
    
    clear.click(lambda: ([], ""), None, [chatbot, msg])

ui.launch(inbrowser=True)
