from sqlalchemy.orm import Session

from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.models.user import User
from app.repositories import users as user_repo
from app.repositories import lists as list_repo
from app.schemas.user import UserCreate, UserLogin


def register_user(db: Session, user_in: UserCreate) -> User:
    if user_repo.get_by_email(db, user_in.email):
        raise ValueError("Email already registered")
    if user_repo.get_by_username(db, user_in.username):
        raise ValueError("Username already taken")

    hashed_pwd = hash_password(user_in.password)
    user = user_repo.create_user(db, email=user_in.email, username=user_in.username, hashed_password=hashed_pwd)

    # Создаем базовые списки
    default_lists = ["Просмотренные", "Буду смотреть", "Любимые"]
    for title in default_lists:
        try:
            list_repo.create_list(db, title=title, description=None, owner_id=user.id)
        except Exception:
            db.rollback()
    return user


def login_user(db: Session, user_in: UserLogin) -> dict:
    email = user_in.email.strip()
    db_user = user_repo.get_by_email(db, email)
    if not db_user or not verify_password(user_in.password, db_user.hashed_password):
        raise ValueError("Incorrect email or password")

    access_token = create_access_token(data={"sub": db_user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user,
    }


def get_user_profile(db: Session, user_id: int) -> User | None:
    return user_repo.get_by_id(db, user_id)
