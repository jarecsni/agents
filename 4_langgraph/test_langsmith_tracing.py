"""
Minimal LangSmith tracing test
Run this to verify LangSmith connection and tracing
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables from .env file
load_dotenv()

print("Environment variables loaded from .env:")
print(f"LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
print(f"LANGCHAIN_PROJECT: {os.getenv('LANGCHAIN_PROJECT')}")
print(f"LANGCHAIN_ENDPOINT: {os.getenv('LANGCHAIN_ENDPOINT')}")
print(f"LANGCHAIN_API_KEY: {os.getenv('LANGCHAIN_API_KEY')[:20] + '...' if os.getenv('LANGCHAIN_API_KEY') else 'NOT SET'}")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')[:20] + '...' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
print()

# Make a simple LLM call that should show up in LangSmith
print("Making LLM call...")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

try:
    response = llm.invoke("Say 'LangSmith tracing test successful' and nothing else.")
    print(f"Response: {response.content}")
    print()
    print("✅ Call completed successfully!")
    print("👉 Check your LangSmith dashboard at: https://smith.langchain.com/")
    print(f"👉 Project: {os.getenv('LANGCHAIN_PROJECT')}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
