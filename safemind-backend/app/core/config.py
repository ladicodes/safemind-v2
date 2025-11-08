from functools import lru_cache

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "sqlite:///./safemind.db"

    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REDIRECT_URI: AnyUrl | str = "http://localhost:8000/api/auth/google/callback"

    JWT_SECRET: str = Field(default="change-me")
    JWT_ALGORITHM: str = "HS256"


@lru_cache
def get_settings() -> "Settings":
    """Return a cached Settings instance."""
    return Settings()


settings = get_settings()
