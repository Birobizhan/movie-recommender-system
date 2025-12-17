import pytest
from fastapi import status


def test_get_movies_empty(client):
    """Тест получения списка фильмов (пустой список)."""
    response = client.get("/api/movies/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_movies_with_params(client):
    """Тест получения фильмов с параметрами."""
    response = client.get("/api/movies/?limit=10&skip=0")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_get_movie_not_found(client):
    """Тест получения несуществующего фильма."""
    response = client.get("/api/movies/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_search_movies_empty(client):
    """Тест поиска фильмов (пустой результат)."""
    response = client.get("/api/movies/search?q=несуществующий+фильм")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
