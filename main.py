import requests
import base64
import json
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
import asyncio
import os
from dotenv import load_dotenv
from services.Langchain_service import chat_prompt, HumanMessage, model

# For running main.py 
import uvicorn

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


# Initialize Deepgram client with API key from environment variable
api_key = os.getenv("DEEPGRAM_API_KEY")
if not api_key:
    raise ValueError("Deepgram API Key is missing.")
deepgram_client = DeepgramClient(api_key)

# Function to clean up repeated words or phrases in a sentence
def invoke_model(input):
    initial_message = HumanMessage(content=f"user query is: {input}")

    # Generate the response using the model
    output = model.invoke(chat_prompt.format(messages=[initial_message]))
    #print(output.content)
    return output.content

def tts_service(text, message_queue,audio):
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
        message_queue.put_nowait(message)
        #print("Sent combined audio to frontend")
        # After combining chunks
        #print(f"Combined audio size: {len(combined_audio)} bytes")
        #print(f"Base64 audio length: {len(audio_base64)} characters")

    except Exception as e:
        print(f"Error in TTS service: {e}")

@app.get("/")
def check_me():
    return {"message":"Done"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    #print("Started receiving")

    try:
        # Create a live transcription connection
        dg_connection = deepgram_client.listen.live.v("1")

        # Create a queue to pass messages from Deepgram to the WebSocket
        message_queue = asyncio.Queue()

        # Define event handlers
        def on_message(self, result, **kwargs):
            # Extract transcription from result
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return
            if result.speech_final:
                #print(f"Final Transcription (cleaned): {sentence}")
                llm_response = invoke_model(sentence)
                cleaned_llm_response = remove_thinking(llm_response)

                # Send text to TTS service for conversion to speech
                tts_service(cleaned_llm_response, message_queue, "f")

        def on_error(self, error, **kwargs):
            print(f"Error: {error}")

        def on_close(self, **kwargs):
            print("Connection closed")


        # Attach event handlers
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        dg_connection.on(LiveTranscriptionEvents.Close, on_close)

        # Configure Deepgram options
        options = LiveOptions(
            model="nova-3",
            smart_format=True,
            interim_results=True,
            language="en",
        )

        # Start the Deepgram connection
        if not dg_connection.start(options):
            #print("Failed to start Deepgram connection")
            await websocket.close()
            return

        # Start a task to send messages from the queue to the WebSocket
        async def send_messages():
            while True:
                message = await message_queue.get()
                await websocket.send_text(message)

        send_task = asyncio.create_task(send_messages())

        # Forward audio chunks from the frontend to Deepgram
        while True:
            try:
                data = await websocket.receive_bytes()
                dg_connection.send(data)
            except WebSocketDisconnect:
                #print("Client disconnected")
                break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        dg_connection.finish()
        send_task.cancel()  
    try:
        await websocket.close()
    except RuntimeError:
        print("WebSocket already closed.")



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

