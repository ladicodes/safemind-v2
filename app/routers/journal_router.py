from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.base import get_db
from app.models.journal import Journal
from app.models.user import User
from app.schemas.journal_schema import JournalCreate, JournalResponse, JournalUpdate

router = APIRouter()


def owned_journal(journal_id: int, user_id: int, db: Session) -> Journal:
    journal = (
        db.query(Journal)
        .filter(Journal.id == journal_id, Journal.user_id == user_id)
        .first()
    )
    if not journal:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return journal


@router.post("/", response_model=JournalResponse, status_code=status.HTTP_201_CREATED)
def create_journal(
    payload: JournalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Journal:
    journal = Journal(user_id=current_user.id, **payload.model_dump())
    db.add(journal)
    db.commit()
    db.refresh(journal)
    return journal


@router.get("/", response_model=list[JournalResponse])
def list_journals(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Journal]:
    return (
        db.query(Journal)
        .filter(Journal.user_id == current_user.id)
        .order_by(Journal.created_at.desc())
        .offset(max(skip, 0))
        .limit(min(max(limit, 1), 100))
        .all()
    )


@router.get("/{journal_id}", response_model=JournalResponse)
def get_journal(
    journal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Journal:
    return owned_journal(journal_id, current_user.id, db)


@router.patch("/{journal_id}", response_model=JournalResponse)
def update_journal(
    journal_id: int,
    payload: JournalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Journal:
    journal = owned_journal(journal_id, current_user.id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(journal, field, value.strip() if isinstance(value, str) else value)
    db.commit()
    db.refresh(journal)
    return journal


@router.delete("/{journal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journal(
    journal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    journal = owned_journal(journal_id, current_user.id, db)
    db.delete(journal)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
