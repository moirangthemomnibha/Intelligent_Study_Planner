"""Database models for planning."""

from datetime import date
from typing import Optional

from sqlmodel import SQLModel, Field


class PlanSettings(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    student_id: int = Field(
        foreign_key="student.id",
        index=True,
        unique=True
    )

    plan_start: date

    plan_days: int = Field(
        default=7,
        ge=1,
        le=30
    )

    daily_available_minutes: int = Field(
        default=180,
        ge=1
    )

    adaptive_scheduling: bool = Field(default=True)

    auto_reschedule_missed: bool = Field(default=True)

    auto_adjust_early_completion: bool = Field(default=True)

    enable_revision: bool = Field(default=True)

    revision_interval_days: int = Field(
        default=3,
        ge=1,
        le=30
    )

    buffer_minutes: int = Field(
        default=30,
        ge=0
    )