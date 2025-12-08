from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.movie import Movie
from app.models.review import Review
from app.models.user import User
from app.schemas.movie import MovieResponse, MovieCreate
from app.schemas.review import ReviewResponse
from app.schemas.user import UserResponse

router = APIRouter()

@router.get("/", response_model=List[MovieResponse])
def get_movies(
    skip: int = 0,
    limit: int = 100,
    genre: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    min_rating: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Movie)
    
    if genre:
        query = query.filter(Movie.genre.contains(genre))
    if year:
        query = query.filter(Movie.year == year)
    if min_rating:
        query = query.filter(Movie.rating >= min_rating)
    
    movies = query.offset(skip).limit(limit).all()
    return movies


@router.get("/top", response_model=List[MovieResponse])
def get_top_250_movies(
        skip: int = 0,
        limit: int = 100,
        genre: Optional[str] = Query(None),
        year: Optional[int] = Query(None),
        min_rating: Optional[float] = Query(None),
        db: Session = Depends(get_db)
):
    query = db.query(Movie)

    if genre:
        query = query.filter(Movie.genre.contains(genre))
    if year:
        query = query.filter(Movie.year == year)
    if min_rating:
        query = query.filter(Movie.rating >= min_rating)
    query = query.order_by(Movie.combined_rating.desc(), Movie.sum_votes.desc())
    movies = query.offset(skip).limit(limit).all()
    return movies


@router.post("/", response_model=MovieResponse, status_code=201)
def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    """
    Создает новый фильм в базе данных.
    Проверяет, не существует ли фильм с таким же kp_id.
    """

    db_movie = db.query(Movie).filter(Movie.kp_id == movie.kp_id).first()
    if db_movie:
        raise HTTPException(
            status_code=400,
            detail="Movie with this Kinopoisk ID already exists"
        )

    db_movie = Movie(**movie.model_dump())

    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)

    return db_movie


@router.get("/search", response_model=List[MovieResponse])
def search_movies(
    q: str = Query(..., min_length=1),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    movies = db.query(Movie).filter(
        Movie.title.contains(q)
    ).offset(skip).limit(limit).all()
    return movies

@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@router.get("/{movie_id}/reviews", response_model=List[ReviewResponse])
def get_movie_reviews(movie_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.movie_id == movie_id).all()
    return reviews

@router.get("/{movie_id}/similar", response_model=List[MovieResponse])
def get_similar_movies(movie_id: int, limit: int = 10, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    if movie.genre:
        first_genre = movie.genre.split(',')[0].strip()
        similar_movies = db.query(Movie).filter(
            Movie.genre.contains(first_genre),
            Movie.id != movie_id
        ).order_by(
            Movie.rating.desc()
        ).limit(limit).all()
    else:
        similar_movies = db.query(Movie).filter(
            Movie.id != movie_id
        ).order_by(
            Movie.rating.desc()
        ).limit(limit).all()
    
    return similar_movies