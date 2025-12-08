import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Text, DateTime, Boolean,
    Table, Column, Integer, ForeignKey)
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from app.db.base import Base

list_movie_association = Table(
    'list_movie_association',
    Base.metadata,
    Column('list_id', Integer, ForeignKey('movie_lists.id'), primary_key=True),
    Column('movie_id', Integer, ForeignKey('movies.id'), primary_key=True)
)


class MovieList(Base):
    __tablename__ = "movie_lists"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now()
    )

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship(back_populates="lists")

    movies: Mapped[List["Movie"]] = relationship(
        secondary=list_movie_association
    )
