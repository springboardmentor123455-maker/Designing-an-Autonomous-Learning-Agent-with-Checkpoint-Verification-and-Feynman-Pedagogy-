import os

from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA

load_dotenv()

print(os.getenv("NVIDIA_API_KEY"))

model = ChatNVIDIA(
  # model="google/gemma-3-1b-it",
  # model="deepseek-ai/deepseek-v3.2",
  model="mistralai/mistral-7b-instruct-v0.2",
  api_key=os.getenv("NVIDIA_API_KEY"), 
  temperature=0.1,
  top_p=0.7,
)

model_1 = ChatNVIDIA(
  # model="google/gemma-3-1b-it",
  model="deepseek-ai/deepseek-v3.1",
#   model="mistralai/mistral-7b-instruct-v0.2",
  api_key=os.getenv("NVIDIA_API_KEY"), 
  temperature=0.1,
  top_p=0.7,
)