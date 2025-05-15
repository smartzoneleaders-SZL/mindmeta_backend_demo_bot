from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse


# For call websocket
from fastapi import WebSocket, WebSocketDisconnect


import json
from fastapi import WebSocket, WebSocketDisconnect, Query
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions

import os
from dotenv import load_dotenv
from services.Langchain_service import chat_with_model, greet_user, invoke_model
import logging

# For extracting history
from services.Langchain_service import get_chat_history
from services.after_call_ends import change_call_status_to_completed

# for sentiment analysis
from services.sentiment_analysis import check_sentiment_using_textblob


# For Prompt
from services.preparing_prompt import prepare_prompt

# get-data-before-call
from services.eleven_lab_services import eleven_labs_voices
from services.postgres import get_time_from_schedule_call_using_patient_id, get_voice_from_db, get_first_name_of_patient, get_carehome_id_from_patient_id

# for db
from fastapi import Depends
from sqlalchemy.orm import Session
from db.postgres import get_db

# For uploading on mongodb
from services.mongodb_service import upload_chat_history_on_mongodb



# import uid for new chats
import uuid 



# For TTS (text to speech)
from utils.eleven_labs_utils import text_to_speech

# for sending intruptions
from utils.utils import send_interruption

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



# we have this separate endpoint to save time on websocket endpoint
@router.get("/get-data-before-call")
def get_call_time(schedule_id: str,patient_id: str, db: Session = Depends(get_db)):
    """TO get 
        -> Time duration of the cal.
        -> To get patient_id againt a schedule_id (right now we aren't but in future if we need it cuz frontend alredy has patient_id)
        -> Voice_id (of ELevenlabs) which the bot uses for this patient
        -> User first name with which the bot greets the user"""
    try:
        call_time = get_time_from_schedule_call_using_patient_id(schedule_id)
        voice = get_voice_from_db(patient_id)
        voice_id = eleven_labs_voices.get(voice)
        patient_first_name = get_first_name_of_patient(patient_id)
        carehome_id = get_carehome_id_from_patient_id(patient_id)
        
        
        return JSONResponse(content={"call_time": call_time, "voice_id": voice_id, "patient_first_name": patient_first_name, "carehome_id": carehome_id}, status_code=200)
    
        
    except HTTPException as he: 
        raise he 
        
    except Exception as e:
        logger.exception("Error in get_call_time in routes/call.py/get-data-before-call -> ",str(e))
        return JSONResponse(content={"details": "Error occured"}, status_code=500)    
    
    


@router.websocket("/call-with-bot")
async def call_with_bot(websocket: WebSocket, 
    patient_id: str = Query(...),
    voice_id: str = Query(...),
    patient_name: str = Query(...),
    carehome_id: str = Query(...)
    ):
    await websocket.accept()

    try:
        
        prompt = prepare_prompt(patient_id)

        
        send_task = None
        
        new_chat_id = uuid.uuid1()
        
        dg_connection = deepgram_client.listen.websocket.v("1")

        message_queue = asyncio.Queue()
        
        
        greetings  = await greet_user(patient_name)
        audio = text_to_speech(greetings.content, voice_id)
        
        # Send audio as base64 string in JSON
        message = json.dumps({"audio": audio, "complete": True})
        message_queue.put_nowait(message)
        
        
        loop = asyncio.get_event_loop()

        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if result.speech_final and sentence.strip():
                logger.info(f"Received sentence: {sentence}")
                asyncio.run_coroutine_threadsafe(send_interruption(websocket), loop)
                llm_response = invoke_model(sentence,new_chat_id, prompt)  
                logger.info(f"Model respose is: {llm_response}")
                audio = text_to_speech(llm_response, voice_id)
                
                # Send audio as base64 string in JSON
                message = json.dumps({"audio": audio, "complete": True})
                message_queue.put_nowait(message)

                


        def on_error(self, error, **kwargs):
            logger.error(f"Deepgram error: {error}")
            raise RuntimeError(f"Error occurred on Deepgram: {str(error)}")


        def on_close(self, *args, **kwargs):  
            logger.info("Deepgram connection closed")
            raise RuntimeError("Connection closed")


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
            logger.error("Failed to start connection")
            raise RuntimeError("Failed to start connection")
    

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
                logger.exception("Error on websocket is: ",str(e))
                
                
                chat_history = get_chat_history(chat_with_model,new_chat_id)
                sentiment = check_sentiment_using_textblob(chat_history)
                did_upload = await upload_chat_history_on_mongodb(patient_id, new_chat_id, chat_history, carehome_id, sentiment)
                did_change = change_call_status_to_completed(patient_id)
                if did_change:
                    logger.info("Call status changed to completed")
                break

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket.close()
    finally:
        if dg_connection is not None:
            dg_connection.finish()
        if send_task is not None:
            send_task.cancel()
    try:
        await websocket.close()
    except RuntimeError:
        logger.error("WebSocket already closed.")

