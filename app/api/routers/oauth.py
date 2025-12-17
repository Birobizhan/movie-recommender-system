from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode, quote
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
    
    # Логируем redirect_uri для отладки
    print(f"[OAuth] Redirect URI: {YANDEX_REDIRECT_URI}")
    print(f"[OAuth] Client ID: {YANDEX_CLIENT_ID[:10]}...")
    
    # Правильно кодируем параметры URL
    params = {
        "response_type": "code",
        "client_id": YANDEX_CLIENT_ID,
        "redirect_uri": YANDEX_REDIRECT_URI,
    }
    
    auth_url = f"https://oauth.yandex.ru/authorize?{urlencode(params)}"
    print(f"[OAuth] Auth URL: {auth_url}")
    
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
        print(f"[OAuth] Callback received, code: {code[:20] if code else 'None'}...")
        oauth_service = OAuthService(db)
        yandex_data = await oauth_service.get_yandex_user_info(code)
        
        if not yandex_data:
            print("[OAuth] Failed to get user info from Yandex")
            return RedirectResponse(
                url=f"{FRONTEND_URL}/login?error=oauth_failed"
            )
        
        print(f"[OAuth] Yandex data received: id={yandex_data.get('id')}, email={yandex_data.get('default_email')}, login={yandex_data.get('login')}")
        user = oauth_service.get_or_create_user_from_yandex(yandex_data)
        print(f"[OAuth] User processed: id={user.id}, username={user.username}, email={user.email}")
        token_data = oauth_service.create_oauth_token(user)
        
        # Правильно кодируем токен для URL
        encoded_token = quote(token_data['access_token'], safe='')
        
        # Перенаправляем на фронтенд с токеном в URL параметре
        # Фронтенд должен будет сохранить токен и перенаправить пользователя
        redirect_url = f"{FRONTEND_URL}/login?token={encoded_token}&success=true"
        print(f"[OAuth] Redirecting to: {redirect_url[:100]}...")
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        print(f"Ошибка при обработке OAuth callback: {e}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?error=oauth_error"
        )
