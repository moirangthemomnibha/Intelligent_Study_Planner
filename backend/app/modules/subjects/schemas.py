from datetime import date
from pydantic import BaseModel, Field, field_validator


class SubjectCreate(BaseModel):
    student_id: int = Field(gt=0)
    name: str = Field(min_length=2, max_length=100)
    exam_date: date
    exam_weight: float = Field(default=1.0, ge=0)

    @field_validator("exam_date")
    @classmethod
    def validate_exam_date(cls, value):
        if value < date.today():
            raise ValueError("Exam date cannot be in the past.")
        return value


class SubjectRead(SubjectCreate):
    id: int