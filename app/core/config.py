import os
import tempfile
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def default_database_url() -> str:
    if os.getenv("VERCEL"):
        database_path = Path(tempfile.gettempdir()) / "safemind-vercel.db"
        return f"sqlite:///{database_path.as_posix()}"
    return "sqlite:///./safemind.db"


def default_auto_seed() -> bool:
    return bool(os.getenv("VERCEL"))


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    DATABASE_URL: str = Field(default_factory=default_database_url)
    AUTO_SEED_DEMO: bool = Field(default_factory=default_auto_seed)
    
    # JWT
    JWT_SECRET_KEY: str = Field(default="change-me-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"

    # Optional AI reflection provider. The app always has an offline fallback.
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-5-mini"
    
    # App settings
    APP_NAME: str = "SafeMind"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


settings = get_settings()
