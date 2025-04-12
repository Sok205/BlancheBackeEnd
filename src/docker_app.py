from fastapi import FastAPI
from transformers import AutoTokenizer, AutoModelForCausalLM
from pydantic import BaseModel
import torch

class PromptRequest(BaseModel):
    prompt: str

app = FastAPI()

MODEL_ID = "phanerozoic/Tiny-Viking-1.1b-v0.1"
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID)

@app.post("/api/generate")
async def generate(request: PromptRequest):
    inputs = tokenizer(request.prompt, return_tensors="pt", padding=True)
    outputs = model.generate(**inputs, max_length=100)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"generated_text": response}