from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field


class PreferredStudyTime(SQLModel, table=True):
    __tablename__ = "preferred_study_times"

    id: Optional[int] = Field(default=None, primary_key=True)

    student_id: int = Field(
        foreign_key="student.id",
        index=True
    )

    day_of_week: int = Field(ge=0, le=6)

    start_time: str
    end_time: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )