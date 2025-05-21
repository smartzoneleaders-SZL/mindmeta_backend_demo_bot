from fastapi import FastAPI,Depends, HTTPException, APIRouter

import asyncio

from opensipscall import OpenSIPSClient, ElevenLabsStreamer
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
import asyncio
import openai
import os
import json
import base64
import logging

from sqlalchemy.orm import Session


# Postgres
from db.postgres import get_db
from services.postgres import get_patient_id_from_schedule_id, get_patient_phone_number


router = APIRouter()

# CONFIG
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_VOICE_ID = "gUbIduqGzBP438teh4ZA"

openai.api_key = OPENAI_API_KEY
logger = logging.getLogger("voicebot")
logging.basicConfig(level=logging.INFO)


async def run_conversation(client, call_id):
    tts = ElevenLabsStreamer(client, call_id)
    dg_client = DeepgramClient(DEEPGRAM_API_KEY)
    dg_connection = dg_client.listen.websocket.v("1")

    loop = asyncio.get_event_loop()
    user_transcript = ""
    response_event = asyncio.Event()

    # Initial greeting
    greeting = "Hello! This is your virtual assistant. How can I help you today?"
    await tts.stream_from_elevenlabs(greeting, ELEVENLABS_VOICE_ID)

    def on_message(self, result, **kwargs):
        nonlocal user_transcript
        if result.speech_final:
            sentence = result.channel.alternatives[0].transcript.strip()
            if sentence:
                logger.info(f"User: {sentence}")
                user_transcript = sentence
                loop.call_soon_threadsafe(response_event.set)

    def on_error(self, error, **kwargs):
        logger.error(f"Deepgram error: {error}")
        raise RuntimeError("Deepgram error")

    def on_close(self, *args, **kwargs):
        logger.info("Deepgram connection closed")
        raise RuntimeError("Deepgram connection closed")

    dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
    dg_connection.on(LiveTranscriptionEvents.Error, on_error)
    dg_connection.on(LiveTranscriptionEvents.Close, on_close)

    # Start Deepgram transcription
    options = LiveOptions(
        model="nova-3",
        smart_format=True,
        interim_results=False,
        language="en"
    )

    if dg_connection.start(options) is False:
        logger.error("Failed to start Deepgram")
        return

    # Start streaming microphone input
    async def capture_audio():
        while True:
            audio = await client.capture_microphone_audio_chunk(call_id)
            if audio:
                dg_connection.send(audio)

    asyncio.create_task(capture_audio())

    # Conversation loop
    while True:
        user_transcript = ""
        try:
            await asyncio.wait_for(response_event.wait(), timeout=15)
        except asyncio.TimeoutError:
            logger.info("No response, ending conversation")
            break

        if not user_transcript:
            break

        # Call LLM
        messages = [
            {"role": "system", "content": "You are a helpful voice assistant."},
            {"role": "user", "content": user_transcript}
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7
            )
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM error: {e}")
            reply = "I'm sorry, I had a problem understanding. Could you repeat that?"

        logger.info(f"Bot: {reply}")
        await tts.stream_from_elevenlabs(reply, ELEVENLABS_VOICE_ID)
        response_event.clear()

    dg_connection.finish()





@router.post("/call-user")
async def call_user(schedule_id: str, db: Session = Depends(get_db)):
    try:
        print("creating task while schdule id is: ",schedule_id)
        asyncio.create_task(start_call_flow(schedule_id, db))
        return {"status": "call started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start call task: {str(e)}")


async def start_call_flow(schedule_id, db):
    try:
        
        patient_id = get_patient_id_from_schedule_id(db, schedule_id)
        
        if not patient_id:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        phone_number = get_patient_phone_number(db, patient_id)
        print("Phone number is: ",phone_number)
        
        server_uri = "wss://ats-demo.call-matrix.com:6061"
        username = "test_test.com"
        password = "l3tMe.Test"
        domain = "tenant_2"

        client = OpenSIPSClient(server_uri, username, password, domain)
        await client.connect()
        print("Connected to SIP server")
        await client.register()
        print("Registered with SIP server")

        result = await client.place_call(phone_number, timeout=30)
        if result["success"]:
            print("Call placed successfully")
            call_id = result["call_id"]
            await run_conversation(client, call_id)
            await client.end_call(call_id)

        await client.disconnect()
    except Exception as e:
        print(f"Error during call flow: {str(e)}")