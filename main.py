import aiohttp  
import base64
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
import asyncio
import os
from dotenv import load_dotenv
from services.Langchain_service import chat_prompt, HumanMessage, model

# For running main.py 
import uvicorn

# from datetime
from datetime import datetime

# From openai
from services.openai_service import system_prompt, client

# For middleware
from fastapi.middleware.cors import CORSMiddleware

# For parsers
from utils.parsers.parsers_for_llm import remove_thinking

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

async def invoke_model(input):
    # print("Entered invoke function")
    system_prompt.append({'role': "user", "content": input})
    # print("Chat completion before")
    # print("System prompt is: ",system_prompt)
    data = await client.chat.completions.create(
    model="gpt-4o", messages=system_prompt
    )
    message = data.choices[0].message
    # print("Model response in invoke_model is: ", message.content)
    print("Request arrived at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return message.content 

async def async_tts_service(text, message_queue, audio):
    print("Going to so tts for: ",text)
    voice = 'aura-athena-en'
    if audio == 'm':
        voice = 'aura-helios-en'
    
    DEEPGRAM_URL = f"https://api.deepgram.com/v1/speak?model={voice}"
    DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                DEEPGRAM_URL,
                headers={
                    "Authorization": f"Token {DEEPGRAM_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={"text": text}
            ) as response:
                if response.status != 200:
                    # print("TTS request failed")
                    return

                audio_data = await response.read()
                audio_base64 = base64.b64encode(audio_data).decode("utf-8")
                message = json.dumps({"audio": audio_base64, "complete": True})
                print("going to send the TTS back to frontend:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                await message_queue.put(message)

        except Exception as e:
            print(f"TTS error: {e}")

@app.get("/")
def check_me():
    return {"message":"Done"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    loop = asyncio.get_running_loop()  # Get reference to main event loop

    try:
        send_task = None
        dg_connection = deepgram_client.listen.live.v("1")
        message_queue = asyncio.Queue()
        print("Received the request at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        async def process_llm_response(sentence):
            try:
                llm_response = await invoke_model(sentence)

                # print("LLM response is: ", llm_response)
                await async_tts_service(llm_response, message_queue, "f")
            except Exception as e:
                print(f"Processing error: {e}")

        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if result.speech_final and sentence.strip():
                msg_to_send= "hmmmm"
                print("before async hmmmm")
                print("STT done at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                asyncio.run_coroutine_threadsafe(async_tts_service(msg_to_send,message_queue,"f"),loop)
                # print(f"Final transcription: {sentence}")
                # Schedule in main event loop
                asyncio.run_coroutine_threadsafe(
                    process_llm_response(sentence),
                    loop
                )

        def on_error(self, error, **kwargs):
            print(f"Deepgram error: {error}")

        def on_close(self, *args, **kwargs):  
            print("Deepgram connection closed")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        dg_connection.on(LiveTranscriptionEvents.Close, on_close)

        options = LiveOptions(
            model="nova-3",
            smart_format=True,
            interim_results=True,
            language="en",
        )

        if not dg_connection.start(options):
            await websocket.close()
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
            except WebSocketDisconnect:
                break

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        dg_connection.finish()
        if send_task is not None:
            send_task.cancel()
    try:
        await websocket.close()
    except RuntimeError:
        print("WebSocket already closed.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

