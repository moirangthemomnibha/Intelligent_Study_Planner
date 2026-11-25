from typing import Optional
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field


class UserSettings(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    user_id: int = Field(
        foreign_key="user.id",
        unique=True,
        index=True
    )

    # Appearance
    theme: str = Field(default="system")
    accent_color: str = Field(default="#4F46E5")
    font_size: str = Field(default="medium")

    # Pomodoro Timer
    pomodoro_work_min: int = Field(default=25, ge=1, le=180)
    pomodoro_short_break_min: int = Field(default=5, ge=1, le=60)
    pomodoro_long_break_min: int = Field(default=15, ge=1, le=120)
    sessions_before_long_break: int = Field(default=4, ge=1, le=12)

    # Study Preferences
    daily_study_target_hours: float = Field(default=3.0, ge=0.5, le=24)
    preferred_study_start: Optional[str] = None
    preferred_study_end: Optional[str] = None

    # Notifications
    study_reminders: bool = Field(default=True)
    assignment_reminders: bool = Field(default=True)
    exam_reminders: bool = Field(default=True)
    break_reminders: bool = Field(default=True)
    motivational_notifications: bool = Field(default=False)

    # Privacy & AI Preferences
    ai_personalization: bool = Field(default=True)

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )