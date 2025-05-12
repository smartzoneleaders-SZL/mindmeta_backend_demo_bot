from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse


# For call websocket
from fastapi import WebSocket, WebSocketDisconnect


import json
from fastapi import WebSocket, WebSocketDisconnect
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions

import os
from dotenv import load_dotenv
from services.Langchain_service import chat_with_model, greet_user, invoke_model
import logging

# For extracting history
from services.after_call_ends import get_chat_hisory



# import uid for new chats
import uuid 



# For TTS (text to speech)
from utils.eleven_labs_utils import text_to_speech

# for sending intruptions
from utils.utils import send_interruption

# To check eligibility for if user has used the bot for more than 30 mins
from services.postgres import is_user_eligible_for_call

from db.dummy_data import PROMPTS

# import schema
from schema.call_bot import CallEndDemo

# For updating the time after the call
from services.postgres import update_time_of_call


# for db
from fastapi import Depends
from sqlalchemy.orm import Session
from db.postgres import get_db


import asyncio



router = APIRouter()

load_dotenv()

logger = logging.getLogger(__name__)




# Initialize Deepgram client
api_key = os.getenv("DEEPGRAM_API_KEY")
if not api_key:
    raise ValueError("Deepgram API Key is missing.")

# config = DeepgramClientOptions(
#             options={"keepalive": "true"}
#         )
deepgram_client = DeepgramClient(api_key)



@router.post("/call-with-bot-end")
def update_time(request :CallEndDemo, db: Session = Depends(get_db)):
    """Update the remaining time of the user to use the bot, as we ony allow 30 mins per user """
    try:
        did_change = update_time_of_call(db,request.email,request.time)
        if did_change:
            return {"sucess": True, "details": " "}
    except HTTPException as http_exc:
        return JSONResponse(content={"detail": http_exc.detail}, status_code=http_exc.status_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail="An Error has occured")



@router.websocket("/call-with-demo-bot")
async def call_with_bot(
    websocket: WebSocket,
    email: str = Query(...),
    prompt: str = Query(...),
    voice_id: str = Query(...),
):

    await websocket.accept()
    dg_connection = None 
    send_task = None 

    try:
        db_gen = get_db()
        db = next(db_gen)
        full_prompt = PROMPTS.get(prompt)
        user_eligibility, remaining_time = is_user_eligible_for_call(db, email)
        if user_eligibility == False:
            await websocket.send_text(json.dumps({"error": "Connection closed"}))
            await websocket.close()
            return

        await websocket.send_text(json.dumps({"remaining_time": remaining_time}))
        
        
        send_task = None
        new_chat_id = uuid.uuid1()

        dg_connection = deepgram_client.listen.websocket.v("1")

        message_queue = asyncio.Queue()

        audio = text_to_speech("Hello how are you doing", voice_id)
        
        # Send audio as base64 string in JSON
        message = json.dumps({"audio": audio, "complete": True})
        message_queue.put_nowait(message)
        
        
        loop = asyncio.get_event_loop()

        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if result.speech_final and sentence.strip():
                logger.info(f"Received sentence: {sentence}")
                asyncio.run_coroutine_threadsafe(send_interruption(websocket), loop)
                llm_response = invoke_model(sentence,new_chat_id,full_prompt)  
                logger.info(f"Model respose is: {llm_response}")
                audio = text_to_speech(llm_response, voice_id)
                logger.info("Sending audio to frontend")
                # Send audio as base64 string in JSON
                message = json.dumps({"audio": audio, "complete": True})
                message_queue.put_nowait(message)

                


        def on_error(self, error, **kwargs):
            logger.error(f"Deepgram error: {error}")

        def on_close(self, *args, **kwargs):  
            logger.info("Deepgram connection closed")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        dg_connection.on(LiveTranscriptionEvents.Close, on_close)

        options = LiveOptions(
            model="nova-3",
            smart_format=True,
            interim_results=True,
            language="en"
        )

        if dg_connection.start(options) is False:
            print("Failed to start connection")
            return
    

        async def send_messages():
            while True:
                message = await message_queue.get()
                await websocket.send_text(message)

        send_task = asyncio.create_task(send_messages())

        while True:
            try:

                data = await websocket.receive_bytes()

                dg_connection.send(data)
                
            except WebSocketDisconnect as e:
                logger.exception(f"Error on websocket is: {str(e)}")
                break

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        # Send the error message to the WebSocket client
        await websocket.send_text(json.dumps({"error": str(e)}))
        await websocket.close()
    finally:
        try:
            next(db_gen)  
        except StopIteration:
            pass
        if dg_connection is not None:
            dg_connection.finish()
        if send_task is not None:
            send_task.cancel()
    try:
        await websocket.close()
    except RuntimeError:
        logger.error("WebSocket already closed.")

