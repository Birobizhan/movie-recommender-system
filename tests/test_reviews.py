import pytest
from fastapi import status


@pytest.fixture
def auth_token(client, test_user_data):
    """Фикстура для получения токена авторизации"""
    client.post("/api/users/register", json=test_user_data)
    login_response = client.post(
        "/api/users/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    return login_response.json()["access_token"]


@pytest.fixture
def test_movie(client, db, test_movie_data):
    """Создает тестовый фильм в БД напрямую"""
    from app.models.movie import Movie
    
    # Убираем genres из данных, так как SQLite не поддерживает ARRAY
    movie_data = {k: v for k, v in test_movie_data.items() if k != "genres"}
    movie = Movie(**movie_data)
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


def test_create_review(client, auth_token, test_movie):
    """Тест создания отзыва"""
    response = client.post(
        "/api/reviews/",
        json={
            "movie_id": test_movie.id,
            "rating": 8.5,
            "content": "Отличный фильм!"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["movie_id"] == test_movie.id
    assert data["rating"] == 8.5
    assert data["content"] == "Отличный фильм!"
    assert "id" in data
    assert "author_id" in data


def test_create_review_unauthorized(client, test_movie):
    """Тест создания отзыва без авторизации"""
    response = client.post(
        "/api/reviews/",
        json={
            "movie_id": test_movie.id,
            "rating": 8.5
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_movie_reviews(client, auth_token, test_movie):
    """Тест получения отзывов фильма"""
    # Создаем отзыв
    client.post(
        "/api/reviews/",
        json={
            "movie_id": test_movie.id,
            "rating": 8.5,
            "content": "Тестовый отзыв"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Получаем отзывы
    response = client.get(f"/api/reviews/movie/{test_movie.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_update_review(client, auth_token, test_movie):
    """Тест обновления отзыва"""
    # Создаем отзыв
    create_response = client.post(
        "/api/reviews/",
        json={
            "movie_id": test_movie.id,
            "rating": 8.5,
            "content": "Старый отзыв"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    review_id = create_response.json()["id"]
    
    # Обновляем отзыв
    response = client.put(
        f"/api/reviews/{review_id}",
        json={
            "rating": 9.0,
            "content": "Обновленный отзыв"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["rating"] == 9.0
    assert data["content"] == "Обновленный отзыв"


def test_delete_review(client, auth_token, test_movie):
    """Тест удаления отзыва"""
    # Создаем отзыв
    create_response = client.post(
        "/api/reviews/",
        json={
            "movie_id": test_movie.id,
            "rating": 8.5
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    review_id = create_response.json()["id"]
    
    # Удаляем отзыв
    response = client.delete(
        f"/api/reviews/{review_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Review deleted successfully"
    
    # Проверяем, что отзыв удален
    get_response = client.get(f"/api/reviews/movie/{test_movie.id}")
    assert len(get_response.json()) == 0
