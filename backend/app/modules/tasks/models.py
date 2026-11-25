from datetime import datetime, date, timezone
from typing import Optional

from sqlmodel import SQLModel, Field


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)

    student_id: int = Field(foreign_key="student.id", index=True)
    subject_id: Optional[int] = Field(
        default=None, foreign_key="subject.id", index=True
    )
    topic_id: Optional[int] = Field(
        default=None, foreign_key="topic.id", index=True
    )

    title: str = Field(min_length=2, max_length=150)
    description: Optional[str] = Field(default=None)

    priority: str = Field(default="Medium")
    status: str = Field(default="Not Started")

    deadline: Optional[date] = Field(default=None)
    estimated_minutes: Optional[int] = Field(default=None, gt=0)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))