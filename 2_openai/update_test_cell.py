#!/usr/bin/env python3
import json

with open('2_openai/2_lab2_with_replies.ipynb', 'r') as f:
    nb = json.load(f)

# Find and update the test cell
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if 'test_reply' in source and ('test.customer@example.com' in source or 'johnny.jarecsni' in source):
            print(f'Updating test cell {i}...')
            cell['source'] = [
                "# Test with a manual reply - sends to YOUR email so you can see it!\n",
                "test_reply = {\n",
                "    \"from\": \"johnny.jarecsni@icloud.com\",\n",
                "    \"subject\": \"Re: Transform Your Business with ComplAI\",\n",
                "    \"body\": \"Hi, this sounds interesting! Can you tell me more about pricing and how long implementation typically takes?\"\n",
                "}\n",
                "\n",
                "print(\"📧 Test Scenario:\")\n",
                "print(f\"  Simulating reply from: {test_reply['from']}\")\n",
                "print(f\"  Subject: {test_reply['subject']}\")\n",
                "print(f\"  Message: {test_reply['body']}\")\n",
                "print(f\"\\n🤖 The agent will:\")\n",
                "print(\"  1. Analyze the sentiment (likely INTERESTED or QUESTION)\")\n",
                "print(\"  2. Generate an appropriate response\")\n",
                "print(f\"  3. Send reply email to: {test_reply['from']}\")\n",
                "print(f\"\\n💡 You'll receive the reply at {test_reply['from']}!\\n\")\n",
                "\n",
                "# Uncomment to test:\n",
                "# await process_reply(test_reply['from'], test_reply['subject'], test_reply['body'])\n",
                "\n",
                "print(\"✅ Test ready - uncomment the line above to run\")"
            ]
            break

with open('2_openai/2_lab2_with_replies.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print('✅ Test cell updated with your email!')
