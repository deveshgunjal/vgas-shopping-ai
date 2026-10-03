"""
VGAS Voice Assistant API
Provides speech-to-text and text-to-speech endpoints for seamless voice shopping.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import speech_recognition as sr
import pyttsx3

router = APIRouter(prefix="/voice", tags=["Voice Assistant"])

class VoiceRequest(BaseModel):
    audio_file_path: str

class TextResponse(BaseModel):
    text: str

@router.post("/stt", response_model=TextResponse)
async def speech_to_text(req: VoiceRequest):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(req.audio_file_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tts/{text}")
async def text_to_speech(text: str):
    try:
        engine = pyttsx3.init()
        engine.save_to_file(text, "tts_output.wav")
        engine.runAndWait()
        return {"message": "Audio generated at tts_output.wav"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
