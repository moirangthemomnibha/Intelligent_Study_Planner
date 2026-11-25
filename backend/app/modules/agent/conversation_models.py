from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field


class AgentConversation(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    summary: str | None = None

    student_id: int = Field(index=True)

    title: str = Field(default="New Conversation")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class AgentMessage(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    conversation_id: int = Field(index=True)

    student_id: int = Field(index=True)

    role: str

    content: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )