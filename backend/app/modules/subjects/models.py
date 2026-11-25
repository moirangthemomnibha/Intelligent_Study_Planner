from typing import Optional
from sqlmodel import SQLModel, Field


class Subject(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(index=True, foreign_key="student.id")
    name: str
    exam_date: str
    exam_weight: float = 1.0