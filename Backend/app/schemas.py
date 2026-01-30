from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from uuid import UUID

# --- Request Models ---

class InterviewStartRequest(BaseModel):
    target_company: str
    job_role: str
    interview_style: str
    difficulty: str
    topic: Optional[str] = None
    max_follow_ups: int = 1 # Default to 1 follow-up per question

class ChatRequest(BaseModel):
    session_id: str
    user_input: Optional[str] = None
    audio_file_data: Optional[bytes] = None # For direct file upload if needed, usually handled via UploadFile

class ReportRequest(BaseModel):
    session_id: str

# --- Response Models ---

class InterviewStartResponse(BaseModel):
    session_id: str
    message: str
    first_question: str

class ChatResponse(BaseModel):
    question: Optional[str] = None
    audio_url: Optional[str] = None # URL to TTS audio
    feedback: Optional[Dict[str, Any]] = None
    user_transcript: Optional[str] = None # Transcribed text from audio
    is_finished: bool = False

class ReportResponse(BaseModel):
    report_content: str
