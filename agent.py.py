# agent.py
from pydantic_ai import Agent, OpenAIModel
import os
import logging
from file_tools import agent as file_tools_agent

logger = logging.getLogger(__name__)

def setup_agent():
    try:
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "your_openrouter_api_key")
        model = OpenAIModel(
            api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            model_name="openai/gpt-4-turbo"
        )
        agent = Agent(model=model)
        # Tools are already registered in file_tools.py
        logger.info("Agent initialized with OpenRouter")
        return agent
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise