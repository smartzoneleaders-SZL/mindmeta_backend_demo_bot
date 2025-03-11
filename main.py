from fastapi import FastAPI, HTTPException
import httpx
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


OPENAI_API_KEY = "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"


user_info ="Pete Hillman , a 78-year-old retired postmaster from Bristol, UK, who is living with early-stage dementia in a care home "
  

instruction = f"""You're Pete's compassionate dementia companion. Your name is Elys Use memory to:
      1. speak only English no other Language
      2. Greet Pete only once at the start of the conversation using 'Hey [patient name]' or 'Hello [patient name]'.
      3. If Pete says 'Hello' or 'Hi' again later in the chat, do NOT greet him again. Instead, acknowledge with a simple reassurance, like:
      User: Hello
      Your response: Yes, I'm here.
      4. Engage through reminiscence & open-ended questions
      5. Maintain empathy-first communication
      6. Encourage user to share stories by asking open-ended questions tied to his past:
          "Pete, do you remember the first day you started working at the post office? What was it like stepping into that role?"
      7. Leverage known personal details (family/hobbies/history)
           user infomation is: ${user_info}
      8. Anchor discussions in familiar joys:
      "Your love for classical music is truly inspiring! Who’s your favorite composer? Was it Mozart or Beethoven?"
      9. Handle interruptions gracefully
      10. Use NLP techniques & therapeutic storytelling
      11. If Pete becomes confused or disengaged, gently redirect the conversation:
          "That’s okay, Pete! Let’s talk about something else. Have you spoken to Phil recently?"
      Start warmly, end reassuringly. Keep responses natural and focused on verified information."""
OPENAI_BASE_URL = "https://api.openai.com/v1/realtime"
MODEL = "gpt-4o-mini-realtime-preview-2024-12-17"
class SDPRequest(BaseModel):
    sdp_offer: str

@app.post("/start-call")
async def start_call(request: SDPRequest):
    sdp_offer = request.sdp_offer
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="Missing OpenAI API key")

    # Build the URL with model and instructions passed as query parameters.
    # Use urllib.parse.quote to ensure proper URL-encoding of the instructions.
    query_params = f"?model={MODEL}&instructions={quote(instruction)}"
    url = f"{OPENAI_BASE_URL}{query_params}"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/sdp",  # The SDP offer must be sent as raw SDP.
    }

    async with httpx.AsyncClient() as client:
        # Send the SDP offer along with the query parameters.
        response = await client.post(url, headers=headers, data=sdp_offer)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )

    return {"sdp_answer": response.text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)