from typing import Callable
from fastapi import FastAPI, Request
from sqlalchemy.orm import Session
from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routers.users import router as users_router
from app.api.routers.movies import router as movies_router
from app.api.routers.reviews import router as reviews_router
from app.api.routers.lists import router as lists_router
from app.api.routers.admin_stats import router as admin_stats_router

from app.db.session import get_db
from app.log_to_db import log_page_view

app = FastAPI(
    title="MovieHub API",
    version="1.0.0",
    description="Backend API для аналога Кинопоиска/Letterboxd",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ... (Настройка CORS и роутеров остается без изменений) ...

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(movies_router, prefix="/api/movies", tags=["Movies"])
app.include_router(reviews_router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(lists_router, prefix="/api/lists", tags=["Lists"])
app.include_router(admin_stats_router, prefix="/api", tags=["Admin"])


@app.middleware("http")
async def log_page_view_middleware(request: Request, call_next: Callable) -> Response:
    """
    Перехватывает все HTTP-запросы и записывает их в лог.
    """
    # 1. Выполняем запрос (call_next всегда асинхронный)
    response = await call_next(request)

    path = request.url.path

    # 2. Исключаем служебные и статические пути
    if (
            path.startswith("/static")
            or path.startswith("/api/docs")
            or path.startswith("/api/openapi.json")
            or path.startswith("/api/redoc")
            or path == "/api/health"
    ):
        return response

    # 3. Синхронная запись в БД (с использованием генератора get_db)
    try:
        # Получаем сессию, используя генератор get_db (как в Depends)
        db_generator = get_db()
        db: Session = next(db_generator)  # Получаем сессию из генератора

        # Выполняем синхронное логирование
        log_page_view(db, request, path)
        try:
            next(db_generator)
        except StopIteration:
            pass

    except Exception as db_exc:
        print(f"Ошибка при записи лога посещения в БД: {db_exc}")

    # 4. Возвращаем ответ
    return response


@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в MovieHub API!",
        "version": "1.0.0",
        "docs_url": "http://localhost:8000/api/docs"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
