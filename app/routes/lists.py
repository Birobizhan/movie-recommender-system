from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.movie import Movie
from app.models.list import MovieList
from app.schemas.list import MovieListResponse, MovieListCreate, MovieListUpdate, MovieListAddRemoveMovies
from app.schemas.movie import MovieResponse  

router = APIRouter()

@router.post("/", response_model=MovieListResponse)
def create_list(
    list_data: MovieListCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == current_user).first()
    
    # Создаем список
    db_list = MovieList(
        title=list_data.title,
        description=list_data.description,
        owner_id=user.id
    )
    
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    
    # Добавляем фильмы, если указаны
    if list_data.movie_ids:
        for movie_id in list_data.movie_ids:
            movie = db.query(Movie).filter(Movie.id == movie_id).first()
            if movie:
                db_list.movies.append(movie)
        
        db.commit()
        db.refresh(db_list)
    
    # Добавляем количество фильмов
    db_list.movie_count = len(db_list.movies)
    
    return db_list

# Создаем кастомную схему ответа для списка с фильмами
class MovieListWithMoviesResponse(MovieListResponse):
    movies: List[MovieResponse]

@router.get("/{list_id}", response_model=MovieListWithMoviesResponse)
def get_list(list_id: int, db: Session = Depends(get_db)):
    db_list = db.query(MovieList).filter(MovieList.id == list_id).first()
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
    
    # Добавляем количество фильмов
    db_list.movie_count = len(db_list.movies)
    
    # Возвращаем список с фильмами
    return {
        "id": db_list.id,
        "title": db_list.title,
        "description": db_list.description,
        "owner_id": db_list.owner_id,
        "created_at": db_list.created_at,
        "updated_at": db_list.updated_at,
        "movie_count": db_list.movie_count,
        "movies": db_list.movies
    }

@router.put("/{list_id}", response_model=MovieListResponse)
def update_list(
    list_id: int,
    list_update: MovieListUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == current_user).first()
    db_list = db.query(MovieList).filter(MovieList.id == list_id).first()
    
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
    
    if db_list.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Обновляем поля
    if list_update.title is not None:
        db_list.title = list_update.title
    if list_update.description is not None:
        db_list.description = list_update.description
    
    db.commit()
    db.refresh(db_list)
    
    # Добавляем количество фильмов
    db_list.movie_count = len(db_list.movies)
    
    return db_list

@router.delete("/{list_id}")
def delete_list(
    list_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == current_user).first()
    db_list = db.query(MovieList).filter(MovieList.id == list_id).first()
    
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
    
    if db_list.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db.delete(db_list)
    db.commit()
    return {"message": "List deleted successfully"}

@router.post("/{list_id}/movies", response_model=MovieListResponse)
def add_movies_to_list(
    list_id: int,
    data: MovieListAddRemoveMovies,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == current_user).first()
    db_list = db.query(MovieList).filter(MovieList.id == list_id).first()
    
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
    
    if db_list.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Добавляем фильмы
    for movie_id in data.movie_ids:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if movie and movie not in db_list.movies:
            db_list.movies.append(movie)
    
    db.commit()
    db.refresh(db_list)
    
    # Добавляем количество фильмов
    db_list.movie_count = len(db_list.movies)
    
    return db_list

@router.delete("/{list_id}/movies", response_model=MovieListResponse)
def remove_movies_from_list(
    list_id: int,
    data: MovieListAddRemoveMovies,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == current_user).first()
    db_list = db.query(MovieList).filter(MovieList.id == list_id).first()
    
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
    
    if db_list.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Удаляем фильмы
    for movie_id in data.movie_ids:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if movie and movie in db_list.movies:
            db_list.movies.remove(movie)
    
    db.commit()
    db.refresh(db_list)
    
    # Добавляем количество фильмов
    db_list.movie_count = len(db_list.movies)
    
    return db_list

@router.get("/user/{user_id}", response_model=List[MovieListResponse])
def get_user_lists(user_id: int, db: Session = Depends(get_db)):
    lists = db.query(MovieList).filter(MovieList.owner_id == user_id).all()
    
    # Добавляем количество фильмов для каждого списка
    for movie_list in lists:
        movie_list.movie_count = len(movie_list.movies)
    
    return lists