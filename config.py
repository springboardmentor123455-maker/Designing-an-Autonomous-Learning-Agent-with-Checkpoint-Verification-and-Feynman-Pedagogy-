import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
 
# Load environment variables from .env
load_dotenv()

# LLM: we use OpenAI chat model via LangChain
llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # or "llama-3.1-8b-instant" for cheaper/faster
    temperature=0.2,
) 

# Simple web search tool (no API key needed)
web_search = DuckDuckGoSearchRun()
