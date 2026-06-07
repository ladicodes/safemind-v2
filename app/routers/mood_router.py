from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.base import get_db
from app.models.mood import MoodCheckIn
from app.models.user import User
from app.schemas.mood_schema import MoodCreate, MoodResponse, MoodSummary

router = APIRouter()


@router.post("/", response_model=MoodResponse, status_code=201)
def create_mood(
    payload: MoodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MoodCheckIn:
    check_in = MoodCheckIn(user_id=current_user.id, **payload.model_dump())
    db.add(check_in)
    db.commit()
    db.refresh(check_in)
    return check_in


@router.get("/", response_model=list[MoodResponse])
def mood_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MoodCheckIn]:
    return (
        db.query(MoodCheckIn)
        .filter(MoodCheckIn.user_id == current_user.id)
        .order_by(MoodCheckIn.created_at.desc(), MoodCheckIn.id.desc())
        .limit(min(max(limit, 1), 100))
        .all()
    )


@router.get("/summary", response_model=MoodSummary)
def mood_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MoodSummary:
    entries = (
        db.query(MoodCheckIn)
        .filter(MoodCheckIn.user_id == current_user.id)
        .order_by(MoodCheckIn.created_at.asc(), MoodCheckIn.id.asc())
        .all()
    )
    if not entries:
        return MoodSummary(
            total_check_ins=0, most_common_mood=None, recent_mood_trend="not enough data"
        )

    common = Counter(item.mood for item in entries).most_common(1)[0][0]
    recent = entries[-3:]
    if len(recent) < 2:
        trend = "not enough data"
    else:
        change = recent[-1].intensity - recent[0].intensity
        trend = "increasing" if change > 0 else "decreasing" if change < 0 else "steady"
    return MoodSummary(
        total_check_ins=len(entries), most_common_mood=common, recent_mood_trend=trend
    )
