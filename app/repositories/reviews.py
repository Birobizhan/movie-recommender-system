from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.review import Review


def get_by_id(db: Session, review_id: int) -> Optional[Review]:
    return db.query(Review).filter(Review.id == review_id).first()


def get_for_movie(db: Session, movie_id: int, skip: int = 0, limit: int = 50) -> List[Review]:
    return (
        db.query(Review)
        .filter(Review.movie_id == movie_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[Review]:
    return (
        db.query(Review)
        .filter(Review.author_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_movie_review(db: Session, user_id: int, movie_id: int) -> Optional[Review]:
    return (
        db.query(Review)
        .filter(Review.author_id == user_id, Review.movie_id == movie_id)
        .first()
    )


def create_review(db: Session, *, content: str, rating: float, author_id: int, movie_id: int) -> Review:
    review = Review(content=content, rating=rating, author_id=author_id, movie_id=movie_id)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def update_review(db: Session, review: Review, *, content: Optional[str], rating: Optional[float]) -> Review:
    if content is not None:
        review.content = content
    if rating is not None:
        review.rating = rating
    db.commit()
    db.refresh(review)
    return review


def delete_review(db: Session, review: Review) -> None:
    db.delete(review)
    db.commit()
