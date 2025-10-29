from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.auth import get_password_hash, verify_password, create_access_token
from app.dependencies import get_current_user
from app.models.user import User
from app.models.review import Review
from app.models.list import MovieList
from app.schemas.user import UserBase, UserCreate, UserResponse, UserProfile, UserLogin, Token

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Проверяем, существует ли пользователь с таким email
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Проверяем, существует ли пользователь с таким username
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Хешируем пароль и создаем пользователя
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    # Ищем пользователя по email
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if not db_user or not verify_password(user_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Создаем JWT токен
    access_token = create_access_token(data={"sub": db_user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(db_user)
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{user_id}", response_model=UserProfile)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Считаем статистику
    reviews_count = db.query(Review).filter(Review.author_id == user_id).count()
    lists_count = db.query(MovieList).filter(MovieList.owner_id == user_id).count()
    
    # Средний рейтинг пользователя
    from sqlalchemy import func
    avg_rating_result = db.query(func.avg(Review.rating)).filter(Review.author_id == user_id).scalar()
    avg_rating = float(avg_rating_result) if avg_rating_result else None
    
    user_data = UserResponse.model_validate(user)
    return UserProfile(
        **user_data.model_dump(),
        reviews_count=reviews_count,
        lists_count=lists_count,
        average_rating=avg_rating
    )