from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from pydantic import EmailStr

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class InterviewStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class InterviewStyle(str, Enum):
    VISUAL = "visual"           # e.g., friendly, seeing the interviewer
    PROFESSIONAL = "professional"
    HR = "hr"
    TECHNICAL = "technical"

class User(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(index=True, unique=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.USER)
    
    sessions: List["InterviewSession"] = Relationship(back_populates="user")

class InterviewSession(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    job_role: str
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM)
    interview_style: InterviewStyle = Field(default=InterviewStyle.PROFESSIONAL)
    target_company: Optional[str] = None
    status: InterviewStatus = Field(default=InterviewStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    final_analysis_report: Optional[str] = Field(default=None, description="JSON or text summary of the interview")

    user: User = Relationship(back_populates="sessions")
    questions: List["Question"] = Relationship(back_populates="session")

class Question(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="interviewsession.id")
    content: str
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    order: int
    
    session: InterviewSession = Relationship(back_populates="questions")
    response: Optional["Response"] = Relationship(back_populates="question")

class Response(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    question_id: UUID = Field(foreign_key="question.id")
    audio_url: Optional[str] = None
    transcript: Optional[str] = None
    sentiment_score: Optional[float] = None
    
    question: Question = Relationship(back_populates="response")
    feedback: Optional["Feedback"] = Relationship(back_populates="response")

class Feedback(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    response_id: UUID = Field(foreign_key="response.id")
    content: str
    score: Optional[int] = None
    
    response: Response = Relationship(back_populates="feedback")
