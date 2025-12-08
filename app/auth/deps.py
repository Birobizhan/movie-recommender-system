from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.auth.jwt import verify_token

security = HTTPBearer()


async def get_current_user(token=Depends(security)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token.credentials)
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception


async def get_optional_user(token=Depends(security)) -> str | None:
    try:
        payload = verify_token(token.credentials)
        return payload.get("sub")
    except Exception:
        return None
