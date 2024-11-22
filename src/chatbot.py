import os
import re
from dotenv import load_dotenv
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("API_KEY")

# Initialize the ChatOpenAI instance
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    base_url="https://api.avalai.ir/v1",
    api_key=api_key,
    max_tokens=1000,
    n=1,
    stop=None,
    temperature=0.7
)
