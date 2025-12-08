from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.list import MovieListResponse, MovieListCreate, MovieListUpdate, MovieListAddRemoveMovies
from app.services import lists as list_service

router = APIRouter(tags=["Lists"])


@router.post("/", response_model=MovieListResponse)
def create_list(
    list_data: MovieListCreate,
    current_user: str = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    try:
        return list_service.create_list(db, list_data, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/{list_id}", response_model=MovieListResponse)
def get_list(list_id: int, db: Session = Depends(deps.get_db)):
    db_list = list_service.get_list(db, list_id)
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
    return db_list


@router.put("/{list_id}", response_model=MovieListResponse)
def update_list(
    list_id: int,
    list_update: MovieListUpdate,
    current_user: str = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    try:
        return list_service.update_list(db, list_id, list_update, current_user)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.delete("/{list_id}")
def delete_list(
    list_id: int,
    current_user: str = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    try:
        list_service.delete_list(db, list_id, current_user)
        return {"message": "List deleted successfully"}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.post("/{list_id}/movies", response_model=MovieListResponse)
def add_movies_to_list(
    list_id: int,
    data: MovieListAddRemoveMovies,
    current_user: str = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    try:
        return list_service.add_movies(db, list_id, data, current_user)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.delete("/{list_id}/movies", response_model=MovieListResponse)
def remove_movies_from_list(
    list_id: int,
    data: MovieListAddRemoveMovies,
    current_user: str = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    try:
        return list_service.remove_movies(db, list_id, data, current_user)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.get("/user/{user_id}", response_model=List[MovieListResponse])
def get_user_lists(user_id: int, db: Session = Depends(deps.get_db)):
    return list_service.get_user_lists(db, user_id)
