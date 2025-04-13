from fastapi import FastAPI
from src.endpoints import router as api_router
from src.endpoints.event import router as event_router
from src.llm import generate_text
from pydantic import BaseModel
from src.endpoints.game import router as game_router


class PromptRequest(BaseModel):
    prompt: str

app = FastAPI()

app.include_router(api_router, prefix="/api")
app.include_router(event_router, prefix="/api/event")
app.include_router(game_router, prefix="/api/game")

@app.post("/api/generate-text")
async def generate(prompt: PromptRequest):
    response = await generate_text(prompt.prompt)
    return {"generated_text": response}