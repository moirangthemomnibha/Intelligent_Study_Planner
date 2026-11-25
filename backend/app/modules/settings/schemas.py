from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SettingsUpdate(BaseModel):

    # Appearance
    theme: Optional[str] = None
    accent_color: Optional[str] = None
    font_size: Optional[str] = None

    # Pomodoro
    pomodoro_work_min: Optional[int] = Field(default=None, ge=1, le=180)
    pomodoro_short_break_min: Optional[int] = Field(default=None, ge=1, le=60)
    pomodoro_long_break_min: Optional[int] = Field(default=None, ge=1, le=120)
    sessions_before_long_break: Optional[int] = Field(default=None, ge=1, le=12)

    # Study Preferences
    daily_study_target_hours: Optional[float] = Field(default=None, ge=0.5, le=24)
    preferred_study_start: Optional[str] = None
    preferred_study_end: Optional[str] = None

    # Notifications
    study_reminders: Optional[bool] = None
    assignment_reminders: Optional[bool] = None
    exam_reminders: Optional[bool] = None
    break_reminders: Optional[bool] = None
    motivational_notifications: Optional[bool] = None

    # AI Preferences
    ai_personalization: Optional[bool] = None


class SettingsRead(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int

    theme: str
    accent_color: str
    font_size: str

    pomodoro_work_min: int
    pomodoro_short_break_min: int
    pomodoro_long_break_min: int
    sessions_before_long_break: int

    daily_study_target_hours: float
    preferred_study_start: Optional[str]
    preferred_study_end: Optional[str]

    study_reminders: bool
    assignment_reminders: bool
    exam_reminders: bool
    break_reminders: bool
    motivational_notifications: bool

    ai_personalization: bool

    created_at: datetime
    updated_at: datetime