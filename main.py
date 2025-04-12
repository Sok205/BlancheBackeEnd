from fastapi import FastAPI
from src.endpoints import router as api_router
from src.endpoints.event import router as event_router

app = FastAPI()

app.include_router(api_router, prefix="/api")
app.include_router(event_router, prefix="/api/event")

@app.get("/")
async def root():
    return {"message": "Hello World"}
