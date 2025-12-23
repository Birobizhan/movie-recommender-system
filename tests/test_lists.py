import pytest
from fastapi import status


@pytest.fixture
def auth_token(client, test_user_data):
    """Фикстура для получения токена авторизации."""
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


def test_create_list(client, auth_token):
    """Тест создания списка фильмов"""
    response = client.post(
        "/api/lists/",
        json={
            "title": "Мой список",
            "description": "Описание списка"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Мой список"
    assert data["description"] == "Описание списка"
    assert "id" in data
    assert "owner_id" in data


def test_create_list_unauthorized(client):
    """Тест создания списка без авторизации"""
    response = client.post(
        "/api/lists/",
        json={
            "title": "Мой список"
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_list(client, auth_token):
    """Тест получения списка по ID"""
    create_response = client.post(
        "/api/lists/",
        json={
            "title": "Тестовый список"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    list_id = create_response.json()["id"]
    
    # Получаем список
    response = client.get(f"/api/lists/{list_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == list_id
    assert data["title"] == "Тестовый список"


def test_get_list_not_found(client):
    """Тест получения несуществующего списка"""
    response = client.get("/api/lists/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_list(client, auth_token):
    """Тест обновления списка"""
    create_response = client.post(
        "/api/lists/",
        json={
            "title": "Старое название"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    list_id = create_response.json()["id"]
    
    # Обновляем список
    response = client.put(
        f"/api/lists/{list_id}",
        json={
            "title": "Новое название",
            "description": "Новое описание"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Новое название"
    assert data["description"] == "Новое описание"


def test_delete_list(client, auth_token):
    """Тест удаления списка"""
    # Создаем список
    create_response = client.post(
        "/api/lists/",
        json={
            "title": "Список для удаления"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    list_id = create_response.json()["id"]
    
    # Удаляем список
    response = client.delete(
        f"/api/lists/{list_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "List deleted successfully"
    
    # Проверяем, что список удален
    get_response = client.get(f"/api/lists/{list_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_add_movies_to_list(client, auth_token, test_movie):
    """Тест добавления фильмов в список"""
    # Создаем список
    create_response = client.post(
        "/api/lists/",
        json={
            "title": "Список с фильмами"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    list_id = create_response.json()["id"]
    
    # Добавляем фильм
    response = client.post(
        f"/api/lists/{list_id}/movies",
        json={
            "movie_ids": [test_movie.id]
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["movie_count"] >= 1


def test_remove_movies_from_list(client, auth_token, test_movie):
    """Тест удаления фильмов из списка"""
    # Создаем список и добавляем фильм
    create_response = client.post(
        "/api/lists/",
        json={
            "title": "Список для удаления фильмов",
            "movie_ids": [test_movie.id]
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    list_id = create_response.json()["id"]
    
    # Удаляем фильм
    import json as json_lib
    response = client.request(
        "DELETE",
        f"/api/lists/{list_id}/movies",
        content=json_lib.dumps({"movie_ids": [test_movie.id]}),
        headers={"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["movie_count"] == 0
