from pydantic import BaseModel, Field
from typing import List

class PlanRequest(BaseModel):
    student_id: int
    horizon_days: int = Field(default=7, ge=1, le=30)
    available_minutes_per_day: int = Field(default=180, gt=0)

class PlannedSession(BaseModel):
    topic_id: int
    topic_name: str
    day: str
    duration_minutes: int
    priority_score: float
    reason: str

from datetime import date


class PlanSettingsCreate(BaseModel):
    student_id: int
    plan_start: date
    plan_days: int = Field(default=7, ge=1, le=30)


class PlanSettingsRead(BaseModel):
    id: int
    student_id: int
    plan_start: date
    plan_days: int