from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(func.lower(User.email) == func.lower(email))
            .first()
        )

    def get_by_username(self, username: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(func.lower(User.username) == func.lower(username))
            .first()
        )

    def create_user(self, *, email: str, username: str, hashed_password: str, role: str = "user") -> User:
        from app.models.user import UserRole
        user_role = UserRole(role) if isinstance(role, str) else role
        user = User(email=email, username=username, hashed_password=hashed_password, role=user_role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def update_user(
        self,
        user: User,
        *,
        email: Optional[str] = None,
        username: Optional[str] = None,
    ) -> User:
        if email is not None:
            # Проверяем, что email не занят другим пользователем
            existing = self.get_by_email(email)
            if existing and existing.id != user.id:
                raise ValueError("Email already registered")
            user.email = email
        if username is not None:
            # Проверяем, что username не занят другим пользователем
            existing = self.get_by_username(username)
            if existing and existing.id != user.id:
                raise ValueError("Username already taken")
            user.username = username
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user: User, new_hashed_password: str) -> User:
        user.hashed_password = new_hashed_password
        self.db.commit()
        self.db.refresh(user)
        return user
