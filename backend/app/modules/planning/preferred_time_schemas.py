from pydantic import BaseModel, Field


class PreferredStudyTimeCreate(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    start_time: str
    end_time: str


class PreferredStudyTimeRead(PreferredStudyTimeCreate):
    id: int
    student_id: int