from fastapi import FastAPI, HTTPException
import httpx
import uvicorn

from fastapi.middleware.cors import CORSMiddleware


from pydantic import BaseModel





app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


OPENAI_API_KEY = "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"
OPENAI_BASE_URL = "https://api.openai.com/v1/realtime"
MODEL = "gpt-4o-mini-realtime-preview-2024-12-17"



class SDPRequest(BaseModel):
    sdp_offer: str

@app.post("/start-call")
async def start_call(request: SDPRequest):
    sdp_offer = request.sdp_offer
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="Missing OpenAI API key")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/sdp",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{OPENAI_BASE_URL}?model={MODEL}", headers=headers, data=sdp_offer)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    print("sdp is: ",response)
    return {"sdp_answer": response.text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)