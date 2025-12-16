from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.schemas.user import UserBase, UserCreate, UserResponse, UserProfile, UserProfileExtended, UserLogin, Token, UserUpdate, UserPasswordUpdate, PasswordResetRequest, PasswordResetConfirm
from app.services import UserService
from app.repositories import UserRepository
from app.models.review import Review
from app.models.list import MovieList

router = APIRouter(tags=["Users"])


@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(deps.get_db)):
    try:
        service = UserService(db)
        return service.register_user(user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/login", response_model=Token)
def login_user(user_data: UserLogin, db: Session = Depends(deps.get_db)):
    try:
        service = UserService(db)
        result = service.login_user(user_data)
        return {**result, "user": UserResponse.model_validate(result["user"])}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@router.post("/forgot-password")
def forgot_password(reset_request: PasswordResetRequest, db: Session = Depends(deps.get_db)):
    """
    Запрос на сброс пароля.
    В реальном приложении здесь должна быть отправка email с токеном.
    Для демонстрации возвращаем токен в ответе.
    """
    try:
        service = UserService(db)
        result = service.request_password_reset(reset_request)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/reset-password")
def reset_password(reset_confirm: PasswordResetConfirm, db: Session = Depends(deps.get_db)):
    """
    Установка нового пароля по токену сброса.
    """
    try:
        service = UserService(db)
        result = service.reset_password(reset_confirm)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    return current_user


@router.get("/me/profile", response_model=UserProfileExtended)
def get_current_user_profile(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Получает расширенный профиль текущего пользователя с последними просмотренными фильмами
    и любимыми жанрами.
    """
    try:
        service = UserService(db)
        profile_data = service.get_extended_profile(current_user.id)
        
        # Формируем ответ
        user_data = UserResponse.model_validate(profile_data["user"])
        # Преобразуем MovieResponse объекты в словари
        recent_movies = []
        for movie in profile_data["recent_watched_movies"]:
            if hasattr(movie, 'model_dump'):
                recent_movies.append(movie.model_dump())
            else:
                recent_movies.append(movie)
        
        return UserProfileExtended(
            **user_data.model_dump(),
            reviews_count=profile_data["reviews_count"],
            lists_count=profile_data["lists_count"],
            average_rating=profile_data["average_rating"],
            recent_watched_movies=recent_movies,
            favorite_genres=profile_data["favorite_genres"],
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Обновление своего профиля (email, username).
    Пользователь может обновлять только свой профиль.
    """
    try:
        service = UserService(db)
        return service.update_profile(current_user, user_update)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.put("/me/password", response_model=UserResponse)
def update_current_user_password(
    password_update: UserPasswordUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Изменение пароля текущего пользователя.
    Требует старый пароль для подтверждения.
    """
    try:
        service = UserService(db)
        return service.update_password(current_user, password_update)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/{user_id}", response_model=UserProfile)
def get_user_profile(user_id: int, db: Session = Depends(deps.get_db)):
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reviews_count = db.query(Review).filter(Review.author_id == user_id).count()
    lists_count = db.query(MovieList).filter(MovieList.owner_id == user_id).count()

    from sqlalchemy import func

    avg_rating_result = db.query(func.avg(Review.rating)).filter(Review.author_id == user_id).scalar()
    avg_rating = float(avg_rating_result) if avg_rating_result is not None else None

    user_data = UserResponse.model_validate(user)
    return UserProfile(
        **user_data.model_dump(),
        reviews_count=reviews_count,
        lists_count=lists_count,
        average_rating=avg_rating,
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user_profile(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(deps.get_current_admin),  # Только админ может обновлять чужие профили
    db: Session = Depends(deps.get_db),
):
    """
    Обновление профиля пользователя администратором.
    Админ может обновлять профили любых пользователей.
    """
    try:
        service = UserService(db)
        return service.update_user_by_admin(user_id, user_update, current_user)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
