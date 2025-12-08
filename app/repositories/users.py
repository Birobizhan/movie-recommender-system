from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User


def get_by_email(db: Session, email: str) -> Optional[User]:
    return (
        db.query(User)
        .filter(func.lower(User.email) == func.lower(email))
        .first()
    )


def get_by_username(db: Session, username: str) -> Optional[User]:
    return (
        db.query(User)
        .filter(func.lower(User.username) == func.lower(username))
        .first()
    )


def create_user(db: Session, *, email: str, username: str, hashed_password: str) -> User:
    user = User(email=email, username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()
