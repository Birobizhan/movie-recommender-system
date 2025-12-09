from sqlalchemy.orm import Session

from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.models.user import User
from app.repositories.users import UserRepository
from app.repositories.lists import ListRepository
from app.schemas.user import UserCreate, UserLogin, UserUpdate, UserPasswordUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.list_repo = ListRepository(db)

    def register_user(self, user_in: UserCreate) -> User:
        if self.user_repo.get_by_email(user_in.email):
            raise ValueError("Email already registered")
        if self.user_repo.get_by_username(user_in.username):
            raise ValueError("Username already taken")

        hashed_pwd = hash_password(user_in.password)
        user = self.user_repo.create_user(email=user_in.email, username=user_in.username, hashed_password=hashed_pwd)

        # Создаем базовые списки
        default_lists = ["Просмотренные", "Буду смотреть", "Любимые"]
        for title in default_lists:
            try:
                self.list_repo.create_list(title=title, description=None, owner_id=user.id)
            except Exception:
                self.db.rollback()
        return user

    def login_user(self, user_in: UserLogin) -> dict:
        email = user_in.email.strip()
        db_user = self.user_repo.get_by_email(email)
        if not db_user or not verify_password(user_in.password, db_user.hashed_password):
            raise ValueError("Incorrect email or password")

        access_token = create_access_token(data={"sub": db_user.username})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": db_user,
        }

    def get_user_profile(self, user_id: int) -> User | None:
        return self.user_repo.get_by_id(user_id)

    def update_profile(self, current_user: User, user_update: UserUpdate) -> User:
        """
        Обновляет профиль пользователя.
        Пользователь может обновлять только свой профиль.
        """
        from app.models.user import User
        if not isinstance(current_user, User):
            raise ValueError("Invalid user object")

        return self.user_repo.update_user(
            current_user,
            email=user_update.email,
            username=user_update.username,
        )

    def update_password(self, current_user: User, password_update: UserPasswordUpdate) -> User:
        """
        Обновляет пароль пользователя.
        Требует старый пароль для подтверждения.
        """
        from app.models.user import User
        if not isinstance(current_user, User):
            raise ValueError("Invalid user object")

        # Проверяем старый пароль
        if not verify_password(password_update.old_password, current_user.hashed_password):
            raise ValueError("Incorrect old password")

        # Хешируем новый пароль
        new_hashed_password = hash_password(password_update.new_password)
        return self.user_repo.update_password(current_user, new_hashed_password)

    def update_user_by_admin(self, user_id: int, user_update: UserUpdate, admin_user: User) -> User:
        """
        Обновляет профиль пользователя администратором.
        Админ может обновлять профили любых пользователей.
        """
        from app.models.user import User
        if not isinstance(admin_user, User):
            raise ValueError("Invalid admin user object")
        if not admin_user.is_admin():
            raise PermissionError("Admin access required")

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise LookupError("User not found")

        return self.user_repo.update_user(
            user,
            email=user_update.email,
            username=user_update.username,
        )
