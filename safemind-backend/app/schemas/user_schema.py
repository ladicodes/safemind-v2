from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    name: str | None = None
    picture: str | None = None


class UserCreate(UserBase):
    google_id: str


class UserOut(UserBase):
    id: int
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)
