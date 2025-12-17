from datetime import datetime, timedelta
from typing import Any, Dict

import aiohttp
import requests
from sqlalchemy import text
from sqlalchemy.orm import Session
from environs import Env

from app.repositories.admin_stats import AdminStatsRepository

env = Env()
env.read_env()


async def check_frontend(url: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                return response.status == 200
    except Exception:
        return False


class AdminStatsService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AdminStatsRepository(db)

    # --- STATUS / HEALTH ---
    async def get_status(self):
        """
        Проверяет статус API, БД и возвращает общий статус.
        """
        db_status = False
        db_error = None

        # --- 1. Проверка БД ---
        try:
            # Выполняем простейший запрос, который не изменяет данные
            self.db.execute(text("SELECT 1"))
            db_status = True
        except Exception as e:
            db_error = str(e)
            # Важно: зависимость get_db позаботится о закрытии сессии

        # --- 2. Проверка API (Backend) ---
        # Если мы дошли до этого места, API работает
        api_status = True
        frontend_ok = await check_frontend("http://frontend:5173/")
        # --- 3. Проверка Frontend (заглушка) ---
        # Если фронтенд - это отдельный сервис, который не критичен для работы API,
        # можно просто указать его статус как "unknown" или "ok" по умолчанию.

        # --- Общий статус ---
        overall_status = "healthy"
        if not db_status:
            overall_status = "degraded"  # Ухудшенное состояние

        return {
            "status": overall_status,
            "services": {
                "backend_api": {
                    "status": "ok",
                    "message": "API запущен и отвечает"
                },
                "database": {
                    "status": "ok" if db_status else "error",
                    "message": "Соединение с БД установлено" if db_status else f"Ошибка соединения: {db_error}"
                },
                "frontend_ui": {
                    "status": "ok" if frontend_ok else "error",
                    "message": "Фронтенд работает исправно" if db_status else f"Ошибка фронта"
                }
            }
        }
    # def get_status(self) -> Dict[str, Any]:
    #     backend_ok = self.repo.db_health()
    #
    #     # Проверка фронтенда (опционально, через HTTP GET)
    #     frontend_status: str = "unknown"
    #     frontend_ok = None
    #
    #     frontend_url = env.str("FRONTEND_URL", None)
    #     if frontend_url:
    #         try:
    #             resp = requests.get(frontend_url, timeout=3)
    #             frontend_ok = resp.ok
    #         except Exception:
    #             frontend_ok = False
    #     if frontend_ok is True:
    #         frontend_status = "OK"
    #     elif frontend_ok is False:
    #         frontend_status = "ERROR"
    #
    #     all_ok = backend_ok and (frontend_ok in (True, None))
    #
    #     return {
    #         "overall": "OK" if all_ok else "ERROR",
    #         "backend": "OK" if backend_ok else "ERROR",
    #         "frontend": frontend_status,
    #     }

    def get_db_check(self) -> Dict[str, Any]:
        stats = self.repo.db_basic_stats()
        return {"status": "OK", **stats}

    def get_last_errors(self, limit: int = 10) -> Dict[str, Any]:
        errors = self.repo.get_last_errors(limit=limit)
        return {
            "count": len(errors),
            "items": [
                {
                    "id": e.id,
                    "level": e.level,
                    "message": e.message,
                    "details": e.details,
                    "created_at": e.created_at,
                }
                for e in errors
            ],
        }

    # --- MOVIES / REVIEWS / USERS ---

    def get_top_movies(self, period: str = "24h") -> Dict[str, Any]:
        now = datetime.utcnow()
        if period == "7d":
            since = now - timedelta(days=7)
        else:
            since = now - timedelta(hours=24)

        rows = self.repo.top_movies_by_views(since=since, limit=10)
        return {
            "period": period,
            "items": [
                {
                    "movie_id": movie.id,
                    "title": movie.title,
                    "views": views,
                }
                for movie, views in rows
            ],
        }

    def get_new_reviews_today(self) -> Dict[str, Any]:
        count = self.repo.new_reviews_count_today()
        return {"today_reviews": count}

    def get_new_users(self) -> Dict[str, Any]:
        return self.repo.new_users_stats()

    def get_active_users(self) -> Dict[str, Any]:
        count = self.repo.active_users_last_7_days()
        return {"active_users_last_7_days": count}

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        stats = self.repo.user_stats(user_id)
        if not stats:
            raise LookupError("User not found")
        return stats

    # --- SEARCH / PAGES ---

    def get_search_stats_none(self) -> Dict[str, Any]:
        rows = self.repo.top_search_queries(limit=5, only_without_results=True)
        return {
            "items": [
                {"query": query, "count": cnt}
                for query, cnt in rows
            ]
        }

    def get_top_search(self) -> Dict[str, Any]:
        rows = self.repo.top_search_queries(limit=5, only_without_results=False)
        return {
            "items": [
                {"query": query, "count": cnt}
                for query, cnt in rows
            ]
        }

    def get_top_pages(self) -> Dict[str, Any]:
        rows = self.repo.top_pages(limit=10)
        return {
            "items": [
                {"path": path, "count": cnt}
                for path, cnt in rows
            ]
        }

    # --- COMPOSITE REPORTS ---

    def get_full_report(self) -> Dict[str, Any]:
        status = self.get_status()
        db_check = self.get_db_check()
        errors = self.get_last_errors(limit=10)
        top_movies_24h = self.get_top_movies(period="24h")
        new_reviews = self.get_new_reviews_today()
        search_none = self.get_search_stats_none()
        top_search = self.get_top_search()
        new_users = self.get_new_users()
        active_users = self.get_active_users()
        top_pages = self.get_top_pages()

        return {
            "status": status,
            "db_check": db_check,
            "logs_errors": errors,
            "top_movies_24h": top_movies_24h,
            "new_reviews": new_reviews,
            "search_stats_none": search_none,
            "top_search": top_search,
            "new_users": new_users,
            "active_users": active_users,
            "top_pages": top_pages,
        }

    # --- AI REPORT ---

    def get_ai_report(self) -> Dict[str, Any]:
        """
        Отправляет полный отчёт в LLM и возвращает текстовый анализ.
        Требует настроенного OPENAI_API_KEY.
        """
        full_report = self.get_full_report()

        try:
            from openai import OpenAI

            client = OpenAI()
            prompt = (
                "Ниже приведён JSON с техническим отчётом о состоянии кино-сервиса. "
                "Сделай краткий анализ для администратора: опиши текущее состояние, "
                "возможные проблемы и 3-5 конкретных рекомендаций по улучшению.\n\n"
                f"Отчёт:\n{full_report}"
            )

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты аналитик данных для веб-сервиса с фильмами.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )

            analysis_text = response.choices[0].message.content
            return {
                "report": full_report,
                "analysis": analysis_text,
            }
        except Exception as exc:
            return {
                "report": full_report,
                "analysis": None,
                "error": str(exc),
            }
