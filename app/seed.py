from app.core.security import hash_password
from app.db.base import SessionLocal, init_db
from app.models.journal import Journal
from app.models.mood import MoodCheckIn
from app.models.user import User

DEMO_EMAIL = "demo@safespace.app"
DEMO_PASSWORD = "DemoPass123!"


def seed_demo_data() -> None:
    init_db()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == DEMO_EMAIL).first()
        if user is None:
            user = User(
                email=DEMO_EMAIL,
                name="SafeSpace Demo",
                password_hash=hash_password(DEMO_PASSWORD),
                is_verified=True,
                is_active=True,
            )
            db.add(user)
            db.flush()

        if not db.query(Journal).filter(Journal.user_id == user.id).first():
            db.add_all(
                [
                    Journal(
                        user_id=user.id,
                        title="A calmer morning",
                        content="I slowed down before work and noticed that a short walk helped.",
                        mood="calm",
                    ),
                    Journal(
                        user_id=user.id,
                        title="One thing at a time",
                        content="The day felt busy, so I chose one small task instead of everything.",
                        mood="overwhelmed",
                    ),
                ]
            )

        if not db.query(MoodCheckIn).filter(MoodCheckIn.user_id == user.id).first():
            db.add_all(
                [
                    MoodCheckIn(user_id=user.id, mood="calm", intensity=7),
                    MoodCheckIn(user_id=user.id, mood="anxious", intensity=6),
                    MoodCheckIn(user_id=user.id, mood="hopeful", intensity=8),
                ]
            )
        db.commit()
        print(f"Demo data ready: {DEMO_EMAIL} / {DEMO_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
