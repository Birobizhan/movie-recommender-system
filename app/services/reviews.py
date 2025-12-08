from sqlalchemy.orm import Session

from app.models.review import Review
from app.repositories import reviews as review_repo
from app.repositories import users as user_repo
from app.repositories import movies as movie_repo
from app.schemas.review import ReviewCreate, ReviewUpdate


def create_review(db: Session, review_in: ReviewCreate, current_username: str) -> Review:
    user = user_repo.get_by_username(db, current_username)
    if not user:
        raise ValueError("User not found")

    movie = movie_repo.get_movie(db, review_in.movie_id)
    if not movie:
        raise LookupError("Movie not found")

    existing = review_repo.get_user_movie_review(db, user.id, review_in.movie_id)
    if existing:
        raise ValueError("You have already reviewed this movie")

    return review_repo.create_review(
        db,
        content=review_in.content,
        rating=review_in.rating,
        author_id=user.id,
        movie_id=review_in.movie_id,
    )


def update_review(db: Session, review_id: int, review_in: ReviewUpdate, current_username: str) -> Review:
    user = user_repo.get_by_username(db, current_username)
    review = review_repo.get_by_id(db, review_id)
    if not review:
        raise LookupError("Review not found")
    if not user or review.author_id != user.id:
        raise PermissionError("Not enough permissions")

    return review_repo.update_review(db, review, content=review_in.content, rating=review_in.rating)


def delete_review(db: Session, review_id: int, current_username: str) -> None:
    user = user_repo.get_by_username(db, current_username)
    review = review_repo.get_by_id(db, review_id)
    if not review:
        raise LookupError("Review not found")
    if not user or review.author_id != user.id:
        raise PermissionError("Not enough permissions")
    review_repo.delete_review(db, review)


def list_movie_reviews(db: Session, movie_id: int, skip: int = 0, limit: int = 50):
    return review_repo.get_for_movie(db, movie_id, skip=skip, limit=limit)


def list_user_reviews(db: Session, user_id: int, skip: int = 0, limit: int = 50):
    return review_repo.get_for_user(db, user_id, skip=skip, limit=limit)
