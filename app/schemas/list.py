from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.schemas.movie import MovieResponse

class MovieListBase(BaseModel):
    title: str
    description: Optional[str] = None

class MovieListCreate(MovieListBase):
    movie_ids: Optional[List[int]] = None

class MovieListUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class MovieListResponse(MovieListBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    movie_count: int
    movies: Optional[List[MovieResponse]] = None
    
    class Config:
        from_attributes = True

class MovieListAddRemoveMovies(BaseModel):
    movie_ids: List[int]