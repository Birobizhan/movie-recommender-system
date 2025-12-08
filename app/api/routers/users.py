from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.user import UserBase, UserCreate, UserResponse, UserProfile, UserLogin, Token
from app.services import users as user_service
from app.repositories import users as user_repo
from app.repositories import reviews as review_repo
from app.repositories import lists as list_repo
from app.models.review import Review
from app.models.list import MovieList

router = APIRouter(tags=["Users"])


@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(deps.get_db)):
    try:
        return user_service.register_user(db, user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/login", response_model=Token)
def login_user(user_data: UserLogin, db: Session = Depends(deps.get_db)):
    try:
        result = user_service.login_user(db, user_data)
        return {**result, "user": UserResponse.model_validate(result["user"])}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: str = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    user = user_repo.get_by_username(db, current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}", response_model=UserProfile)
def get_user_profile(user_id: int, db: Session = Depends(deps.get_db)):
    user = user_repo.get_by_id(db, user_id)
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
