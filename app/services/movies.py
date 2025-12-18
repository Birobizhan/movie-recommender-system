from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func, cast, TEXT
from app.basic_algorithm import recommend_movies
from app.models.movie import Movie
from app.models.analytics import MovieViewLog, SearchLog
from app.repositories.movies import MovieRepository
from app.schemas.movie import MovieCreate
from app.models.user import User


class MovieService:
    def __init__(self, db: Session):
        self.db = db
        self.movie_repo = MovieRepository(db)

    def get_movies(
        self,
        *,
        skip: int = 0,
        limit: int = 250,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        min_rating: Optional[float] = None,
        sort_by: Optional[str] = None,
        q: Optional[str] = None,
    ) -> List[Movie]:
        return self.movie_repo.list_movies(
            skip=skip,
            limit=limit,
            genre=genre,
            year=year,
            min_rating=min_rating,
            sort_by=sort_by,
            search_q=q,
        )

    def get_top_movies(
        self,
        *,
        skip: int = 0,
        limit: int = 250,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        min_rating: Optional[float] = None,
        sort_by: Optional[str] = None,
        q: Optional[str] = None,
        current_user: User | None = None
    ) -> List[Movie]:
        movies = self.movie_repo.list_movies(
            skip=skip,
            limit=limit,
            genre=genre,
            year=year,
            min_rating=min_rating,
            order_by_top=True,
            sort_by=sort_by,
            search_q=q,

        )
        if q is not None:
            # Логируем поиск
            try:
                log = SearchLog(
                    query=q.strip()[:255],
                    has_results=bool(movies),
                    results_count=len(movies),
                    user_id=current_user.id if current_user else None,
                )
                self.db.add(log)
                self.db.commit()
            except Exception:
                self.db.rollback()
        return movies

    def search(
        self,
        *,
        q: str,
        skip: int = 0,
        limit: int = 50,
        current_user: User | None = None,
    ) -> List[Movie]:
        movies = self.movie_repo.search_movies(q=q, skip=skip, limit=limit)

        # Логируем поиск
        try:
            log = SearchLog(
                query=q.strip()[:255],
                has_results=bool(movies),
                results_count=len(movies),
                user_id=current_user.id if current_user else None,
            )
            self.db.add(log)
            self.db.commit()
        except Exception:
            self.db.rollback()

        return movies

    def get_movie(
        self,
        movie_id: int,
        current_user: User | None = None,
    ) -> Movie | None:
        movie = self.movie_repo.get_movie(movie_id)
        if movie:
            try:
                log = MovieViewLog(
                    movie_id=movie.id,
                    user_id=current_user.id if current_user else None,
                )
                self.db.add(log)
                self.db.commit()
            except Exception:
                self.db.rollback()
        return movie

    def create_movie(self, movie_in: MovieCreate) -> Movie:
        existing = self.movie_repo.get_by_kp_id(movie_in.kp_id)
        if existing:
            raise ValueError("Movie with this Kinopoisk ID already exists")
        db_movie = Movie(**movie_in.model_dump())
        return self.movie_repo.create_movie(db_movie)

    def get_similar(self, movie_id: int, limit: int = 10) -> List[Movie]:
        movie = self.movie_repo.get_movie(movie_id)
        if not movie:
            return []
        return self.movie_repo.get_similar_movies(movie, limit=limit)

    def recommend_movies(
        self,
        *,
        main_genre: str,
        subgenre: str,
        subgenre_detail: str,
        time_period: str,
        limit: int = 20,
    ) -> List[Movie]:
        """
        Рекомендует фильмы на основе ответов пользователя из бота вопрос-ответ.
        
        Args:
            main_genre: Основной жанр (например, "Драма", "Комедия")
            subgenre: Поджанр (например, "Драма", "Комедия")
            subgenre_detail: Детализация поджанра (например, "Грустное/Трагическое")
            time_period: Временной период (например, "Классика (до 2000 года)")
            limit: Количество рекомендаций
        
        Returns:
            Список рекомендованных фильмов
        """
        print([main_genre, subgenre, subgenre_detail, time_period])
        movies = recommend_movies([main_genre, subgenre, subgenre_detail, time_period])
        list_movies = self.db.query(Movie).filter(
            Movie.title.in_(movies)
        ).all()
        order_map = {title: index for index, title in enumerate(movies)}

        # Сортируем список в Python, используя индекс из order_map
        list_movies.sort(key=lambda movie: order_map.get(movie.title, float('inf')))
        print(movies)
        print(list_movies)
        return list_movies[:limit]
