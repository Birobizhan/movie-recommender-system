from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.movie import MovieResponse, MovieCreate
from app.services import movies as movie_service

router = APIRouter(tags=["Movies"])


@router.get("/", response_model=List[MovieResponse])
def get_movies(
    skip: int = 0,
    limit: int = 250,
    genre: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    min_rating: Optional[float] = Query(None),
    sort_by: Optional[str] = Query(None, description="rating|year|title|votes"),
    q: Optional[str] = Query(None, description="поиск по названию"),
    db: Session = Depends(deps.get_db),
):
    return movie_service.get_movies(
        db,
        skip=skip,
        limit=limit,
        genre=genre,
        year=year,
        min_rating=min_rating,
        sort_by=sort_by,
        q=q,
    )


@router.get("/top", response_model=List[MovieResponse])
def get_top_250_movies(
    skip: int = 0,
    limit: int = 250,
    genre: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    min_rating: Optional[float] = Query(None),
    sort_by: Optional[str] = Query("rating", description="rating|year|title|votes"),
    q: Optional[str] = Query(None, description="поиск по названию"),
    db: Session = Depends(deps.get_db),
):
    return movie_service.get_top_movies(
        db,
        skip=skip,
        limit=limit,
        genre=genre,
        year=year,
        min_rating=min_rating,
        sort_by=sort_by,
        q=q,
    )


@router.post("/", response_model=MovieResponse, status_code=201)
def create_movie(movie: MovieCreate, db: Session = Depends(deps.get_db)):
    try:
        return movie_service.create_movie(db, movie)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/search", response_model=List[MovieResponse])
def search_movies(
    q: str = Query(..., min_length=1),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(deps.get_db),
):
    return movie_service.search(db, q=q, skip=skip, limit=limit)


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(deps.get_db)):
    movie = movie_service.get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.get("/{movie_id}/similar", response_model=List[MovieResponse])
def get_similar_movies(movie_id: int, limit: int = 10, db: Session = Depends(deps.get_db)):
    similar = movie_service.get_similar(db, movie_id, limit=limit)
    if similar is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return similar
