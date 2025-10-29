#!/usr/bin/env python3
"""
Jupyter Notebook Extension Tool

A reusable utility for safely adding cells to Jupyter notebooks.
Handles JSON structure properly to avoid breaking notebooks.

Usage:
    python notebook_extender.py <source_notebook> <output_notebook> [--cells cells.json]
    
Or import as module:
    from notebook_extender import extend_notebook, create_code_cell, create_markdown_cell
"""

import json
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional


def create_code_cell(source: str, execution_count: Optional[int] = None) -> Dict[str, Any]:
    """
    Create a properly formatted code cell.
    
    Args:
        source: Python code as string or list of strings
        execution_count: Optional execution count (None for unexecuted)
    
    Returns:
        Dictionary representing a Jupyter code cell
    """
    if isinstance(source, str):
        source = source.split('\n')
    
    # Ensure each line ends with \n except the last
    source = [line + '\n' if i < len(source) - 1 else line 
              for i, line in enumerate(source)]
    
    return {
        "cell_type": "code",
        "execution_count": execution_count,
        "metadata": {},
        "outputs": [],
        "source": source
    }


def create_markdown_cell(source: str) -> Dict[str, Any]:
    """
    Create a properly formatted markdown cell.
    
    Args:
        source: Markdown text as string or list of strings
    
    Returns:
        Dictionary representing a Jupyter markdown cell
    """
    if isinstance(source, str):
        source = source.split('\n')
    
    # Ensure each line ends with \n except the last
    source = [line + '\n' if i < len(source) - 1 else line 
              for i, line in enumerate(source)]
    
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source
    }


def extend_notebook(
    source_path: str,
    output_path: str,
    new_cells: List[Dict[str, Any]],
    validate: bool = True
) -> Dict[str, Any]:
    """
    Extend a Jupyter notebook by adding new cells.
    
    Args:
        source_path: Path to source notebook
        output_path: Path to output notebook
        new_cells: List of cell dictionaries to add
        validate: Whether to validate the notebook structure
    
    Returns:
        The modified notebook dictionary
    
    Raises:
        FileNotFoundError: If source notebook doesn't exist
        json.JSONDecodeError: If source notebook is invalid JSON
        ValueError: If notebook structure is invalid
    """
    # Read source notebook
    source_path = Path(source_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Source notebook not found: {source_path}")
    
    with open(source_path, 'r') as f:
        notebook = json.load(f)
    
    # Validate structure
    if validate:
        if 'cells' not in notebook:
            raise ValueError("Invalid notebook: missing 'cells' key")
        if 'metadata' not in notebook:
            raise ValueError("Invalid notebook: missing 'metadata' key")
        if 'nbformat' not in notebook:
            raise ValueError("Invalid notebook: missing 'nbformat' key")
    
    # Add new cells
    original_count = len(notebook['cells'])
    notebook['cells'].extend(new_cells)
    
    # Write output notebook
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(notebook, f, indent=1)
    
    print(f"✅ Successfully created {output_path}")
    print(f"   Original cells: {original_count}")
    print(f"   Added cells: {len(new_cells)}")
    print(f"   Total cells: {len(notebook['cells'])}")
    
    return notebook


def load_cells_from_json(cells_file: str) -> List[Dict[str, Any]]:
    """
    Load cell definitions from a JSON file.
    
    Args:
        cells_file: Path to JSON file containing cell definitions
    
    Returns:
        List of cell dictionaries
    """
    with open(cells_file, 'r') as f:
        return json.load(f)


def create_reply_notebook():
    """Original function - creates the email reply notebook."""
    # Read the original notebook
    with open('2_openai/2_lab2.ipynb', 'r') as f:
        notebook = json.load(f)
    
    # New cells to add for email reply functionality
    new_cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "\n",
                "# Part 4: Email Reply Capability 🎯\n",
                "\n",
                "## HARD CHALLENGE SOLUTION!\n",
                "\n",
                "This section implements automatic email reply handling using IMAP polling.\n",
                "\n",
                "### How it works:\n",
                "1. **Polls your inbox** every 60 seconds for new replies\n",
                "2. **Analyzes sentiment** (interested/objection/question/not interested)\n",
                "3. **Routes to specialized agents** based on reply type\n",
                "4. **Sends intelligent responses** automatically\n",
                "5. **Maintains conversation history** for context\n",
                "\n",
                "### Setup Required:\n",
                "See `EMAIL_REPLY_SETUP.md` for detailed instructions on getting your email app password."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Additional imports for email reply functionality\n",
                "import imaplib\n",
                "import email\n",
                "from email.header import decode_header\n",
                "import time\n",
                "import json\n",
                "from datetime import datetime\n",
                "from pathlib import Path\n",
                "\n",
                "# Email polling configuration - add these to your .env file\n",
                "IMAP_SERVER = os.environ.get('IMAP_SERVER', 'imap.gmail.com')\n",
                "IMAP_EMAIL = os.environ.get('IMAP_EMAIL', RECIPIENT_EMAIL)\n",
                "IMAP_PASSWORD = os.environ.get('IMAP_PASSWORD')\n",
                "\n",
                "# Create conversations directory\n",
                "Path(\"conversations\").mkdir(exist_ok=True)\n",
                "\n",
                "print(f\"📧 Email monitoring configured for: {IMAP_EMAIL}\")\n",
                "print(f\"🔐 Password set: {'✅ Yes' if IMAP_PASSWORD else '❌ No - add IMAP_PASSWORD to .env'}\")"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "@function_tool\n",
                "def store_conversation(email_address: str, direction: str, subject: str, body: str) -> Dict[str, str]:\n",
                "    \"\"\" Store email in conversation history for context \"\"\"\n",
                "    conversation = {\n",
                "        \"timestamp\": datetime.now().isoformat(),\n",
                "        \"direction\": direction,\n",
                "        \"subject\": subject,\n",
                "        \"body\": body\n",
                "    }\n",
                "    \n",
                "    filename = f\"conversations/{email_address.replace('@', '_at_').replace('<', '').replace('>', '')}.json\"\n",
                "    \n",
                "    conversations = []\n",
                "    if Path(filename).exists():\n",
                "        with open(filename, 'r') as f:\n",
                "            conversations = json.load(f)\n",
                "    \n",
                "    conversations.append(conversation)\n",
                "    \n",
                "    with open(filename, 'w') as f:\n",
                "        json.dump(conversations, f, indent=2)\n",
                "    \n",
                "    return {\"status\": \"stored\", \"count\": len(conversations)}\n",
                "\n",
                "\n",
                "@function_tool\n",
                "def get_conversation_history(email_address: str) -> str:\n",
                "    \"\"\" Retrieve previous emails exchanged with this prospect \"\"\"\n",
                "    filename = f\"conversations/{email_address.replace('@', '_at_').replace('<', '').replace('>', '')}.json\"\n",
                "    \n",
                "    if not Path(filename).exists():\n",
                "        return \"No previous conversation history found.\"\n",
                "    \n",
                "    with open(filename, 'r') as f:\n",
                "        conversations = json.load(f)\n",
                "    \n",
                "    history = []\n",
                "    for conv in conversations:\n",
                "        direction = \"We sent\" if conv[\"direction\"] == \"outbound\" else \"They replied\"\n",
                "        history.append(f\"{direction} ({conv['timestamp']}):\\nSubject: {conv['subject']}\\n{conv['body'][:200]}...\\n\")\n",
                "    \n",
                "    return \"\\n---\\n\".join(history)\n",
                "\n",
                "print(\"✅ Conversation storage tools created\")"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "def check_for_replies():\n",
                "    \"\"\"Poll email inbox for new replies using IMAP\"\"\"\n",
                "    if not IMAP_PASSWORD:\n",
                "        print(\"⚠️  IMAP_PASSWORD not set in .env file. Skipping email check.\")\n",
                "        return []\n",
                "    \n",
                "    try:\n",
                "        mail = imaplib.IMAP4_SSL(IMAP_SERVER)\n",
                "        mail.login(IMAP_EMAIL, IMAP_PASSWORD)\n",
                "        mail.select(\"inbox\")\n",
                "        \n",
                "        status, messages = mail.search(None, 'UNSEEN')\n",
                "        if status != 'OK':\n",
                "            return []\n",
                "        \n",
                "        replies = []\n",
                "        message_ids = messages[0].split()\n",
                "        \n",
                "        if message_ids:\n",
                "            print(f\"📬 Found {len(message_ids)} unread email(s)\")\n",
                "        \n",
                "        for num in message_ids:\n",
                "            status, msg_data = mail.fetch(num, '(RFC822)')\n",
                "            if status != 'OK':\n",
                "                continue\n",
                "                \n",
                "            msg = email.message_from_bytes(msg_data[0][1])\n",
                "            \n",
                "            subject = msg[\"subject\"]\n",
                "            if subject:\n",
                "                decoded = decode_header(subject)[0]\n",
                "                if isinstance(decoded[0], bytes):\n",
                "                    subject = decoded[0].decode(decoded[1] or 'utf-8')\n",
                "            \n",
                "            from_email = msg[\"from\"]\n",
                "            \n",
                "            body = \"\"\n",
                "            if msg.is_multipart():\n",
                "                for part in msg.walk():\n",
                "                    if part.get_content_type() == \"text/plain\":\n",
                "                        try:\n",
                "                            body = part.get_payload(decode=True).decode()\n",
                "                            break\n",
                "                        except:\n",
                "                            pass\n",
                "            else:\n",
                "                try:\n",
                "                    body = msg.get_payload(decode=True).decode()\n",
                "                except:\n",
                "                    body = str(msg.get_payload())\n",
                "            \n",
                "            replies.append({\n",
                "                \"from\": from_email,\n",
                "                \"subject\": subject or \"(no subject)\",\n",
                "                \"body\": body[:1000]\n",
                "            })\n",
                "        \n",
                "        mail.close()\n",
                "        mail.logout()\n",
                "        return replies\n",
                "        \n",
                "    except Exception as e:\n",
                "        print(f\"❌ Error checking emails: {e}\")\n",
                "        return []\n",
                "\n",
                "print(\"✅ Email polling function created\")"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "reply_analyzer = Agent(\n",
                "    name=\"Reply Analyzer\",\n",
                "    instructions=\"\"\"You analyze customer replies to sales emails.\n",
                "    \n",
                "    Determine the sentiment and intent from these categories:\n",
                "    - INTERESTED: Customer wants demo, call, more info, or shows positive interest\n",
                "    - NOT_INTERESTED: Polite decline, not a fit, already have solution\n",
                "    - OBJECTION: Has concerns about price, features, timing, or implementation\n",
                "    - QUESTION: Needs clarification about product, pricing, or process\n",
                "    - OUT_OF_OFFICE: Automated out-of-office reply\n",
                "    \n",
                "    Respond with ONLY the category name and a brief 1-sentence explanation.\n",
                "    Example: \"INTERESTED - Customer asked about scheduling a demo next week\"\n",
                "    \"\"\",\n",
                "    model=\"gpt-4o-mini\"\n",
                ")\n",
                "\n",
                "print(\"✅ Reply analyzer agent created\")"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "interested_responder = Agent(\n",
                "    name=\"Interested Responder\",\n",
                "    instructions=\"\"\"You write enthusiastic follow-up emails for interested prospects.\n",
                "    - Express excitement about their interest\n",
                "    - Offer specific next steps (calendar link, demo, call)\n",
                "    - Keep the tone matching the original email style\n",
                "    - Include 2-3 bullet points about what they'll learn/gain\n",
                "    - End with clear call-to-action\n",
                "    Sign off as 'The ComplAI Team'\n",
                "    \"\"\",\n",
                "    model=\"gpt-4o-mini\"\n",
                ")\n",
                "\n",
                "objection_handler = Agent(\n",
                "    name=\"Objection Handler\",\n",
                "    instructions=\"\"\"You address customer concerns about ComplAI with empathy and solutions.\n",
                "    - Acknowledge their concern specifically\n",
                "    - Provide concrete solutions or alternatives\n",
                "    - Include relevant proof points\n",
                "    - Offer to discuss their specific situation\n",
                "    - Keep tone helpful, not pushy\n",
                "    Sign off as 'The ComplAI Team'\n",
                "    \"\"\",\n",
                "    model=\"gpt-4o-mini\"\n",
                ")\n",
                "\n",
                "question_answerer = Agent(\n",
                "    name=\"Question Answerer\",\n",
                "    instructions=\"\"\"You answer questions about ComplAI clearly and helpfully.\n",
                "    - Answer the specific question directly\n",
                "    - Provide relevant details without overwhelming\n",
                "    - Offer to schedule a call for complex questions\n",
                "    - Suggest related features they might find useful\n",
                "    Sign off as 'The ComplAI Team'\n",
                "    \"\"\",\n",
                "    model=\"gpt-4o-mini\"\n",
                ")\n",
                "\n",
                "not_interested_handler = Agent(\n",
                "    name=\"Not Interested Handler\",\n",
                "    instructions=\"\"\"You write graceful responses to prospects who aren't interested.\n",
                "    - Thank them for their time\n",
                "    - Keep it brief (2-3 sentences)\n",
                "    - Offer to stay in touch for future needs\n",
                "    - Leave door open professionally\n",
                "    Sign off as 'The ComplAI Team'\n",
                "    \"\"\",\n",
                "    model=\"gpt-4o-mini\"\n",
                ")\n",
                "\n",
                "print(\"✅ All reply writer agents created\")"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "@function_tool\n",
                "def send_reply_email(to_email: str, subject: str, body: str) -> Dict[str, str]:\n",
                "    \"\"\" Send a reply email maintaining the conversation thread \"\"\"\n",
                "    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))\n",
                "    from_email = Email(SENDER_EMAIL)\n",
                "    to = To(to_email)\n",
                "    \n",
                "    if not subject.startswith(\"Re:\"):\n",
                "        subject = f\"Re: {subject}\"\n",
                "    \n",
                "    content = Content(\"text/plain\", body)\n",
                "    mail = Mail(from_email, to, subject, content).get()\n",
                "    \n",
                "    try:\n",
                "        response = sg.client.mail.send.post(request_body=mail)\n",
                "        store_conversation(to_email, \"outbound\", subject, body)\n",
                "        return {\"status\": \"sent\", \"code\": response.status_code}\n",
                "    except Exception as e:\n",
                "        return {\"status\": \"error\", \"message\": str(e)}\n",
                "\n",
                "print(\"✅ Reply sending function created\")"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "conversation_manager = Agent(\n",
                "    name=\"Conversation Manager\",\n",
                "    instructions=\"\"\"You manage ongoing email conversations with prospects.\n",
                "    \n",
                "    Follow these steps:\n",
                "    1. Use get_conversation_history to understand the context\n",
                "    2. Analyze the reply to determine intent\n",
                "    3. Choose the appropriate responder agent based on intent\n",
                "    4. Generate a response that references their specific points\n",
                "    5. Send the reply using send_reply_email\n",
                "    \n",
                "    Be natural and helpful. Don't be pushy or robotic.\n",
                "    \"\"\",\n",
                "    tools=[\n",
                "        get_conversation_history,\n",
                "        reply_analyzer.as_tool(\"analyze_reply\", \"Analyze customer reply sentiment and intent\"),\n",
                "        interested_responder.as_tool(\"respond_interested\", \"Write response for interested prospect\"),\n",
                "        objection_handler.as_tool(\"handle_objection\", \"Address customer concerns\"),\n",
                "        question_answerer.as_tool(\"answer_question\", \"Answer customer questions\"),\n",
                "        not_interested_handler.as_tool(\"respond_not_interested\", \"Gracefully handle not interested\"),\n",
                "        send_reply_email\n",
                "    ],\n",
                "    model=\"gpt-4o-mini\"\n",
                ")\n",
                "\n",
                "print(\"✅ Conversation manager agent created\")"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "async def process_reply(from_email: str, subject: str, body: str):\n",
                "    \"\"\"Process an incoming email reply through the agent system\"\"\"\n",
                "    print(f\"\\n{'='*60}\")\n",
                "    print(f\"📧 Processing reply from: {from_email}\")\n",
                "    print(f\"📋 Subject: {subject}\")\n",
                "    print(f\"{'='*60}\\n\")\n",
                "    \n",
                "    store_conversation(from_email, \"inbound\", subject, body)\n",
                "    \n",
                "    context = f\"\"\"Customer Email: {from_email}\n",
                "Subject: {subject}\n",
                "\n",
                "Their Message:\n",
                "{body}\n",
                "\n",
                "Please analyze this reply and send an appropriate response.\"\"\"\n",
                "    \n",
                "    try:\n",
                "        with trace(f\"Reply to {from_email}\"):\n",
                "            result = await Runner.run(conversation_manager, context)\n",
                "        print(f\"\\n✅ Response sent successfully!\")\n",
                "        print(f\"Agent output: {result.final_output[:200]}...\")\n",
                "    except Exception as e:\n",
                "        print(f\"\\n❌ Error processing reply: {e}\")\n",
                "\n",
                "print(\"✅ Reply processing function created\")"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "async def monitor_emails(check_interval=60, max_iterations=None):\n",
                "    \"\"\"Monitor inbox for new replies and process them automatically\"\"\"\n",
                "    print(\"🚀 Starting email reply monitoring...\")\n",
                "    print(f\"📬 Checking {IMAP_EMAIL} every {check_interval} seconds\")\n",
                "    print(f\"⏹️  Press Ctrl+C to stop\\n\")\n",
                "    \n",
                "    iteration = 0\n",
                "    \n",
                "    try:\n",
                "        while True:\n",
                "            iteration += 1\n",
                "            if max_iterations and iteration > max_iterations:\n",
                "                print(f\"\\n🏁 Reached max iterations ({max_iterations})\")\n",
                "                break\n",
                "            \n",
                "            print(f\"\\n[{datetime.now().strftime('%H:%M:%S')}] Checking for new emails... (iteration {iteration})\")\n",
                "            replies = check_for_replies()\n",
                "            \n",
                "            if replies:\n",
                "                print(f\"\\n🎯 Processing {len(replies)} new reply(ies)...\")\n",
                "                for reply in replies:\n",
                "                    await process_reply(reply['from'], reply['subject'], reply['body'])\n",
                "                    await asyncio.sleep(2)\n",
                "            else:\n",
                "                print(\"   No new replies\")\n",
                "            \n",
                "            if max_iterations is None or iteration < max_iterations:\n",
                "                print(f\"   Sleeping for {check_interval} seconds...\")\n",
                "                await asyncio.sleep(check_interval)\n",
                "    except KeyboardInterrupt:\n",
                "        print(\"\\n\\n⏹️  Monitoring stopped by user\")\n",
                "    except Exception as e:\n",
                "        print(f\"\\n\\n❌ Error in monitoring loop: {e}\")\n",
                "\n",
                "print(\"✅ Email monitoring loop created\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Test with Manual Reply\n",
                "\n",
                "Before starting the monitoring loop, test with a manual reply:"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Test with a manual reply\n",
                "test_reply = {\n",
                "    \"from\": \"test.customer@example.com\",\n",
                "    \"subject\": \"Re: Transform Your Business with ComplAI\",\n",
                "    \"body\": \"Hi, this sounds interesting! Can you tell me more about pricing and implementation?\"\n",
                "}\n",
                "\n",
                "# Uncomment to test:\n",
                "# await process_reply(test_reply['from'], test_reply['subject'], test_reply['body'])\n",
                "\n",
                "print(\"✅ Test reply ready - uncomment the line above to test\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Start Email Monitoring\n",
                "\n",
                "**For testing:** Use `max_iterations=5` to limit checks  \n",
                "**For production:** Remove `max_iterations` to run indefinitely"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Start monitoring - this will check for emails every 30 seconds, 5 times\n",
                "await monitor_emails(check_interval=30, max_iterations=5)\n",
                "\n",
                "# For production, run indefinitely:\n",
                "# await monitor_emails(check_interval=60)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 🎉 Congratulations!\n",
                "\n",
                "You've successfully implemented the HARD CHALLENGE!\n",
                "\n",
                "### What you've built:\n",
                "- ✅ IMAP email polling (no server required!)\n",
                "- ✅ Multi-agent reply system\n",
                "- ✅ Sentiment analysis and routing\n",
                "- ✅ Conversation history tracking\n",
                "- ✅ Intelligent response generation\n",
                "\n",
                "### Next steps:\n",
                "1. Check `conversations/` folder for stored email history\n",
                "2. View agent decisions at https://platform.openai.com/traces\n",
                "3. Send yourself a test email to see it in action\n",
                "4. Customize agent instructions to match your style\n",
                "\n",
                "Happy automating! 🚀"
            ]
        }
    ]
    
    # Add new cells to the notebook
    notebook['cells'].extend(new_cells)
    
    # Write the new notebook
    with open('2_openai/2_lab2_with_replies.ipynb', 'w') as f:
        json.dump(notebook, f, indent=1)
    
    print("✅ Successfully created 2_lab2_with_replies.ipynb")
    print(f"   Added {len(new_cells)} new cells")
    print(f"   Total cells: {len(notebook['cells'])}")

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extend Jupyter notebooks by adding cells safely",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create email reply notebook (original use case)
  python notebook_extender.py --create-reply-notebook
  
  # Extend any notebook with cells from JSON
  python notebook_extender.py source.ipynb output.ipynb --cells new_cells.json
  
  # Use as Python module
  from notebook_extender import extend_notebook, create_code_cell
  cells = [create_code_cell("print('Hello')")]
  extend_notebook("source.ipynb", "output.ipynb", cells)
        """
    )
    
    parser.add_argument(
        'source',
        nargs='?',
        help='Source notebook path'
    )
    parser.add_argument(
        'output',
        nargs='?',
        help='Output notebook path'
    )
    parser.add_argument(
        '--cells',
        help='JSON file containing cell definitions'
    )
    parser.add_argument(
        '--create-reply-notebook',
        action='store_true',
        help='Create the email reply notebook (original use case)'
    )
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip notebook structure validation'
    )
    
    args = parser.parse_args()
    
    try:
        if args.create_reply_notebook:
            # Original use case
            create_reply_notebook()
        elif args.source and args.output:
            # General use case
            if args.cells:
                new_cells = load_cells_from_json(args.cells)
            else:
                print("❌ Error: --cells required when using source/output mode")
                sys.exit(1)
            
            extend_notebook(
                args.source,
                args.output,
                new_cells,
                validate=not args.no_validate
            )
        else:
            parser.print_help()
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
