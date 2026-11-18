from pydantic import BaseModel, Field

class SessionUpdate(BaseModel):
    status: str = Field(pattern="^(completed|missed|partial)$")
    actual_minutes: int | None = Field(default=None, ge=0)
    reflection: str | None = None
