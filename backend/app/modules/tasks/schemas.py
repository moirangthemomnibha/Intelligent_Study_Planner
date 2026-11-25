from datetime import date, datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


class TaskCreate(BaseModel):
    student_id: int
    subject_id: Optional[int] = None
    topic_id: Optional[int] = None

    title: str = Field(min_length=2, max_length=150)
    description: Optional[str] = None

    priority: Literal["Low", "Medium", "High"] = "Medium"
    status: Literal["Not Started", "In Progress", "Completed"] = "Not Started"

    deadline: Optional[date] = None
    estimated_minutes: Optional[int] = Field(default=None, gt=0)


class TaskUpdate(BaseModel):
    subject_id: Optional[int] = None
    topic_id: Optional[int] = None

    title: Optional[str] = Field(default=None, min_length=2, max_length=150)
    description: Optional[str] = None

    priority: Optional[Literal["Low", "Medium", "High"]] = None
    status: Optional[Literal["Not Started", "In Progress", "Completed"]] = None

    deadline: Optional[date] = None
    estimated_minutes: Optional[int] = Field(default=None, gt=0)


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    subject_id: Optional[int]
    topic_id: Optional[int]

    title: str
    description: Optional[str]

    priority: str
    status: str

    deadline: Optional[date]
    estimated_minutes: Optional[int]

    created_at: datetime
    updated_at: datetime