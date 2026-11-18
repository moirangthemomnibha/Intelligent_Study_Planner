from pydantic import BaseModel, Field


class TopicCreate(BaseModel):
    subject_id: int = Field(gt=0)
    name: str = Field(min_length=2, max_length=150)
    estimated_minutes: int = Field(default=60, ge=0)
    difficulty: int = Field(default=3, ge=1, le=5)
    confidence: int = Field(default=3, ge=1, le=5)


class TopicRead(TopicCreate):
    id: int
    completion_percent: float = Field(ge=0, le=100)
    priority: int