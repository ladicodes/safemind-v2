from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    """Dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        if settings.DATABASE_URL.startswith("sqlite"):
            _migrate_legacy_sqlite()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


def _migrate_legacy_sqlite():
    """Apply additive compatibility changes for the original demo database."""
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    existing = {column["name"] for column in inspector.get_columns("users")}
    additions = {
        "password_hash": "VARCHAR",
        "is_active": "BOOLEAN NOT NULL DEFAULT 1",
        "updated_at": "DATETIME",
    }
    with engine.begin() as connection:
        for column, definition in additions.items():
            if column not in existing:
                connection.execute(
                    text(f"ALTER TABLE users ADD COLUMN {column} {definition}")
                )
        connection.execute(
            text("UPDATE users SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP)")
        )
        connection.execute(
            text(
                "UPDATE users SET updated_at = COALESCE(updated_at, created_at, CURRENT_TIMESTAMP)"
            )
        )
