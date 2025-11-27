from datetime import date
from typing import Optional
from app.database import Base
from sqlalchemy import (
    String, Text, Date, JSON,
    Table, Column, Integer, ForeignKey)
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
    english_title: Mapped[str] = mapped_column(String, nullable=True)

    kp_rating: Mapped[float] = mapped_column(nullable=True, default=0.0)
    imdb_rating: Mapped[float] = mapped_column(nullable=True, default=0.0)
    critics_rating: Mapped[float] = mapped_column(nullable=True, default=0.0)
    site_rating: Mapped[float] = mapped_column(nullable=True, default=0.0)
    fees_world: Mapped[str] = mapped_column(nullable=True)
    sum_votes: Mapped[int] = mapped_column(nullable=True)
    poster_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    movie_length: Mapped[int] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    world_premiere: Mapped[date] = mapped_column(Date, nullable=True)
    budget: Mapped[str] = mapped_column(nullable=True)
    year_release: Mapped[int] = mapped_column(nullable=True)
    age_rating: Mapped[int] = mapped_column(nullable=True)
    genres: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    countries: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    persons: Mapped[list[list]] = mapped_column(JSON, nullable=True)
    director: Mapped[list] = mapped_column(JSON, nullable=True)
    combined_rating: Mapped[float] = mapped_column(nullable=True)
    # similarMovies: Mapped[list["Movie"]] = relationship(
    #     secondary=movie_similarities,
    #     primaryjoin=id == movie_similarities.c.movie_id,
    #     secondaryjoin=id == movie_similarities.c.similar_movie_id,
    #     backref="is_similar_to"
    # )
    reviews = relationship("Review", back_populates="movie")
