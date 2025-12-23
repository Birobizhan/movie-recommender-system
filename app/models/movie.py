from datetime import date
from typing import Optional, List
from app.db.base import Base
from sqlalchemy import (
    String, Text, Date,
    Table, Column, Integer, ForeignKey
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship, mapped_column, Mapped

movie_similarities = Table(
    "movie_similarities",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id"), primary_key=True),
    Column("similar_movie_id", Integer, ForeignKey("movies.id"), primary_key=True)
)


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    kp_id: Mapped[int] = mapped_column(index=True, unique=True)
    title: Mapped[str] = mapped_column(index=True)
    english_title: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    kp_rating: Mapped[Optional[float]] = mapped_column(default=0.0)
    imdb_rating: Mapped[Optional[float]] = mapped_column(default=0.0)
    critics_rating: Mapped[Optional[float]] = mapped_column(default=0.0)
    site_rating: Mapped[Optional[float]] = mapped_column(default=0.0)
    fees_world: Mapped[Optional[str]] = mapped_column(nullable=True)
    sum_votes: Mapped[Optional[int]] = mapped_column(nullable=True)
    poster_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    movie_length: Mapped[Optional[int]] = mapped_column(nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    world_premiere: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    budget: Mapped[Optional[str]] = mapped_column(nullable=True)
    year_release: Mapped[Optional[int]] = mapped_column(nullable=True)
    age_rating: Mapped[Optional[int]] = mapped_column(nullable=True)

    genres: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    countries: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

    persons: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

    director: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    combined_rating: Mapped[Optional[float]] = mapped_column(nullable=True)

    reviews = relationship("Review", back_populates="movie")