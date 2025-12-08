from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.movie import Movie
from app.models.review import Review
from app.schemas.review import ReviewResponse, ReviewCreate, ReviewUpdate

router = APIRouter()

@router.post("/", response_model=ReviewResponse)
def create_review(
    review: ReviewCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    movie = db.query(Movie).filter(Movie.id == review.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    user = db.query(User).filter(User.username == current_user).first()
    
    existing_review = db.query(Review).filter(
        Review.author_id == user.id,
        Review.movie_id == review.movie_id
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this movie"
        )
    
    db_review = Review(
        content=review.content,
        rating=review.rating,
        author_id=user.id,
        movie_id=review.movie_id
    )
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == current_user).first()
    db_review = db.query(Review).filter(Review.id == review_id).first()
    
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if db_review.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if review_update.content is not None:
        db_review.content = review_update.content
    if review_update.rating is not None:
        db_review.rating = review_update.rating
    
    db.commit()
    db.refresh(db_review)
    return db_review

@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == current_user).first()
    db_review = db.query(Review).filter(Review.id == review_id).first()
    
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if db_review.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db.delete(db_review)
    db.commit()
    return {"message": "Review deleted successfully"}

@router.get("/movie/{movie_id}", response_model=List[ReviewResponse])
def get_movie_reviews(movie_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(
        Review.movie_id == movie_id
    ).offset(skip).limit(limit).all()
    return reviews

@router.get("/user/{user_id}", response_model=List[ReviewResponse])
def get_user_reviews(user_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(
        Review.author_id == user_id
    ).offset(skip).limit(limit).all()
    return reviews