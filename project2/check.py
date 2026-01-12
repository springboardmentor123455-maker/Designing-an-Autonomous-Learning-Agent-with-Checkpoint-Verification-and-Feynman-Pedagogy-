import os
from dotenv import load_dotenv

load_dotenv()

print("LANGCHAIN_API_KEY:", os.getenv("LANGCHAIN_API_KEY"))
print("LANGSMITH_API_KEY:", os.getenv("LANGSMITH_API_KEY"))
print("LANGCHAIN_TRACING_V2:", os.getenv("LANGCHAIN_TRACING_V2"))
print("LANGCHAIN_PROJECT:", os.getenv("LANGCHAIN_PROJECT"))