# server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from agent import setup_agent

logger = logging.getLogger(__name__)

app = FastAPI()
agent = setup_agent()

class ChatRequest(BaseModel):
    messages: list[dict]
    model: str = "openai/gpt-4-turbo"

class ChatResponse(BaseModel):
    choices: list[dict]
    model: str

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    try:
        # Process messages with agent
        response = await agent.run(request.messages)
        choices = [{"message": {"content": response}}]
        return ChatResponse(choices=choices, model=request.model)
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))