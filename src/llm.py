import httpx
from fastapi import HTTPException

async def generate_text(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=200.0) as client:
        try:
            response = await client.post(
                "http://localhost:8080/api/generate",
                json={"prompt": prompt},
            )
            response.raise_for_status()
            result = response.json()["generated_text"]
            return result.split('}\\n\\n\\n{')[0].rstrip('"\n')  # Clean the response
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="LLM service timeout")
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"LLM service error: {str(e)}")