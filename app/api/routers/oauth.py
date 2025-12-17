from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.api import deps
from app.services.oauth import OAuthService
from app.core.config import YANDEX_CLIENT_ID, YANDEX_REDIRECT_URI, FRONTEND_URL

router = APIRouter(tags=["OAuth"])


@router.get("/auth/yandex")
async def yandex_login():
    """Перенаправляет пользователя на страницу авторизации Yandex."""
    if not YANDEX_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Yandex OAuth не настроен"
        )
    
    auth_url = (
        f"https://oauth.yandex.ru/authorize?"
        f"response_type=code&"
        f"client_id={YANDEX_CLIENT_ID}&"
        f"redirect_uri={YANDEX_REDIRECT_URI}"
    )
    
    return RedirectResponse(url=auth_url)


@router.get("/auth/yandex/callback")
async def yandex_callback(
    code: str = None,
    error: str = None,
    db: Session = Depends(deps.get_db),
):
    """Обрабатывает callback от Yandex OAuth."""
    if error:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?error=oauth_cancelled"
        )
    
    if not code:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?error=no_code"
        )
    
    try:
        oauth_service = OAuthService(db)
        yandex_data = await oauth_service.get_yandex_user_info(code)
        
        if not yandex_data:
            return RedirectResponse(
                url=f"{FRONTEND_URL}/login?error=oauth_failed"
            )
        
        user = oauth_service.get_or_create_user_from_yandex(yandex_data)
        token_data = oauth_service.create_oauth_token(user)
        
        # Перенаправляем на фронтенд с токеном в URL параметре
        # Фронтенд должен будет сохранить токен и перенаправить пользователя
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?token={token_data['access_token']}&success=true"
        )
    except Exception as e:
        print(f"Ошибка при обработке OAuth callback: {e}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?error=oauth_error"
        )
