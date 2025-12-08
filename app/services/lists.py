from sqlalchemy.orm import Session

from app.models.list import MovieList
from app.repositories import lists as list_repo
from app.repositories import users as user_repo
from app.schemas.list import MovieListCreate, MovieListUpdate, MovieListAddRemoveMovies


def create_list(db: Session, list_in: MovieListCreate, current_username: str) -> MovieList:
    user = user_repo.get_by_username(db, current_username)
    if not user:
        raise ValueError("User not found")

    db_list = list_repo.create_list(db, title=list_in.title, description=list_in.description, owner_id=user.id)
    if list_in.movie_ids:
        db_list = list_repo.add_movies(db, db_list, list_in.movie_ids)
    db_list.movie_count = len(db_list.movies)
    return db_list


def get_list(db: Session, list_id: int) -> MovieList | None:
    db_list = list_repo.get_list(db, list_id)
    if db_list:
        db_list.movie_count = len(db_list.movies)
    return db_list


def update_list(db: Session, list_id: int, list_in: MovieListUpdate, current_username: str) -> MovieList:
    user = user_repo.get_by_username(db, current_username)
    db_list = list_repo.get_list(db, list_id)
    if not db_list:
        raise LookupError("List not found")
    if not user or db_list.owner_id != user.id:
        raise PermissionError("Not enough permissions")
    db_list = list_repo.update_list(db, db_list, title=list_in.title, description=list_in.description)
    db_list.movie_count = len(db_list.movies)
    return db_list


def delete_list(db: Session, list_id: int, current_username: str) -> None:
    user = user_repo.get_by_username(db, current_username)
    db_list = list_repo.get_list(db, list_id)
    if not db_list:
        raise LookupError("List not found")
    if not user or db_list.owner_id != user.id:
        raise PermissionError("Not enough permissions")
    list_repo.delete_list(db, db_list)


def add_movies(db: Session, list_id: int, payload: MovieListAddRemoveMovies, current_username: str) -> MovieList:
    user = user_repo.get_by_username(db, current_username)
    db_list = list_repo.get_list(db, list_id)
    if not db_list:
        raise LookupError("List not found")
    if not user or db_list.owner_id != user.id:
        raise PermissionError("Not enough permissions")
    db_list = list_repo.add_movies(db, db_list, payload.movie_ids)
    db_list.movie_count = len(db_list.movies)
    return db_list


def remove_movies(db: Session, list_id: int, payload: MovieListAddRemoveMovies, current_username: str) -> MovieList:
    user = user_repo.get_by_username(db, current_username)
    db_list = list_repo.get_list(db, list_id)
    if not db_list:
        raise LookupError("List not found")
    if not user or db_list.owner_id != user.id:
        raise PermissionError("Not enough permissions")
    db_list = list_repo.remove_movies(db, db_list, payload.movie_ids)
    db_list.movie_count = len(db_list.movies)
    return db_list


def get_user_lists(db: Session, user_id: int):
    return list_repo.get_user_lists(db, user_id)
