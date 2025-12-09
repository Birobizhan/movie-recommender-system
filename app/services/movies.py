from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.movie import Movie
from app.repositories.movies import MovieRepository
from app.schemas.movie import MovieCreate


class MovieService:
    def __init__(self, db: Session):
        self.db = db
        self.movie_repo = MovieRepository(db)

    def get_movies(
        self,
        *,
        skip: int = 0,
        limit: int = 250,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        min_rating: Optional[float] = None,
        sort_by: Optional[str] = None,
        q: Optional[str] = None,
    ) -> List[Movie]:
        return self.movie_repo.list_movies(
            skip=skip,
            limit=limit,
            genre=genre,
            year=year,
            min_rating=min_rating,
            sort_by=sort_by,
            search_q=q,
        )

    def get_top_movies(
        self,
        *,
        skip: int = 0,
        limit: int = 250,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        min_rating: Optional[float] = None,
        sort_by: Optional[str] = None,
        q: Optional[str] = None,
    ) -> List[Movie]:
        return self.movie_repo.list_movies(
            skip=skip,
            limit=limit,
            genre=genre,
            year=year,
            min_rating=min_rating,
            order_by_top=True,
            sort_by=sort_by,
            search_q=q,
        )

    def search(self, *, q: str, skip: int = 0, limit: int = 50) -> List[Movie]:
        return self.movie_repo.search_movies(q=q, skip=skip, limit=limit)

    def get_movie(self, movie_id: int) -> Movie | None:
        return self.movie_repo.get_movie(movie_id)

    def create_movie(self, movie_in: MovieCreate) -> Movie:
        existing = self.movie_repo.get_by_kp_id(movie_in.kp_id)
        if existing:
            raise ValueError("Movie with this Kinopoisk ID already exists")
        db_movie = Movie(**movie_in.model_dump())
        return self.movie_repo.create_movie(db_movie)

    def get_similar(self, movie_id: int, limit: int = 10) -> List[Movie]:
        movie = self.movie_repo.get_movie(movie_id)
        if not movie:
            return []
        return self.movie_repo.get_similar_movies(movie, limit=limit)
