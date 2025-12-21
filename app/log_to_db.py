from sqlalchemy.orm import Session
from starlette.requests import Request
import traceback

from app.models.analytics import PageViewLog, ErrorLog


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


def log_error(db: Session, exception: Exception, level: str = "ERROR", details: str = None):
    """
    Создает и сохраняет запись об ошибке в БД.
    """
    try:
        error_message = str(exception)[:500]  # Ограничиваем длину сообщения
        error_details = details or traceback.format_exc()[:2000]  # Ограничиваем длину деталей
        
        log_entry = ErrorLog(
            level=level,
            message=error_message,
            details=error_details
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        # Если не удалось записать ошибку в БД, просто выводим в консоль
        print(f"Не удалось записать ошибку в БД: {e}")
        db.rollback()
