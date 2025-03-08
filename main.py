import azure.cognitiveservices.speech as speechsdk
from fastapi import FastAPI, WebSocket
import uuid
from openai import AsyncAzureOpenAI
import asyncio
import threading

# Azure Speech Credentials
AZURE_SPEECH_KEY = "FEljpwVzv1aGio9Ggq8wHmH2ZnzEb0urkqstPkAYJIlOfaidTWRyJQQJ99ALACYeBjFXJ3w3AAAYACOGLTg3"
AZURE_REGION = "eastus"
azure_api_key = "6mqmitHGjAWZdhkaGlK3AxqtfzY4kARAh2SYaIuR5U0quQZDgHlSJQQJ99ALACYeBjFXJ3w3AAABACOGrqlN"
azure_api_base = "https://mindmetabot.openai.azure.com/"
api_type = "azure"
open_api_version = "2023-03-15-preview"  


DEPLOYMENT_NAME = "gpt-4o-mini"  

user_info ="Pete Hillman , a 78-year-old retired postmaster from Bristol, UK, who is living with early-stage dementia in a care home "


my_system_prompt = f"""You're Pete's compassionate dementia companion. Your name is Elys Use memory to:
1. Greet Pete only once at the start of the conversation using 'Hey [patient name]' or 'Hello [patient name]'.
2. If Pete says 'Hello' or 'Hi' again later in the chat, do NOT greet him again. Instead, acknowledge with a simple reassurance, like:
User: Hello
Your response: Yes, I'm here.
3. Engage through reminiscence & open-ended questions
4. Maintain empathy-first communication
5. Encourage user to share stories by asking open-ended questions tied to his past:
    "Pete, do you remember the first day you started working at the post office? What was it like stepping into that role?"
6. Leverage known personal details (family/hobbies/history)
     user infomation is: {user_info}
7. Anchor discussions in familiar joys:
"Your love for classical music is truly inspiring! Who’s your favorite composer? Was it Mozart or Beethoven?"
8. Handle interruptions gracefully
6. Use NLP techniques & therapeutic storytelling
8. If Pete becomes confused or disengaged, gently redirect the conversation:
    "That’s okay, Pete! Let’s talk about something else. Have you spoken to Phil recently?"

Start warmly, end reassuringly. Keep responses natural and focused on verified information."""







app = FastAPI()

# Global state management
class ConversationState:
    def __init__(self):
        self.recognized_text = ""
        self.is_speaking = False
        self.stop_synthesis = threading.Event()
        self.active_patients = {}  # Now using patient_id as key

state = ConversationState()

# Azure Speech Config
speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)
speech_config.set_property(speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs, "500")
speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm)



azure_ai_client = AsyncAzureOpenAI(  
    azure_endpoint=azure_api_base,
    api_key=azure_api_key,
    api_version=open_api_version
)
# --- Create recognizer for audio input ---
def create_recognizer():
    audio_format = speechsdk.audio.AudioStreamFormat(
        samples_per_second=16000,
        bits_per_sample=16,
        channels=1
    )
    push_stream = speechsdk.audio.PushAudioInputStream(audio_format)
    audio_config = speechsdk.audio.AudioConfig(stream=push_stream)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    return recognizer, push_stream

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    push_stream = None
    recognizer = None
    patient_id = None

    try:
        # Step 1: Receive patient ID from the client.
        init_data = await websocket.receive_json()
        patient_id = init_data.get("patient_id")
        if not patient_id:
            await websocket.send_text("ERROR: Missing patient_id in initial message")
            await websocket.close()
            return

        # Step 2: Initialize components and store patient state.
        recognizer, push_stream = create_recognizer()
        state.active_patients[patient_id] = {
            "history": [],
            "recognizer": recognizer,
            "push_stream": push_stream,
            "has_greeted": False,
            "last_text": ""
        }

        # Event handler: store recognized speech text.
        def recognized_handler(evt):
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                text = evt.result.text.strip()
                if text:
                    state.active_patients[patient_id]["last_text"] = text

        recognizer.recognized.connect(recognized_handler)
        recognizer.start_continuous_recognition()

        # Step 3: Process incoming audio chunks from the client.
        while True:
            audio_chunk = await websocket.receive_bytes()
            push_stream.write(audio_chunk)

            # Check if recognized text is available.
            last_text = state.active_patients[patient_id].get("last_text", "")
            if last_text:
                # Safely remove the recognized text so it isn’t processed twice.
                user_text = state.active_patients[patient_id].pop("last_text", "")
                # print("User text is:", user_text)
                # Stream GPT response directly to TTS.
                await stream_response_to_tts(patient_id, user_text, websocket)

    except Exception as e:
        print(f"[{patient_id}] Error: {str(e)}")
    finally:
        if recognizer:
            recognizer.stop_continuous_recognition()
        if push_stream:
            push_stream.close()
        if patient_id in state.active_patients:
            del state.active_patients[patient_id]
        await websocket.close()

async def stream_response_to_tts(patient_id: str, user_text: str, websocket: WebSocket):
    try:
        state.is_speaking = True
        state.stop_synthesis.clear()

        # --- Setup TTS using Text Streaming (WebSocket v2 endpoint) ---
        # IMPORTANT: Must use the websocket v2 endpoint.
        tts_speech_config = speechsdk.SpeechConfig(
            endpoint=f"wss://{AZURE_REGION}.tts.speech.microsoft.com/cognitiveservices/websocket/v2",
            subscription=AZURE_SPEECH_KEY  # Use the appropriate key for TTS.
        )
        # Set a supported voice (SSML isn’t supported in text streaming).
        tts_speech_config.speech_synthesis_voice_name = "en-US-BrianMultilingualNeural"

        # Set extended timeout properties to handle GPT latency.
        properties = {
            "SpeechSynthesis_FrameTimeoutInterval": "100000000",
            "SpeechSynthesis_RtfTimeoutThreshold": "10"
        }
        tts_speech_config.set_properties_by_name(properties)

        # Create a PullAudioOutputStream and AudioOutputConfig to capture the audio data instead of local playback.
        pull_stream = speechsdk.audio.PullAudioOutputStream()
        audio_config = speechsdk.audio.AudioOutputConfig(stream=pull_stream)
        tts_synthesizer = speechsdk.SpeechSynthesizer(speech_config=tts_speech_config, audio_config=audio_config)

        # Attach an event handler so that synthesized audio chunks are sent immediately to the frontend.
        # def synthesizing_handler(evt):
        #     pass
            # print("Synthesizing_handle called")
            # if evt.audio_data:
            #     print("Audio data length:", len(evt.audio_data), "bytes")
            #     # Print the first 20 bytes in hex for inspection
            #     print("First 20 bytes (hex):", evt.audio_data[:20].hex())
            #     asyncio.create_task(websocket.send_bytes(evt.audio_data))
        # tts_synthesizer.synthesizing.connect(synthesizing_handler)

        # Create a TTS request with TextStream input type.
        tts_request = speechsdk.SpeechSynthesisRequest(
            input_type=speechsdk.SpeechSynthesisRequestInputType.TextStream
        )
        # Start TTS synthesis asynchronously (it will wait for text input via tts_request.input_stream).
        tts_task = tts_synthesizer.speak_async(tts_request)

        # --- Stream GPT response to TTS ---
        # Prepare conversation history.
        patient = state.active_patients.get(patient_id)
        if not patient:
            return

        if not patient.get("has_greeted", False):
            system_prompt = my_system_prompt  # Your defined system prompt.
            patient["history"] = [
                {"role": "system", "content": system_prompt},
                {"role": "assistant", "content": "Hello Pete, I'm Elys..."}
            ]
            patient["has_greeted"] = True
        else:
            patient["history"].append({"role": "user", "content": user_text})

        # Request a GPT streaming response.
        gpt_response = await azure_ai_client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=patient["history"],
            stream=True
        )

        full_response = ""
        async for chunk in gpt_response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = ""
                if hasattr(chunk.choices[0].delta, "content"):
                    delta = chunk.choices[0].delta.content or ""
                if delta:
                    full_response += delta
                    # As soon as a text chunk is received, write it to the TTS input stream.
                    # print("Sending to TTS:", delta)
                    tts_request.input_stream.write(delta)
                    if state.stop_synthesis.is_set():
                        break

        # Signal that no more text is coming.
        tts_request.input_stream.close()

        # Wait for the TTS synthesis task to complete.
        result = tts_task.get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            audio_data = result.audio_data  # This is a bytes object with the complete synthesized audio.
            # print("Final audio data length:", len(audio_data), "bytes")
            await websocket.send_bytes(audio_data)
        else:
            error_details = result.error_details if result.error_details else "Unknown error"
            print("Error in TTS:", error_details)
            await websocket.send_text(f"[ERROR] {error_details}")

        # Append the full GPT response to the conversation history.
        patient["history"].append({"role": "assistant", "content": full_response})

    except Exception as e:
        print(f"[{patient_id}] TTS error: {str(e)}")
        await websocket.send_text(f"[ERROR] {str(e)}")
    finally:
        state.is_speaking = False

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)