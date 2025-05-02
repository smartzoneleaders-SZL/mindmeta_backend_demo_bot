import requests
import io
import os
from typing import Optional
from fastapi import HTTPException


class ElevenLabsService:
    """Service to handle interactions with ElevenLabs API for text-to-speech"""
    
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    @staticmethod
    def get_voices():
        """Get all available voices from ElevenLabs"""
        response = requests.get(
            f"{ElevenLabsService.BASE_URL}/voices",
            headers={"xi-api-key": os.getenv('ELEVENLABS_API_KEY')}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, 
                               detail=f"ElevenLabs API error: {response.text}")
        
        return response.json()
    
    @staticmethod
    def text_to_speech(text: str, voice_id: str, optimize_streaming_latency: Optional[int] = 4) -> bytes:
        """
        Convert text to speech using ElevenLabs API
        
        Args:
            text: The text to convert to speech
            voice_id: The ElevenLabs voice ID to use
            optimize_streaming_latency: Level of optimization (0-4, higher = lower latency)
            
        Returns:
            Audio data as bytes
        """
        url = f"{ElevenLabsService.BASE_URL}/text-to-speech/{voice_id}/stream"
        
        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2",  # Fastest model for real-time applications
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            },
            "optimize_streaming_latency": optimize_streaming_latency
        }
        
        response = requests.post(
            url,
            headers={
                "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
                "Content-Type": "application/json",
                "Accept": "audio/mpeg"
            },
            json=payload,
            stream=True
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, 
                               detail=f"ElevenLabs API error: {response.text}")
        
        # Read and return audio bytes
        buffer = io.BytesIO()
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                buffer.write(chunk)
        
        buffer.seek(0)
        return buffer.read()