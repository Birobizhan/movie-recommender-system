from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, Any
class MovieBase(BaseModel):
    kp_id: int = Field(..., description="ID фильма из Кинопоиска")
    title: str = Field(..., description="Название фильма (Русское)")
    english_title: Optional[str] = None

    kp_rating: Optional[float] = 0.0
    imdb_rating: Optional[float] = 0.0
    critics_rating: Optional[float] = 0.0
    movie_length: Optional[int] = None
    year_release: Optional[int] = None
    age_rating: Optional[int] = None
    sum_votes: Optional[int] = 0

    # Строки
    fees_world: Optional[str] = None
    budget: Optional[str] = None
    poster_url: Optional[str] = None
    description: Optional[str] = None

    # Списки
    genres: Optional[list[str]] = None
    countries: Optional[list[str]] = None
    persons: Optional[list[str]] = None
    director: Optional[str] = None

    # Дата
    world_premiere: Optional[date] = None
    combined_rating: Optional[float] = 0.0

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    poster_url: Optional[str] = None

class MovieResponse(MovieBase):
    id: int
    
    class Config:
        from_attributes = True

class MovieSearchFilters(BaseModel):

    query: Optional[str] = None
    genre: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    rating_from: Optional[float] = None
    rating_to: Optional[float] = None


class MovieCreate(BaseModel):
    kp_id: int = Field(..., description="ID фильма из Кинопоиска")
    title: str = Field(..., description="Название фильма (Русское)")
    english_title: Optional[str] = None
    kp_rating: float = 0.0
    imdb_rating: float = 0.0
    critics_rating: float = 0.0
    movie_length: Optional[int] = None
    year_release: Optional[int] = None
    age_rating: Optional[int] = None
    sum_votes: Optional[int] = 0
    fees_world: Optional[str] = None
    budget: Optional[str] = None
    poster_url: Optional[str] = None
    description: Optional[str] = None
    genres: Optional[list[str]] = None
    countries: Optional[list[str]] = None
    persons: Optional[list[str]] = None
    director: Optional[list[str]] = None
    world_premiere: Optional[date] = None
    combined_rating: Optional[float] = 0.0


class MovieRecommendationRequest(BaseModel):
    main_genre: str = Field(..., description="Основной жанр")
    subgenre: str = Field(..., description="Поджанр")
    subgenre_detail: str = Field(..., description="Детализация поджанра")
    time_period: str = Field(..., description="Временной период")
    limit: int = Field(20, ge=1, le=50, description="Количество рекомендаций")