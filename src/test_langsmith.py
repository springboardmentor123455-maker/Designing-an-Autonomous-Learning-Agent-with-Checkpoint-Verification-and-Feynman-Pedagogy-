import os
from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()

@traceable(name="LangSmith Connectivity Test")
def test_function():
    return "LangSmith is working!"

if __name__ == "__main__":
    print(test_function())
