from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.review import Review


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, review_id: int) -> Optional[Review]:
        return self.db.query(Review).filter(Review.id == review_id).first()

    def get_for_movie(self, movie_id: int, skip: int = 0, limit: int = 50) -> List[Review]:
        return (
            self.db.query(Review)
            .filter(Review.movie_id == movie_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_for_user(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Review]:
        return (
            self.db.query(Review)
            .filter(Review.author_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user_movie_review(self, user_id: int, movie_id: int) -> Optional[Review]:
        return (
            self.db.query(Review)
            .filter(Review.author_id == user_id, Review.movie_id == movie_id)
            .first()
        )

    def create_review(self, *, content: str, rating: float, author_id: int, movie_id: int) -> Review:
        review = Review(content=content, rating=rating, author_id=author_id, movie_id=movie_id)
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def update_review(self, review: Review, *, content: Optional[str], rating: Optional[float]) -> Review:
        if content is not None:
            review.content = content
        if rating is not None:
            review.rating = rating
        self.db.commit()
        self.db.refresh(review)
        return review

    def delete_review(self, review: Review) -> None:
        self.db.delete(review)
        self.db.commit()
