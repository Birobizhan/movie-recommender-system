from sqlalchemy.orm import Session

from app.models.list import MovieList
from app.repositories.lists import ListRepository
from app.repositories.users import UserRepository
from app.schemas.list import MovieListCreate, MovieListUpdate, MovieListAddRemoveMovies


class ListService:
    def __init__(self, db: Session):
        self.db = db
        self.list_repo = ListRepository(db)
        self.user_repo = UserRepository(db)

    def create_list(self, list_in: MovieListCreate, current_user) -> MovieList:
        from app.models.user import User
        if not isinstance(current_user, User):
            raise ValueError("Invalid user object")

        db_list = self.list_repo.create_list(title=list_in.title, description=list_in.description, owner_id=current_user.id)
        if list_in.movie_ids:
            db_list = self.list_repo.add_movies(db_list, list_in.movie_ids)
        db_list.movie_count = len(db_list.movies)
        return db_list

    def get_list(self, list_id: int) -> MovieList | None:
        db_list = self.list_repo.get_list(list_id)
        if db_list:
            db_list.movie_count = len(db_list.movies)
        return db_list

    def update_list(self, list_id: int, list_in: MovieListUpdate, current_user) -> MovieList:
        from app.models.user import User
        if not isinstance(current_user, User):
            raise ValueError("Invalid user object")
            
        db_list = self.list_repo.get_list(list_id)
        if not db_list:
            raise LookupError("List not found")
        # Пользователь может редактировать только свои списки, админ может редактировать любые
        if db_list.owner_id != current_user.id and not current_user.is_admin():
            raise PermissionError("Not enough permissions")
        db_list = self.list_repo.update_list(db_list, title=list_in.title, description=list_in.description)
        db_list.movie_count = len(db_list.movies)
        return db_list

    def delete_list(self, list_id: int, current_user) -> None:
        from app.models.user import User
        if not isinstance(current_user, User):
            raise ValueError("Invalid user object")
            
        db_list = self.list_repo.get_list(list_id)
        if not db_list:
            raise LookupError("List not found")
        # Пользователь может удалять только свои списки, админ может удалять любые
        if db_list.owner_id != current_user.id and not current_user.is_admin():
            raise PermissionError("Not enough permissions")
        self.list_repo.delete_list(db_list)

    def add_movies(self, list_id: int, payload: MovieListAddRemoveMovies, current_user) -> MovieList:
        from app.models.user import User
        if not isinstance(current_user, User):
            raise ValueError("Invalid user object")
            
        db_list = self.list_repo.get_list(list_id)
        if not db_list:
            raise LookupError("List not found")
        # Пользователь может изменять только свои списки, админ может изменять любые
        if db_list.owner_id != current_user.id and not current_user.is_admin():
            raise PermissionError("Not enough permissions")
        db_list = self.list_repo.add_movies(db_list, payload.movie_ids)
        db_list.movie_count = len(db_list.movies)
        return db_list

    def remove_movies(self, list_id: int, payload: MovieListAddRemoveMovies, current_user) -> MovieList:
        from app.models.user import User
        if not isinstance(current_user, User):
            raise ValueError("Invalid user object")
            
        db_list = self.list_repo.get_list(list_id)
        if not db_list:
            raise LookupError("List not found")
        # Пользователь может изменять только свои списки, админ может изменять любые
        if db_list.owner_id != current_user.id and not current_user.is_admin():
            raise PermissionError("Not enough permissions")
        db_list = self.list_repo.remove_movies(db_list, payload.movie_ids)
        db_list.movie_count = len(db_list.movies)
        return db_list

    def get_user_lists(self, user_id: int):
        return self.list_repo.get_user_lists(user_id)










