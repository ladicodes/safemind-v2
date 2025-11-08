from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    picture = Column(String)
    google_id = Column(String, unique=True)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
