from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.schemas.movie import MovieResponse

class MovieListBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_public: bool = True

class MovieListCreate(MovieListBase):
    movie_ids: Optional[List[int]] = None

class MovieListUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None

class MovieListResponse(MovieListBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    movie_count: int
    is_public: bool
    movies: Optional[List[MovieResponse]] = None
    
    class Config:
        from_attributes = True

class MovieListAddRemoveMovies(BaseModel):
    movie_ids: List[int]