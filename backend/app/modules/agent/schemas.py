from datetime import date
from pydantic import BaseModel, Field
from typing import Literal


class AgentRequest(BaseModel):
    student_id: int
    intent: str

    approval_mode: Literal[
        "suggest_only",
        "ask_before_changes"
    ] = "ask_before_changes"

    available_minutes_per_day: int = Field(default=180, gt=0)
    horizon_days: int = Field(default=7, ge=1, le=30)


class AgentProposal(BaseModel):
    summary: str
    actions: list[dict] = Field(default_factory=list)
    requires_confirmation: bool = False


class AgentConfirmRequest(BaseModel):
    student_id: int
    start_date: date
    horizon_days: int = Field(ge=1, le=30)
    available_minutes_per_day: int = Field(gt=0)
    generated_plan: list[dict]


class AgentChatRequest(BaseModel):
    student_id: int
    message: str = Field(min_length=1, max_length=10000)
    conversation_history: list[dict] = Field(default_factory=list)

class AgentChatResponse(BaseModel):
    success: bool
    response: str
    actions: list[dict] = Field(default_factory=list)