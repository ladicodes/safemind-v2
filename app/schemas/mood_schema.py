from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MoodCreate(BaseModel):
    mood: str = Field(..., min_length=1, max_length=50)
    intensity: int = Field(default=5, ge=1, le=10)
    note: str | None = Field(default=None, max_length=2000)

    @field_validator("mood")
    @classmethod
    def normalize_mood(cls, value: str) -> str:
        value = value.strip().lower()
        if not value:
            raise ValueError("must not be blank")
        return value


class MoodResponse(MoodCreate):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MoodSummary(BaseModel):
    total_check_ins: int
    most_common_mood: str | None
    recent_mood_trend: str
