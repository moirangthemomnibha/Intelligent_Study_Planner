from pydantic import BaseModel, Field

class RecommendationRequest(BaseModel):
    student_id: int
    question: str | None = None

class RecommendationResponse(BaseModel):
    recommendation: str
    reasons: list[str] = Field(default_factory=list)
    confidence_note: str = "Suggestions are estimates, not guarantees."
