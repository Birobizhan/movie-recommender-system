from sqlalchemy.orm import Session

from app.models.review import Review
from app.repositories.reviews import ReviewRepository
from app.repositories.users import UserRepository
from app.repositories.movies import MovieRepository
from app.schemas.review import ReviewCreate, ReviewUpdate


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.review_repo = ReviewRepository(db)
        self.user_repo = UserRepository(db)
        self.movie_repo = MovieRepository(db)

    def create_review(self, review_in: ReviewCreate, current_user) -> Review:
        from app.models.user import User
        if not isinstance(current_user, User):
            raise ValueError("Invalid user object")

        movie = self.movie_repo.get_movie(review_in.movie_id)
        if not movie:
            raise LookupError("Movie not found")

        existing = self.review_repo.get_user_movie_review(current_user.id, review_in.movie_id)
        if existing:
            raise ValueError("You have already reviewed this movie")

        return self.review_repo.create_review(
            content=review_in.content,
            rating=review_in.rating,
            author_id=current_user.id,
            movie_id=review_in.movie_id,
        )

    def update_review(self, review_id: int, review_in: ReviewUpdate, current_user) -> Review:
        from app.models.user import User
        if not isinstance(current_user, User):
            raise ValueError("Invalid user object")
            
        review = self.review_repo.get_by_id(review_id)
        if not review:
            raise LookupError("Review not found")
        # Пользователь может редактировать только свои отзывы, админ может редактировать любые
        if review.author_id != current_user.id and not current_user.is_admin():
            raise PermissionError("Not enough permissions")

        return self.review_repo.update_review(review, content=review_in.content, rating=review_in.rating)

    def delete_review(self, review_id: int, current_user) -> None:
        from app.models.user import User
        if not isinstance(current_user, User):
            raise ValueError("Invalid user object")
            
        review = self.review_repo.get_by_id(review_id)
        if not review:
            raise LookupError("Review not found")
        # Пользователь может удалять только свои отзывы, админ может удалять любые
        if review.author_id != current_user.id and not current_user.is_admin():
            raise PermissionError("Not enough permissions")
        self.review_repo.delete_review(review)

    def list_movie_reviews(self, movie_id: int, skip: int = 0, limit: int = 50):
        return self.review_repo.get_for_movie(movie_id, skip=skip, limit=limit)

    def list_user_reviews(self, user_id: int, skip: int = 0, limit: int = 50):
        return self.review_repo.get_for_user(user_id, skip=skip, limit=limit)
