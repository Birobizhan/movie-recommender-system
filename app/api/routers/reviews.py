from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.review import ReviewResponse, ReviewCreate, ReviewUpdate
from app.services import reviews as review_service

router = APIRouter(tags=["Reviews"])


@router.post("/", response_model=ReviewResponse)
def create_review(
    review: ReviewCreate,
    current_user: str = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    try:
        return review_service.create_review(db, review, current_user)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    current_user: str = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    try:
        return review_service.update_review(db, review_id, review_update, current_user)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))


@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    current_user: str = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    try:
        review_service.delete_review(db, review_id, current_user)
        return {"message": "Review deleted successfully"}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))


@router.get("/movie/{movie_id}", response_model=List[ReviewResponse])
def get_movie_reviews(movie_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(deps.get_db)):
    return review_service.list_movie_reviews(db, movie_id, skip=skip, limit=limit)


@router.get("/user/{user_id}", response_model=List[ReviewResponse])
def get_user_reviews(user_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(deps.get_db)):
    return review_service.list_user_reviews(db, user_id, skip=skip, limit=limit)
