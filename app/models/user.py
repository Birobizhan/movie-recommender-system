import datetime
from enum import Enum as PyEnum
from sqlalchemy import DateTime, Enum
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from app.db.base import Base


class UserRole(str, PyEnum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False),
        default=UserRole.USER,
        nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now()
    )

    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="author")
    lists: Mapped[list["MovieList"]] = relationship("MovieList", back_populates="owner")
    
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
