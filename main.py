from fastapi import FastAPI, HTTPException
import httpx
import json
from urllib.parse import quote
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()


origins = [
    "http://localhost:5173",  
    "http://127.0.0.1:5173", 
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_API_KEY = "sk-proj-..."
OPENAI_BASE_URL = "https://api.openai.com/v1/realtime"  # Check OpenAI docs
MODEL = "gpt-4o-mini-realtime-preview-2024-12-17"

class SDPRequest(BaseModel):
    sdp_offer: str

@app.post("/start-call")
async def start_call(request: SDPRequest):
    sdp_offer = request.sdp_offer
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="Missing OpenAI API key")

    # OpenAI API might not support direct SDP input
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": "Real-time voice assistant is initializing..."}],
        "stream": False  # Ensure API supports streaming if needed
    }

    url = f"{OPENAI_BASE_URL}"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"OpenAI API Error: {response.text}"
            )

    return {"sdp_answer": response.text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
