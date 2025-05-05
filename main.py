import requests  
import base64
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
import asyncio
import os
from dotenv import load_dotenv
from services.Langchain_service import chat_with_model
import logging
# For extracting history
from services.after_call_ends import get_chat_hisory

# For running main.py 
import uvicorn

# import uid for new chats
import uuid 

# from datetime
from datetime import datetime

# For eleven labs
from services.eleven_lab_services import ElevenLabsService

# From openai
# from services.openai_service import system_prompt, client

# For direct groq
# from services.direct_langchain import client
# from services.openai_service import main_prompt

# For middleware
from fastapi.middleware.cors import CORSMiddleware







load_dotenv()

app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Deepgram client
api_key = os.getenv("DEEPGRAM_API_KEY")
if not api_key:
    raise ValueError("Deepgram API Key is missing.")
deepgram_client = DeepgramClient(api_key)

def invoke_model(input, chat_id):
    input_data = {"messages": [{"role": "user", "content": input}]}
    config = {"configurable": {"thread_id": chat_id}}
    response = chat_with_model.invoke(input_data, config=config)
    return response["messages"][-1].content





def text_to_speech(text: str, message_queue) -> bytes:
    """Convert text to speech using ElevenLabs API with latency optimization"""
    try:
        logging.info("Sending llm response to TTS: ", text)
        audio_data = ElevenLabsService.text_to_speech(
            text=text, 
            voice_id="gUbIduqGzBP438teh4ZA",  # Just for demo: Rachel voice
            optimize_streaming_latency=4
        )

        # Encode audio bytes to base64 string
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')

        # Send audio as base64 string in JSON
        message = json.dumps({"audio": audio_base64, "complete": True})
        message_queue.put_nowait(message)
        
        return True
        
    except Exception as e:
        return text_to_speech("Oh sorry can you repeat?")

# this is for deepgram tts (incase we switch but right now its not being used)
# def async_tts_service(text, message_queue, audio):
#     logging.info("Sending llm to TTS: ",text)
#     voice = 'aura-athena-en'
#     if audio == 'm':
#         voice = 'aura-helios-en'
#     try: 
#         DEEPGRAM_URL = f"https://api.deepgram.com/v1/speak?model={voice}"
#         DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")  # Use the correct API key

#         payload = {
#             "text": text  # Use the text passed to the function
#         }

#         headers = {
#             "Authorization": f"Token {DEEPGRAM_API_KEY}",
#             "Content-Type": "application/json"
#         }

#         response = requests.post(DEEPGRAM_URL, headers=headers, json=payload, stream=True)

#         # Check if the response is valid
#         if not response.ok:
#             #print("Failed to get audio from TTS service")
#             return

#         # Collect all chunks
#         audio_chunks = []
#         for chunk in response.iter_content(chunk_size=1024):
#             if chunk:
#                 audio_chunks.append(chunk)

#         # Combine all chunks into a single file
#         combined_audio = b"".join(audio_chunks)
#         audio_base64 = base64.b64encode(combined_audio).decode("utf-8")

#         # Send the combined audio to the frontend
#         message = json.dumps({"audio": audio_base64, "complete": True})
#         logging.info("Sending voice to frontend")
#         message_queue.put_nowait(message)
#     except Exception as e:
#         print(f"TTS error: {e}")

@app.get("/")
def check_me():
    return {"message":"Done"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logging.info("Entered")
    dg_connection = None
    await websocket.accept()
    try:
        send_task = None
        new_chat_id = uuid.uuid1()
        
        dg_connection = deepgram_client.listen.websocket.v("1")

        message_queue = asyncio.Queue()

        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if result.speech_final and sentence.strip():
                llm_response = invoke_model(sentence,new_chat_id)  
                text_to_speech(llm_response, message_queue)

                


        def on_error(self, error, **kwargs):
            logging.error(f"Deepgram error: {error}")

        def on_close(self, *args, **kwargs):  
            logging.info("Deepgram connection closed")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        dg_connection.on(LiveTranscriptionEvents.Close, on_close)

        options = LiveOptions(
            model="nova-3",
            smart_format=True,
            interim_results=True,
            language="en",
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
                print("Error on websocket is: ",str(e))
                
                # printing all the history interaction 
                get_chat_hisory(chat_with_model,new_chat_id)
                break

    except Exception as e:
        logging.error(f"WebSocket error: {e}")
    finally:
        if dg_connection is not None:
            dg_connection.finish()
        if send_task is not None:
            send_task.cancel()
    try:
        await websocket.close()
    except RuntimeError:
        logging.error("WebSocket already closed.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)

