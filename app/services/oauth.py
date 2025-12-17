from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import httpx
from app.models.user import User
from app.repositories.users import UserRepository
from app.auth.jwt import create_access_token
from app.core.config import YANDEX_CLIENT_ID, YANDEX_CLIENT_SECRET, YANDEX_REDIRECT_URI


class OAuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_yandex_user_info(self, code: str) -> Optional[Dict[str, Any]]:
        """Получает информацию о пользователе Yandex по коду авторизации."""
        try:
            # Обмениваем код на токен
            async with httpx.AsyncClient() as client:
                token_response = await client.post(
                    "https://oauth.yandex.ru/token",
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "client_id": YANDEX_CLIENT_ID,
                        "client_secret": YANDEX_CLIENT_SECRET,
                    },
                )
                token_response.raise_for_status()
                token_data = token_response.json()
                access_token = token_data.get("access_token")

                if not access_token:
                    return None

                # Получаем информацию о пользователе
                user_response = await client.get(
                    "https://login.yandex.ru/info",
                    headers={"Authorization": f"OAuth {access_token}"},
                )
                user_response.raise_for_status()
                return user_response.json()
        except Exception as e:
            print(f"Ошибка при получении данных от Yandex: {e}")
            return None

    def get_or_create_user_from_yandex(self, yandex_data: Dict[str, Any]) -> User:
        """Создает или получает пользователя на основе данных Yandex."""
        yandex_id = yandex_data.get("id")
        email = yandex_data.get("default_email") or yandex_data.get("emails", [None])[0]
        first_name = yandex_data.get("first_name", "")
        last_name = yandex_data.get("last_name", "")
        username = yandex_data.get("login") or email.split("@")[0] if email else f"user_{yandex_id}"

        # Проверяем, есть ли пользователь с таким Yandex ID или email
        user = self.user_repo.get_by_email(email) if email else None
        
        if not user and yandex_id:
            # Пытаемся найти по Yandex ID (если есть поле oauth_id в модели)
            # Пока ищем только по email
            pass

        if user:
            # Обновляем данные пользователя, если нужно
            if not user.username and username:
                user.username = username
            self.db.commit()
            self.db.refresh(user)
            return user

        # Создаем нового пользователя
        # Генерируем случайный пароль (пользователь не будет его знать, но это нужно для модели)
        import secrets
        from app.auth.password import hash_password
        random_password = secrets.token_urlsafe(32)
        hashed_password = hash_password(random_password)

        new_user = self.user_repo.create_user(
            email=email or f"yandex_{yandex_id}@yandex.oauth",
            username=username,
            hashed_password=hashed_password,
        )
        return new_user

    def create_oauth_token(self, user: User) -> Dict[str, Any]:
        """Создает JWT токен для пользователя после OAuth авторизации."""
        from app.schemas.user import UserResponse
        
        access_token = create_access_token(data={"sub": str(user.id)})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user),
        }
