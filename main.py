import requests  
import base64
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
import asyncio
import os
from dotenv import load_dotenv
from services.Langchain_service import chat_with_model

# For running main.py 
import uvicorn

# from datetime
from datetime import datetime

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

def invoke_model(input):
    input_data = {"messages": [{"role": "user", "content": input}]}
    config = {"configurable": {"thread_id": 'abc123'}}
    response = chat_with_model.invoke(input_data, config=config)
    return response["messages"][-1].content

# def invoke_model(input):
#     chat_completion = client.chat.completions.create(
#     messages=[
       
#         {
#             "role": "system",
#             "content": main_prompt
#         },
       
#         {
#             "role": "user",
#             "content": input
#         }
#     ],
#     model="mixtral-8x7b-32768"
#     )

#     print(chat_completion.choices[0].message.content)
#     return chat_completion.choices[0].message.content

def async_tts_service(text, message_queue, audio):
    print("LLM responded at: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    voice = 'aura-athena-en'
    if audio == 'm':
        voice = 'aura-helios-en'
    try:
        DEEPGRAM_URL = f"https://api.deepgram.com/v1/speak?model={voice}"
        DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")  # Use the correct API key

        payload = {
            "text": text  # Use the text passed to the function
        }

        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(DEEPGRAM_URL, headers=headers, json=payload, stream=True)

        # Check if the response is valid
        if not response.ok:
            #print("Failed to get audio from TTS service")
            return

        # Collect all chunks
        audio_chunks = []
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                audio_chunks.append(chunk)

        # Combine all chunks into a single file
        combined_audio = b"".join(audio_chunks)
        audio_base64 = base64.b64encode(combined_audio).decode("utf-8")

        # Send the combined audio to the frontend
        message = json.dumps({"audio": audio_base64, "complete": True})
        print("sending response at: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        message_queue.put_nowait(message)
    except Exception as e:
        print(f"TTS error: {e}")

@app.get("/")
def check_me():
    return {"message":"Done"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    loop = asyncio.get_running_loop()  
    try:
        send_task = None
        dg_connection = deepgram_client.listen.live.v("1")
        message_queue = asyncio.Queue()

        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if result.speech_final and sentence.strip():
                print("STT done at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                llm_response = invoke_model(sentence)
                async_tts_service(llm_response, message_queue, "f")


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

