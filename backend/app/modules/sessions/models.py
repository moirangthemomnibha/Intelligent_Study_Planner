from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field


class StudySession(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    student_id: int = Field(index=True)

    topic_id: int = Field(index=True)

    planned_date: str

    planned_minutes: int

    actual_minutes: int | None = None

    status: str = Field(
        default="planned",
        index=True
    )

    reflection: str | None = None

    completed_at: datetime | None = None

    original_planned_date: str | None = None

    rescheduled_count: int = Field(default=0)

    missed_reason: str | None = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )