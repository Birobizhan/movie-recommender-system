from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.auth import verify_token

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    # Зависимость для получения текущего пользователя из JWT токена
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token.credentials)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception

async def get_optional_user(token: str = Depends(security)):
    try:
        payload = verify_token(token.credentials)
        username: str = payload.get("sub")
        return username
    except Exception:
        return None