from typing import Optional
from sqlmodel import SQLModel, Field

class Topic(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(index=True, foreign_key="subject.id")
    name: str
    estimated_minutes: int = 60
    difficulty: int = Field(default=3, ge=1, le=5)
    completion_percent: float = 0.0
    confidence: int = Field(default=3, ge=1, le=5)
    priority: int = 3
