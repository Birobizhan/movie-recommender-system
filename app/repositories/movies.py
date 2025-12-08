from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.movie import Movie


def list_movies(
    db: Session,
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
    query = db.query(Movie)

    if genre:
        query = query.filter(
            Movie.genres.contains([genre]) if hasattr(Movie, "genres") else Movie.genre.contains(genre)
        )
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
            # default or sort_by == "rating"
            if combined is not None:
                query = query.order_by(combined.desc(), sum_votes.desc() if sum_votes is not None else None)

    return query.offset(skip).limit(limit).all()


def search_movies(db: Session, *, q: str, skip: int = 0, limit: int = 50) -> List[Movie]:
    return (
        db.query(Movie)
        .filter(Movie.title.contains(q))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_movie(db: Session, movie_id: int) -> Optional[Movie]:
    return db.query(Movie).filter(Movie.id == movie_id).first()


def create_movie(db: Session, movie: Movie) -> Movie:
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


def get_by_kp_id(db: Session, kp_id: int) -> Optional[Movie]:
    return db.query(Movie).filter(Movie.kp_id == kp_id).first()


def get_similar_movies(db: Session, movie: Movie, limit: int = 10) -> List[Movie]:
    if movie.genres:
        # take first genre string
        first_genre = movie.genres[0] if isinstance(movie.genres, list) else str(movie.genres).split(",")[0].strip()
        query = db.query(Movie).filter(
            Movie.genres.contains([first_genre]) if hasattr(Movie, "genres") else Movie.genre.contains(first_genre),
            Movie.id != movie.id,
        )
    else:
        query = db.query(Movie).filter(Movie.id != movie.id)

    rating_column = getattr(Movie, "combined_rating", getattr(Movie, "rating", None))
    if rating_column is not None:
        query = query.order_by(rating_column.desc())

    return query.limit(limit).all()
