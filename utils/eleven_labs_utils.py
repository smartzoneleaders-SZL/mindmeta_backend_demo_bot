from services.eleven_lab_services import ElevenLabsService
import base64

def text_to_speech(text: str, voice_id: str) -> bytes:
    """Convert text to speech using ElevenLabs API with latency optimization"""
    try:
        audio_data = ElevenLabsService.text_to_speech(
            text=text, 
            voice_id= voice_id, 
            optimize_streaming_latency=4
        )

        # Encode audio bytes to base64 string
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        return audio_base64
    
    except Exception as e:
        return text_to_speech("Oh sorry can you repeat?")
