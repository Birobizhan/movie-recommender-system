from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.services.admin_stats import AdminStatsService

router = APIRouter(prefix="/admin", tags=["Admin"])


def get_service(db: Session = Depends(deps.get_db)) -> AdminStatsService:
    return AdminStatsService(db)


@router.get("/status")
async def status(service: AdminStatsService = Depends(get_service)):
    """
    /status - Проверка состояния всех сервисов (backend, db, frontend).
    """
    return await service.get_status()


@router.get("/db_check")
def db_check(service: AdminStatsService = Depends(get_service)):
    """
    /db_check - Проверка подключения к базе данных и базовая статистика.
    """
    return service.get_db_check()


@router.get("/logs_errors")
def logs_errors(
    limit: int = Query(10, ge=1, le=50),
    service: AdminStatsService = Depends(get_service),
):
    """
    /logs_errors - Последние критические ошибки из логов бэкенда.
    """
    return service.get_last_errors(limit=limit)


@router.get("/top_movies")
def top_movies(
    period: str = Query("24h", pattern="^(24h|7d)$"),
    service: AdminStatsService = Depends(get_service),
):
    """
    /top_movies - Топ-10 фильмов по просмотрам за период (24h или 7d).
    """
    return service.get_top_movies(period=period)


@router.get("/new_reviews")
def new_reviews(service: AdminStatsService = Depends(get_service)):
    """
    /new_reviews - Количество новых отзывов/рейтингов за сегодня.
    """
    return service.get_new_reviews_today()


@router.get("/search_stats_none")
def search_stats_none(service: AdminStatsService = Depends(get_service)):
    """
    /search_stats_none - Топ-5 популярных поисков, которые не дали результатов.
    """
    return service.get_search_stats_none()


@router.get("/top_search")
def top_search(service: AdminStatsService = Depends(get_service)):
    """
    /top_search - Топ-5 самых популярных поисковых запросов.
    """
    return service.get_top_search()


@router.get("/top_pages")
def top_pages(service: AdminStatsService = Depends(get_service)):
    """
    /top_pages - Топ-10 самых посещаемых страниц.
    """
    return service.get_top_pages()


@router.get("/new_users")
def new_users(service: AdminStatsService = Depends(get_service)):
    """
    /new_users - Кол-во новых регистраций за сегодня и за неделю.
    """
    return service.get_new_users()


@router.get("/active_users")
def active_users(service: AdminStatsService = Depends(get_service)):
    """
    /active_users - Кол-во активных пользователей за последние 7 дней.
    """
    return service.get_active_users()


@router.get("/user_stats/{user_id}")
def user_stats(
    user_id: int,
    service: AdminStatsService = Depends(get_service),
):
    """
    /user_stats [ID] - Сводная статистика по пользователю.
    """
    try:
        return service.get_user_stats(user_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/full_report")
def full_report(service: AdminStatsService = Depends(get_service)):
    """
    /full_report - Комплексный отчёт по основным метрикам.
    """
    return service.get_full_report()


@router.get("/ai_report")
def ai_report(service: AdminStatsService = Depends(get_service)):
    """
    /ai_report - Анализ полного отчёта с помощью LLM.
    """
    return service.get_ai_report()
