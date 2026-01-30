import os
import asyncio
from typing import Optional
import assemblyai as aai
from elevenlabs.client import ElevenLabs

from app.core.config import settings
from app.core.logging_config import logger

class VoiceService:
    def __init__(self):
        # Initialize AssemblyAI
        if settings.ASSEMBLYAI_API_KEY:
            aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
            self.transcriber = aai.Transcriber()
        else:
            logger.warning("AssemblyAI API Key not found. STT will be disabled.")
            self.transcriber = None

        # Initialize ElevenLabs
        if settings.ELEVENLABS_API_KEY:
            self.elevenlabs = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        else:
            logger.warning("ElevenLabs API Key not found. TTS will be disabled.")
            self.elevenlabs = None

    async def transcribe_audio(self, file_path: str) -> str:
        """Transcribes audio file using Google Gemini (Fallbacks to AssemblyAI if needed)."""
        
        # Method 1: Google Gemini (Multimodal) - Robust & supports many formats without FFMPEG
        if settings.GOOGLE_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                
                logger.info(f"Uploading audio {file_path} to Gemini...")
                # Upload file
                audio_file = genai.upload_file(path=file_path)
                
                # Prompt
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content([
                    "Transcribe this audio file verbatim. Output strictly the transcription text only.",
                    audio_file
                ])
                
                logger.info("Gemini Transcription complete.")
                return response.text.strip()
            except Exception as e:
                logger.error(f"Gemini STT failed: {e}")
                # Fallthrough to AssemblyAI
        
        # Method 2: AssemblyAI
        if not self.transcriber:
             raise ValueError("No Transcription service available (Gemini or AssemblyAI). check API Keys.")

        logger.info(f"Transcribing audio with AssemblyAI: {file_path}")
        
        # AssemblyAI SDK is synchronous, run in executor
        loop = asyncio.get_event_loop()
        
        try:
            transcript = await loop.run_in_executor(
                None, 
                self.transcriber.transcribe, 
                file_path
            )
            
            if transcript.status == aai.TranscriptStatus.error:
                raise Exception(transcript.error)
                
            return transcript.text
        except Exception as e:
            logger.error(f"AssemblyAI Transcription failed: {e}")
            raise

    async def generate_audio(self, text: str, output_path: str) -> Optional[str]:
        """Generates audio from text using ElevenLabs."""
        logger.info(f"ENTER generate_audio: {text[:20]}...")
        if not self.elevenlabs:
            logger.error("ElevenLabs not configured")
            raise ValueError("ElevenLabs not configured.")

        logger.info(f"Generating audio for: {text[:50]}...")
        
        try:
            # Run blocking generation in executor
            loop = asyncio.get_event_loop()
            
            # Use default voice for now
            audio_generator = await loop.run_in_executor(
                None,
                lambda: self.elevenlabs.generate(
                    text=text,
                    voice="Rachel", # Default popular voice
                    model="eleven_monolingual_v1"
                )
            )
            
            # Save to file
            with open(output_path, "wb") as f:
                for chunk in audio_generator:
                    f.write(chunk)
            
            return output_path
        except Exception as e:
            logger.error(f"ElevenLabs TTS generation failed: {e}. Falling back to gTTS.")
            
            # Fallback: gTTS (Free)
            try:
                from gtts import gTTS
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: gTTS(text=text, lang='en').save(output_path)
                )
                logger.info("gTTS generation successful.")
                return output_path
            except Exception as e_gtts:
                logger.error(f"gTTS also failed: {e_gtts}")
                raise

voice_service = VoiceService()
