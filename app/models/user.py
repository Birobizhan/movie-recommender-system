import datetime
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now()
    )

    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="author")
    lists: Mapped[list["MovieList"]] = relationship("MovieList", back_populates="owner")
