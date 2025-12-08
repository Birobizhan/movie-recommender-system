from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.movie import Movie
from app.repositories import movies as movie_repo
from app.schemas.movie import MovieCreate


def get_movies(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 250,
    genre: Optional[str] = None,
    year: Optional[int] = None,
    min_rating: Optional[float] = None,
    sort_by: Optional[str] = None,
    q: Optional[str] = None,
) -> List[Movie]:
    return movie_repo.list_movies(
        db,
        skip=skip,
        limit=limit,
        genre=genre,
        year=year,
        min_rating=min_rating,
        sort_by=sort_by,
        search_q=q,
    )


def get_top_movies(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 250,
    genre: Optional[str] = None,
    year: Optional[int] = None,
    min_rating: Optional[float] = None,
    sort_by: Optional[str] = None,
    q: Optional[str] = None,
) -> List[Movie]:
    return movie_repo.list_movies(
        db,
        skip=skip,
        limit=limit,
        genre=genre,
        year=year,
        min_rating=min_rating,
        order_by_top=True,
        sort_by=sort_by,
        search_q=q,
    )


def search(db: Session, *, q: str, skip: int = 0, limit: int = 50) -> List[Movie]:
    return movie_repo.search_movies(db, q=q, skip=skip, limit=limit)


def get_movie(db: Session, movie_id: int) -> Movie | None:
    return movie_repo.get_movie(db, movie_id)


def create_movie(db: Session, movie_in: MovieCreate) -> Movie:
    existing = movie_repo.get_by_kp_id(db, movie_in.kp_id)
    if existing:
        raise ValueError("Movie with this Kinopoisk ID already exists")
    db_movie = Movie(**movie_in.model_dump())
    return movie_repo.create_movie(db, db_movie)


def get_similar(db: Session, movie_id: int, limit: int = 10) -> List[Movie]:
    movie = movie_repo.get_movie(db, movie_id)
    if not movie:
        return []
    return movie_repo.get_similar_movies(db, movie, limit=limit)
