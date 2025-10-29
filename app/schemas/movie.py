from pydantic import BaseModel
from typing import Optional

class MovieBase(BaseModel):
    title: str
    year: int
    genre: str
    description: Optional[str] = None
    rating: Optional[float] = None
    poster_url: Optional[str] = None

class MovieCreate(MovieBase):
    pass

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