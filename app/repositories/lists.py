from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.list import MovieList
from app.models.movie import Movie


class ListRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_list(self, *, title: str, description: str | None, owner_id: int) -> MovieList:
        db_list = MovieList(title=title, description=description, owner_id=owner_id)
        self.db.add(db_list)
        self.db.commit()
        self.db.refresh(db_list)
        return db_list

    def get_list(self, list_id: int) -> Optional[MovieList]:
        return self.db.query(MovieList).filter(MovieList.id == list_id).first()

    def update_list(self, movie_list: MovieList, *, title: Optional[str], description: Optional[str]) -> MovieList:
        if title is not None:
            movie_list.title = title
        if description is not None:
            movie_list.description = description
        self.db.commit()
        self.db.refresh(movie_list)
        return movie_list

    def delete_list(self, movie_list: MovieList) -> None:
        self.db.delete(movie_list)
        self.db.commit()

    def add_movies(self, movie_list: MovieList, movie_ids: List[int]) -> MovieList:
        for movie_id in movie_ids:
            movie = self.db.query(Movie).filter(Movie.id == movie_id).first()
            if movie and movie not in movie_list.movies:
                movie_list.movies.append(movie)
        self.db.commit()
        self.db.refresh(movie_list)
        return movie_list

    def remove_movies(self, movie_list: MovieList, movie_ids: List[int]) -> MovieList:
        for movie_id in movie_ids:
            movie = self.db.query(Movie).filter(Movie.id == movie_id).first()
            if movie and movie in movie_list.movies:
                movie_list.movies.remove(movie)
        self.db.commit()
        self.db.refresh(movie_list)
        return movie_list

    def get_user_lists(self, user_id: int) -> List[MovieList]:
        lists = self.db.query(MovieList).filter(MovieList.owner_id == user_id).all()
        for movie_list in lists:
            movie_list.movie_count = len(movie_list.movies)
        return lists





