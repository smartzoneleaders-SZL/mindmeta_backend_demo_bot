from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import httpx
from urllib.parse import quote
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# For schemas of endpoints
from schema.call_bot import SDPRequest, RequestData, CallYourBot

# for the prompt that we will give the model
from services.preparing_prompt import prepare_prompt

# To get time of scheduled call
from services.before_call_start import get_time_of_call

# to check and inform about user suicidal behaviour
from services.after_call_ends import check_chat_for_possible_word

# To get bot voice
from services.before_call_start import get_voice_of_bot

# For websocket and deepgram
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uuid
import asyncio

# For routers
from routes import analytics, auth, allow_access, call_bot, cold_call


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
    try:
        sdp_offer = request.sdp_offer
        patient_id = request.patient_id
        if not OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="Missing OpenAI API key")
        time_of_call = get_time_of_call(request.schedule_id)
        instructions = prepare_prompt(patient_id)
        voice_option = get_voice_of_bot(patient_id)

    # Build the URL with model and instructions passed as query parameters.
    # Use urllib.parse.quote to ensure proper URL-encoding of the instructions.
        query_params = (
                f"?model={os.getenv('MODEL')}"
                f"&instructions={quote(instructions)}"
                f"&voice={quote(voice_option)}"
                f"&cache=true"         # Enable caching
                # f"&cache_level=1"    # Optionally set cache level (if supported)
            )
        base_url = os.getenv('OPENAI_BASE_URL')
        url = f"{base_url}{query_params}"
        headers = {
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/sdp",}

        async with httpx.AsyncClient() as client:
            # Send the SDP offer along with the query parameters.
            response = await client.post(url, headers=headers, data=sdp_offer)
            if response.status_code == 200 or response.status_code == 201:
                print("sdp data is: ",response.text)
                return JSONResponse(
                        status_code=response.status_code,
                        content={"sdp_answer": response.text, "time": time_of_call}
                    )
            else:
                return JSONResponse(status_code=500, content={"detail":"An Error occured"})
    except Exception as e:
        print("Error as: ", str(e))
        raise

# For generating uuid 
from utils.utils import generate_uuid

# for uploading chat
# for changing the status
from services.after_call_ends import upload_chat_hisory, change_call_status_to_completed

@app.post("/call-with-bot-end")
def upload_call_data_on_mongodb(request :RequestData):
    try:
        patient_id= request.patient_id
        # call_id = generate_uuid()
        # messages = "Hello my name is Sarab. my childern don't come here to visit me my wife died i should join her"
        # is_done = check_chat_for_possible_word(messages,patient_id)
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


from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        patient_id = await asyncio.wait_for(websocket.receive_text(), timeout=2.0)
        print(f"Received patient_id: {patient_id}")
    except asyncio.TimeoutError:
        await websocket.send_text("Error: Patient ID not received within 3 seconds")
        await websocket.close()
        return

    total_chat = ""
    new_chat_id = uuid.uuid1()
    deepgram_client: DeepgramClient = DeepgramClient(api_key=os.getenv('DEEPGRAM_API'))
    dg_connection = deepgram_client.listen.websocket.v("1")

    def on_open(self, open, **kwargs):
        print(f"Deepgram connection opened: {open}")

    def on_message(self, result, **kwargs):
        nonlocal total_chat
        if result.is_final:
            transcript = result.channel.alternatives[0].transcript.strip()
            print(f"Final Transcription: {transcript}")
            total_chat += transcript + " "

    def on_error(self, error, **kwargs):
        print(f"Deepgram error: {error}")

    def on_close(self, close, **kwargs):
        print(f"Deepgram connection closed: {close}")

    dg_connection.on(LiveTranscriptionEvents.Open, on_open)
    dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
    dg_connection.on(LiveTranscriptionEvents.Error, on_error)
    dg_connection.on(LiveTranscriptionEvents.Close, on_close)

    options: LiveOptions = LiveOptions(
        model="nova-3",
        language="en-US",
        smart_format=True,
        interim_results=True,
        utterance_end_ms="4000",
        vad_events=True,
        endpointing=300
    )

    if not dg_connection.start(options):
        await websocket.close()
        return

    try:
        while True:
            data = await websocket.receive_bytes()
            dg_connection.send(data)
    except WebSocketDisconnect:
        await upload_chat_hisory(patient_id, new_chat_id, total_chat)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # dg_connection.finish()
        try:
            await websocket.close()
        except RuntimeError:
            print("WebSocket already closed.")

# voice_option = "sage"


# "alloy"
# "ash"
# "ballad"
# "coral"
# "echo"
# "sage"
# "shimmer"
# "verse"





app.include_router(auth.router, prefix="/api/auth", tags=["AUTH"])
app.include_router(allow_access.router, prefix="/api/allow-access", tags=["Allow Access"])
app.include_router(call_bot.router, prefix="/api/call_bot", tags=["Call_bot"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(cold_call.router, prefix="/api/cold-call", tags=["Cold Call Script"])




if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
