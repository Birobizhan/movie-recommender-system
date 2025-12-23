from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Any
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    username: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None


class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str


class UserProfile(UserResponse):
    reviews_count: int
    lists_count: int
    average_rating: Optional[float] = None


class UserProfileExtended(UserProfile):
    recent_watched_movies: list[Any] = []
    favorite_genres: list[dict[str, Any]] = []


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
