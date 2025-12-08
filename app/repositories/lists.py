from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.list import MovieList
from app.models.movie import Movie


def create_list(db: Session, *, title: str, description: str | None, owner_id: int) -> MovieList:
    db_list = MovieList(title=title, description=description, owner_id=owner_id)
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list


def get_list(db: Session, list_id: int) -> Optional[MovieList]:
    return db.query(MovieList).filter(MovieList.id == list_id).first()


def update_list(db: Session, movie_list: MovieList, *, title: Optional[str], description: Optional[str]) -> MovieList:
    if title is not None:
        movie_list.title = title
    if description is not None:
        movie_list.description = description
    db.commit()
    db.refresh(movie_list)
    return movie_list


def delete_list(db: Session, movie_list: MovieList) -> None:
    db.delete(movie_list)
    db.commit()


def add_movies(db: Session, movie_list: MovieList, movie_ids: List[int]) -> MovieList:
    for movie_id in movie_ids:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if movie and movie not in movie_list.movies:
            movie_list.movies.append(movie)
    db.commit()
    db.refresh(movie_list)
    return movie_list


def remove_movies(db: Session, movie_list: MovieList, movie_ids: List[int]) -> MovieList:
    for movie_id in movie_ids:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if movie and movie in movie_list.movies:
            movie_list.movies.remove(movie)
    db.commit()
    db.refresh(movie_list)
    return movie_list


def get_user_lists(db: Session, user_id: int) -> List[MovieList]:
    lists = db.query(MovieList).filter(MovieList.owner_id == user_id).all()
    for movie_list in lists:
        movie_list.movie_count = len(movie_list.movies)
    return lists
