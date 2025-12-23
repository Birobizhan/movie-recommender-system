from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, TEXT

from app.models.movie import Movie


class MovieRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_movies(
            self,
            *,
            skip: int = 0,
            limit: int = 250,
            genre: Optional[str] = None,
            year: Optional[int] = None,
            min_rating: Optional[float] = None,
            order_by_top: bool = False,
            sort_by: Optional[str] = None,
            search_q: Optional[str] = None,
    ) -> List[Movie]:
        query = self.db.query(Movie)

        if genre:
            if hasattr(Movie, "genres"):
                query = query.filter(
                    func.lower(cast(Movie.genres, TEXT)).like(f"%{genre.lower()}%")
                )
            else:
                query = query.filter(Movie.genre.ilike(f"%{genre}%"))
        if year:
            query = query.filter(
                Movie.year_release == year if hasattr(Movie, "year_release") else Movie.year == year
            )
        if min_rating:
            rating_column = getattr(Movie, "combined_rating", getattr(Movie, "rating", None))
            if rating_column is not None:
                query = query.filter(rating_column >= min_rating)
        if search_q:
            query = query.filter(Movie.title.ilike(f"%{search_q}%"))

        query = query.filter(Movie.sum_votes >= 50_000)

        if order_by_top or sort_by:
            combined = getattr(Movie, "combined_rating", getattr(Movie, "rating", None))
            sum_votes = getattr(Movie, "sum_votes", None)
            year_col = getattr(Movie, "year_release", getattr(Movie, "year", None))
            title_col = getattr(Movie, "title", None)

            if sort_by == "year" and year_col is not None:
                query = query.order_by(year_col.desc())
            elif sort_by == "title" and title_col is not None:
                query = query.order_by(title_col.asc())
            elif sort_by == "votes" and sum_votes is not None:
                query = query.order_by(sum_votes.desc())
            else:
                if combined is not None:
                    query = query.order_by(combined.desc(), sum_votes.desc() if sum_votes is not None else None)

        return query.offset(skip).limit(limit).all()

    def search_movies(self, *, q: str, skip: int = 0, limit: int = 50) -> List[Movie]:
        return (
            self.db.query(Movie)
            .filter(Movie.title.contains(q))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_movie(self, movie_id: int) -> Optional[Movie]:
        return self.db.query(Movie).filter(Movie.id == movie_id).first()

    def create_movie(self, movie: Movie) -> Movie:
        self.db.add(movie)
        self.db.commit()
        self.db.refresh(movie)
        return movie

    def get_by_kp_id(self, kp_id: int) -> Optional[Movie]:
        return self.db.query(Movie).filter(Movie.kp_id == kp_id).first()

    def get_similar_movies(self, movie: Movie, limit: int = 10) -> List[Movie]:
        from app.models.movie import movie_similarities
        
        similar_ids = (
            self.db.query(movie_similarities.c.similar_movie_id)
            .filter(movie_similarities.c.movie_id == movie.id)
            .limit(limit)
            .all()
        )
        
        if similar_ids:
            ids = [row[0] for row in similar_ids]
            similar_movies = (
                self.db.query(Movie)
                .filter(Movie.id.in_(ids))
                .all()
            )
            id_to_movie = {m.id: m for m in similar_movies}
            return [id_to_movie[id] for id in ids if id in id_to_movie]
        
        if movie.genres:
            first_genre = movie.genres[0] if isinstance(movie.genres, list) else str(movie.genres).split(",")[0].strip()
            query = self.db.query(Movie).filter(
                Movie.genres.contains([first_genre]) if hasattr(Movie, "genres") else Movie.genre.contains(first_genre),
                Movie.id != movie.id,
            )
        else:
            query = self.db.query(Movie).filter(Movie.id != movie.id)

        rating_column = getattr(Movie, "combined_rating", getattr(Movie, "rating", None))
        if rating_column is not None:
            query = query.order_by(rating_column.desc())

        return query.limit(limit).all()
