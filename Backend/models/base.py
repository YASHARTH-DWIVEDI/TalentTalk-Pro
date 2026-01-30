from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Candidate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    resume_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InterviewSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: int = Field(foreign_key="candidate.id")
    role: str
    status: str = "scheduled" # scheduled, in_progress, completed
    created_at: datetime = Field(default_factory=datetime.utcnow)
