from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.base import get_db
from app.models.journal import Journal
from app.models.mood import MoodCheckIn
from app.models.user import User
from app.services.reflection_service import create_reflection

router = APIRouter()


class ReflectionRequest(BaseModel):
    source_type: Literal["journal", "mood"]
    source_id: int


class ReflectionResponse(BaseModel):
    reflection: str
    crisis_detected: bool
    source: str
    disclaimer: str


@router.post("/", response_model=ReflectionResponse)
def reflect(
    payload: ReflectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if payload.source_type == "journal":
        item = (
            db.query(Journal)
            .filter(Journal.id == payload.source_id, Journal.user_id == current_user.id)
            .first()
        )
        text = item.content if item else None
        mood = item.mood if item else None
    else:
        item = (
            db.query(MoodCheckIn)
            .filter(
                MoodCheckIn.id == payload.source_id,
                MoodCheckIn.user_id == current_user.id,
            )
            .first()
        )
        text = (item.note or f"I checked in feeling {item.mood}.") if item else None
        mood = item.mood if item else None

    if not item or not text:
        raise HTTPException(status_code=404, detail="Reflection source not found")
    return create_reflection(text, mood)
