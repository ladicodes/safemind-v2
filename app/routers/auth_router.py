from typing import Any
from urllib.parse import urlencode

import requests
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import id_token as google_id_token
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.db.base import get_db
from app.models.user import User
from app.schemas.user_schema import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)

router = APIRouter()
AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"


class GoogleCredentialPayload(BaseModel):
    token: str


def token_response(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token({"sub": str(user.id)}),
        user=UserResponse.model_validate(user),
    )


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    user = User(
        email=email,
        name=payload.name.strip(),
        picture=payload.picture,
        password_hash=hash_password(payload.password),
        is_verified=True,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if (
        not user
        or not user.password_hash
        or not verify_password(payload.password, user.password_hash)
    ):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    return token_response(user)


@router.get("/me", response_model=UserResponse)
def read_profile(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/logout")
def logout() -> dict:
    return {"message": "Logged out. Discard the bearer token on the client."}


def _google_config() -> None:
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="Google OAuth is not configured")


def _upsert_google_user(db: Session, profile: dict[str, Any]) -> User:
    email = profile.get("email")
    google_id = profile.get("sub")
    if not email or not google_id:
        raise HTTPException(status_code=400, detail="Google profile is incomplete")
    user = db.query(User).filter(User.email == email.lower()).first()
    if user is None:
        user = User(
            email=email.lower(),
            name=profile.get("name") or email.split("@")[0],
            picture=profile.get("picture"),
            google_id=google_id,
            is_verified=True,
            is_active=True,
        )
        db.add(user)
    else:
        user.google_id = user.google_id or google_id
        user.name = profile.get("name") or user.name
        user.picture = profile.get("picture") or user.picture
        user.is_verified = True
    db.commit()
    db.refresh(user)
    return user


def _verify_google_token(token: str) -> dict[str, Any]:
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google OAuth is not configured")
    try:
        return google_id_token.verify_oauth2_token(
            token, GoogleRequest(), settings.GOOGLE_CLIENT_ID, clock_skew_in_seconds=10
        )
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid Google credential") from exc


@router.get("/google/login", response_class=RedirectResponse)
def google_login() -> RedirectResponse:
    _google_config()
    query = urlencode(
        {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "online",
            "prompt": "select_account",
        }
    )
    return RedirectResponse(f"{AUTHORIZATION_ENDPOINT}?{query}")


@router.get("/google/callback", response_model=TokenResponse)
def google_callback(code: str, db: Session = Depends(get_db)) -> TokenResponse:
    _google_config()
    try:
        response = requests.post(
            TOKEN_ENDPOINT,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail="Google token exchange failed") from exc
    profile = _verify_google_token(response.json().get("id_token", ""))
    return token_response(_upsert_google_user(db, profile))


@router.post("/google/verify", response_model=TokenResponse)
def verify_google_credential(
    payload: GoogleCredentialPayload, db: Session = Depends(get_db)
) -> TokenResponse:
    return token_response(_upsert_google_user(db, _verify_google_token(payload.token)))
