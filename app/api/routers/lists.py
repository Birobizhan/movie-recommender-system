from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.schemas.list import MovieListResponse, MovieListCreate, MovieListUpdate, MovieListAddRemoveMovies
from app.services import ListService

router = APIRouter(tags=["Lists"])


@router.post("/", response_model=MovieListResponse)
def create_list(
    list_data: MovieListCreate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    try:
        service = ListService(db)
        return service.create_list(list_data, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/{list_id}", response_model=MovieListResponse)
def get_list(list_id: int, db: Session = Depends(deps.get_db)):
    service = ListService(db)
    db_list = service.get_list(list_id)
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
    return db_list


@router.put("/{list_id}", response_model=MovieListResponse)
def update_list(
    list_id: int,
    list_update: MovieListUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    try:
        service = ListService(db)
        return service.update_list(list_id, list_update, current_user)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.delete("/{list_id}")
def delete_list(
    list_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    try:
        service = ListService(db)
        service.delete_list(list_id, current_user)
        return {"message": "List deleted successfully"}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.post("/{list_id}/movies", response_model=MovieListResponse)
def add_movies_to_list(
    list_id: int,
    data: MovieListAddRemoveMovies,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    try:
        service = ListService(db)
        return service.add_movies(list_id, data, current_user)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.delete("/{list_id}/movies", response_model=MovieListResponse)
def remove_movies_from_list(
    list_id: int,
    data: MovieListAddRemoveMovies,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    try:
        service = ListService(db)
        return service.remove_movies(list_id, data, current_user)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.get("/user/{user_id}", response_model=List[MovieListResponse])
def get_user_lists(user_id: int, db: Session = Depends(deps.get_db)):
    service = ListService(db)
    return service.get_user_lists(user_id)
