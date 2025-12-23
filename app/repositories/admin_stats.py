from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Tuple
from sqlalchemy import func, desc
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session
from app.models.movie import Movie
from app.models.review import Review
from app.models.list import MovieList
from app.models.user import User
from app.models.analytics import (
    SearchLog,
    PageViewLog,
    MovieViewLog,
    ErrorLog,
)


class AdminStatsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def db_health(self) -> bool:
        try:
            self.db.execute(func.now())
            return True
        except Exception:
            return False

    def db_basic_stats(self) -> Dict[str, Any]:
        movies_count = self.db.query(func.count(Movie.id)).scalar() or 0
        users_count = self.db.query(func.count(User.id)).scalar() or 0
        reviews_count = self.db.query(func.count(Review.id)).scalar() or 0
        lists_count = self.db.query(func.count(MovieList.id)).scalar() or 0
        users_created_list = lists_count - users_count * 3
        return {
            "movies_count": movies_count,
            "users_count": users_count,
            "reviews_count": reviews_count,
            "lists_count": lists_count,
            "users_created_list": users_created_list
        }

    def get_last_errors(self, limit: int = 10) -> List[ErrorLog]:
        try:
            return (
                self.db.query(ErrorLog)
                .order_by(desc(ErrorLog.created_at))
                .limit(limit)
                .all()
            )
        except ProgrammingError:
            self.db.rollback()
            return []

    def top_movies_by_views(
        self, since: datetime, limit: int = 10
    ) -> List[Tuple[Movie, int]]:
        try:
            q = (
                self.db.query(Movie, func.count(MovieViewLog.id).label("views"))
                .join(MovieViewLog, MovieViewLog.movie_id == Movie.id)
                .filter(MovieViewLog.created_at >= since)
                .group_by(Movie.id)
                .order_by(desc("views"))
                .limit(limit)
            )
            return q.all()
        except ProgrammingError:
            self.db.rollback()
            return []

    def new_reviews_count_today(self) -> int:
        today = date.today()
        tomorrow = today + timedelta(days=1)
        return (
            self.db.query(func.count(Review.id))
            .filter(Review.created_at >= today, Review.created_at < tomorrow)
            .scalar()
            or 0
        )

    def new_users_stats(self) -> Dict[str, int]:
        today = date.today()
        week_ago = today - timedelta(days=7)
        tomorrow = today + timedelta(days=1)

        today_count = (
            self.db.query(func.count(User.id))
            .filter(User.created_at >= today, User.created_at < tomorrow)
            .scalar()
            or 0
        )
        week_count = (
            self.db.query(func.count(User.id))
            .filter(User.created_at >= week_ago, User.created_at < tomorrow)
            .scalar()
            or 0
        )
        return {"today": today_count, "last_7_days": week_count}

    def active_users_last_7_days(self) -> int:
        since = datetime.utcnow() - timedelta(days=7)

        review_users = (
            self.db.query(Review.author_id)
            .filter(Review.created_at >= since)
            .distinct()
        )

        user_ids = {uid for (uid,) in review_users}

        return len(user_ids)

    def user_stats(self, user_id: int) -> Dict[str, Any] | None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        reviews_count = (
            self.db.query(func.count(Review.id))
            .filter(Review.author_id == user_id)
            .scalar()
            or 0
        )

        from app.models.list import MovieList

        lists_count = (
            self.db.query(func.count(MovieList.id))
            .filter(MovieList.owner_id == user_id)
            .scalar()
            or 0
        )

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "created_at": user.created_at,
            "reviews_count": reviews_count,
            "lists_count": lists_count,
        }

    def top_search_queries(
        self, limit: int = 5, only_without_results: bool = False
    ) -> List[Tuple[str, int]]:
        q = self.db.query(
            SearchLog.query,
            func.count(SearchLog.id).label("cnt"),
        )
        if only_without_results:
            q = q.filter(SearchLog.has_results.is_(False))
        q = (
            q.group_by(SearchLog.query)
            .order_by(desc("cnt"))
            .limit(limit)
        )
        print(q)
        return q.all()

    def top_pages(self, limit: int = 10) -> List[Tuple[str, int]]:
        q = (
            self.db.query(
                PageViewLog.path,
                func.count(PageViewLog.id).label("cnt"),
            )
            .group_by(PageViewLog.path)
            .order_by(desc("cnt"))
            .limit(limit)
        )
        return q.all()
