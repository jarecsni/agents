#!/usr/bin/env python3
"""
Fix the notebook by properly separating callable functions from tool wrappers
"""

import json

# Read the notebook
with open('2_openai/2_lab2_with_replies.ipynb', 'r') as f:
    notebook = json.load(f)

# Find and fix the conversation storage cell
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code' and any('@function_tool' in line for line in cell.get('source', [])):
        source = ''.join(cell['source'])
        
        # Fix the store_conversation cell
        if 'def store_conversation' in source:
            cell['source'] = [
                "# Conversation storage - regular functions first, then tool wrappers\n",
                "def _store_conversation_impl(email_address: str, direction: str, subject: str, body: str) -> Dict[str, str]:\n",
                "    \"\"\" Internal implementation for storing conversation \"\"\"\n",
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
                "def _get_conversation_history_impl(email_address: str) -> str:\n",
                "    \"\"\" Internal implementation for getting conversation history \"\"\"\n",
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
                "\n",
                "# Now create the tool wrappers\n",
                "@function_tool\n",
                "def store_conversation(email_address: str, direction: str, subject: str, body: str) -> Dict[str, str]:\n",
                "    \"\"\" Store email in conversation history for context \"\"\"\n",
                "    return _store_conversation_impl(email_address, direction, subject, body)\n",
                "\n",
                "\n",
                "@function_tool\n",
                "def get_conversation_history(email_address: str) -> str:\n",
                "    \"\"\" Retrieve previous emails exchanged with this prospect \"\"\"\n",
                "    return _get_conversation_history_impl(email_address)\n",
                "\n",
                "print(\"✅ Conversation storage tools created\")"
            ]
        
        # Fix the process_reply cell
        if 'async def process_reply' in source:
            cell['source'] = [
                "async def process_reply(from_email: str, subject: str, body: str):\n",
                "    \"\"\"Process an incoming email reply through the agent system\"\"\"\n",
                "    print(f\"\\n{'='*60}\")\n",
                "    print(f\"📧 Processing reply from: {from_email}\")\n",
                "    print(f\"📋 Subject: {subject}\")\n",
                "    print(f\"{'='*60}\\n\")\n",
                "    \n",
                "    # Use the implementation function directly (not the tool wrapper)\n",
                "    _store_conversation_impl(from_email, \"inbound\", subject, body)\n",
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
        
        # Fix send_reply_email
        if 'def send_reply_email' in source and '@function_tool' in source:
            cell['source'] = [
                "def _send_reply_email_impl(to_email: str, subject: str, body: str) -> Dict[str, str]:\n",
                "    \"\"\" Internal implementation for sending reply email \"\"\"\n",
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
                "        _store_conversation_impl(to_email, \"outbound\", subject, body)\n",
                "        return {\"status\": \"sent\", \"code\": response.status_code}\n",
                "    except Exception as e:\n",
                "        return {\"status\": \"error\", \"message\": str(e)}\n",
                "\n",
                "\n",
                "@function_tool\n",
                "def send_reply_email(to_email: str, subject: str, body: str) -> Dict[str, str]:\n",
                "    \"\"\" Send a reply email maintaining the conversation thread \"\"\"\n",
                "    return _send_reply_email_impl(to_email, subject, body)\n",
                "\n",
                "print(\"✅ Reply sending function created\")"
            ]

# Write the fixed notebook
with open('2_openai/2_lab2_with_replies.ipynb', 'w') as f:
    json.dump(notebook, f, indent=1)

print("✅ Fixed notebook saved!")
