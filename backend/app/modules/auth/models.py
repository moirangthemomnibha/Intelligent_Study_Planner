from typing import Optional
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    email: str = Field(
        index=True,
        unique=True,
        max_length=255
    )

    hashed_password: str

    is_verified: bool = Field(default=False)

    is_active: bool = Field(default=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class EmailOTP(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    email: str = Field(index=True)

    otp_hash: str

    expires_at: datetime

    is_used: bool = Field(default=False)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )