from fastapi import FastAPI, HTTPException
import httpx
import json
from urllib.parse import quote
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# For schemas of endpoints
from schema.call_bot import SDPRequest, RequestData

# for the prompt that we will give the model
from services.preparing_prompt import prepare_prompt

import os
from dotenv import load_dotenv

# For loading Pete's dummy data 
# from db.dummy_data import instructions

load_dotenv()

app = FastAPI()


# origins = [
#     "http://localhost:5173",  
#     "http://127.0.0.1:5173", 
# ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_BASE_URL = "https://api.openai.com/v1/realtime"
MODEL = "gpt-4o-mini-realtime-preview-2024-12-17"


@app.get("/health-check")
def health_check():
    try:
        return {"status": "Good"}
    except Exception as e:
        return {"status": "Bad"}


@app.post("/start-call")
async def start_call(request: SDPRequest):
    sdp_offer = request.sdp_offer
    instructions =request.prompt
    # print("User prompt is: ",instructions)
    # patient_id = request.patient_id
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="Missing OpenAI API key")
    # print("Patient_id is: ",patient_id)
    # instructions = prepare_prompt(patient_id)
    # Build the URL with model and instructions passed as query parameters.
    # Use urllib.parse.quote to ensure proper URL-encoding of the instructions.
    query_params = f"?model={MODEL}&instructions={quote(instructions)}"
    url = f"{OPENAI_BASE_URL}{query_params}"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/sdp",  
    }

    async with httpx.AsyncClient() as client:
        # Send the SDP offer along with the query parameters.
        response = await client.post(url, headers=headers, data=sdp_offer)
        # print("Print repponse is: ",response.text)
        # print("Print response status: ",response.status_code)
        if response.status_code != 200 or response.status_code != 201:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )

    return {"sdp_answer": response.text}

# For generating uuid 
from utils.utils import generate_uuid

# for uploading chat
# for changing the status
from services.after_call_ends import upload_chat_hisory, change_call_status_to_completed

@app.post("/call-with-bot-end")
def upload_call_data_on_mongodb(request :RequestData):
    try:
        patient_id= request.patient_id
        call_id = generate_uuid()
        messages = ["Hi i am Sarab", "Hello sarab, how are you today", "I am not feeling very good", "whats the problem sarab", "i am feeling very lonely" ]

        # Now because the call has ended, we need to change the status from 'schedule' to 'completed'
        did_change = change_call_status_to_completed(patient_id)
        if did_change:
            return {"sucess": True, "details": " "}
        
        # did_upload = upload_chat_hisory(patient_id , call_id, messages)
        # if did_upload and did_change:
        #     return {"sucess":True, "details": "chat history upload and schedule call status changed"}
        # else:
        #     return {"sucess": False, "details": " "}
    except Exception as e:
        print("Error in call_with_bot_end in main.py -> ",str(e))
        raise



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
