from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ReviewBase(BaseModel):
    content: Optional[str] = None
    rating: float = Field(..., ge=0, le=10, description="Rating from 0 to 10")


class ReviewCreate(ReviewBase):
    movie_id: int


class ReviewUpdate(BaseModel):
    content: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=10)


class ReviewResponse(ReviewBase):
    id: int
    author_id: int
    movie_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
