import pytest
from fastapi import status


def test_register_user(client, test_user_data):
    """Тест регистрации нового пользователя."""
    response = client.post("/api/users/register", json=test_user_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["username"] == test_user_data["username"]
    assert "id" in data
    assert "password" not in data  # Пароль не должен возвращаться


def test_register_duplicate_email(client, test_user_data):
    """Тест регистрации с дублирующимся email."""
    # Создаем первого пользователя
    client.post("/api/users/register", json=test_user_data)
    
    # Пытаемся создать второго с тем же email
    response = client.post("/api/users/register", json=test_user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_user(client, test_user_data):
    """Тест входа пользователя."""
    # Сначала регистрируем
    client.post("/api/users/register", json=test_user_data)
    
    # Затем логинимся
    response = client.post(
        "/api/users/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data


def test_login_wrong_password(client, test_user_data):
    """Тест входа с неверным паролем."""
    client.post("/api/users/register", json=test_user_data)
    
    response = client.post(
        "/api/users/login",
        json={
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, test_user_data):
    """Тест получения текущего пользователя."""
    # Регистрируем и логинимся
    client.post("/api/users/register", json=test_user_data)
    login_response = client.post(
        "/api/users/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    token = login_response.json()["access_token"]
    
    # Получаем текущего пользователя
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["username"] == test_user_data["username"]


def test_get_current_user_unauthorized(client):
    """Тест получения текущего пользователя без токена."""
    response = client.get("/api/users/me")
    assert response.status_code == status.HTTP_403_FORBIDDEN


