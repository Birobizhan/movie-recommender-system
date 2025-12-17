from sqlalchemy.orm import Session
from starlette.requests import Request

from app.models import PageViewLog


def log_page_view(db: Session, request: Request, path: str):
    """
    Создает и сохраняет запись лога в БД.
    """
    # В реальном приложении user_id должен извлекаться из состояния запроса,
    # которое устанавливается после успешной аутентификации (например, в зависимости).
    # Мы используем getattr для безопасного извлечения.
    user_id = getattr(request.state, "user_id", None)

    log_entry = PageViewLog(
        path=path,
        user_id=user_id
    )
    print(f'add {log_entry}')
    db.add(log_entry)
    db.commit()
