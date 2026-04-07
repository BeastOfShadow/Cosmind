import sys
try:
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat
    from pydantic import BaseModel, Field
    print("Agno loaded successfully!")
except Exception as e:
    print(f"Error loading Agno: {e}")
