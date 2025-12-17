from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.auth.jwt import verify_token
from app.repositories.users import UserRepository
from app.models.user import User, UserRole
from app.db.session import get_db

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Получает текущего пользователя из JWT токена.
    Возвращает объект User или вызывает HTTPException.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(credentials.credentials)
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        user_repo = UserRepository(db)
        user = user_repo.get_by_username(username)
        if user is None:
            raise credentials_exception
        return user
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Проверяет, что текущий пользователь является администратором.
    Возвращает объект User или вызывает HTTPException.
    """
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> User | None:
    """
    Опционально получает пользователя из токена.
    Возвращает User если токен валиден, иначе None.
    """
    if credentials is None:
        return None
    try:
        payload = verify_token(credentials.credentials)
        username: str | None = payload.get("sub")
        if username is None:
            return None
        
        user_repo = UserRepository(db)
        return user_repo.get_by_username(username)
    except Exception:
        return None










