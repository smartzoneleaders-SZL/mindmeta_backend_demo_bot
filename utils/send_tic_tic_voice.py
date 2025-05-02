import json
import base64

def send_audio_from_local(audio_file_path):
    try:
        # Open the audio file in binary mode
        with open(audio_file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        return audio_bytes
    except Exception as e:
        print("Error while sending audio from local directory:", e)
