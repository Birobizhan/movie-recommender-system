from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.schemas.movie import MovieResponse, MovieCreate, MovieRecommendationRequest
from app.services import MovieService

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
    service = MovieService(db)
    return service.get_movies(
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
    current_user: User | None = Depends(deps.get_optional_user)
):
    service = MovieService(db)
    return service.get_top_movies(
        skip=skip,
        limit=limit,
        genre=genre,
        year=year,
        min_rating=min_rating,
        sort_by=sort_by,
        q=q,
        current_user=current_user
    )


@router.post("/", response_model=MovieResponse, status_code=201)
def create_movie(
    movie: MovieCreate,
    current_user: User = Depends(deps.get_current_admin),  # Только админ может создавать фильмы
    db: Session = Depends(deps.get_db),
):
    try:
        service = MovieService(db)
        return service.create_movie(movie)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/search", response_model=List[MovieResponse])
def search_movies(
    q: str = Query(..., min_length=1),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(deps.get_db),
    current_user: User | None = Depends(deps.get_optional_user),
):
    service = MovieService(db)
    return service.search(q=q, skip=skip, limit=limit, current_user=current_user)


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(
    movie_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User | None = Depends(deps.get_optional_user),
):
    service = MovieService(db)
    movie = service.get_movie(movie_id, current_user=current_user)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.get("/{movie_id}/similar", response_model=List[MovieResponse])
def get_similar_movies(movie_id: int, limit: int = 10, db: Session = Depends(deps.get_db)):
    service = MovieService(db)
    similar = service.get_similar(movie_id, limit=limit)
    # Возвращаем пустой список, если похожих фильмов нет
    return similar or []


@router.post("/recommend", response_model=List[MovieResponse])
def recommend_movies(
    request: MovieRecommendationRequest,
    db: Session = Depends(deps.get_db),
):
    """
    Рекомендует фильмы на основе ответов пользователя из бота вопрос-ответ.
    """
    service = MovieService(db)
    movies = service.recommend_movies(
        main_genre=request.main_genre,
        subgenre=request.subgenre,
        subgenre_detail=request.subgenre_detail,
        time_period=request.time_period,
        limit=request.limit,
    )
    return movies

