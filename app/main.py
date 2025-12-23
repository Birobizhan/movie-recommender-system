from typing import Callable
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routers.users import router as users_router
from app.api.routers.movies import router as movies_router
from app.api.routers.reviews import router as reviews_router
from app.api.routers.lists import router as lists_router
from app.api.routers.admin_stats import router as admin_stats_router
from app.api.routers.oauth import router as oauth_router
from app.db.session import get_db
from app.log_to_db import log_page_view, log_error

app = FastAPI(
    title="MovieHub API",
    version="1.0.0",
    description="Backend API для аналога Кинопоиска/Letterboxd",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


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
app.include_router(oauth_router, prefix="/api", tags=["OAuth"])


@app.middleware("http")
async def log_page_view_middleware(request: Request, call_next: Callable) -> Response:
    """
    Перехватывает все HTTP-запросы и записывает их в лог
    Также логирует ошибки в ErrorLog
    """
    try:
        response = await call_next(request)
    except Exception as exc:
        # Логируем исключение в БД
        try:
            db_generator = get_db()
            db: Session = next(db_generator)
            log_error(db, exc, level="ERROR")
            try:
                next(db_generator)
            except StopIteration:
                pass
        except Exception as db_exc:
            print(f"Ошибка при записи ошибки в БД: {db_exc}")
        
        raise

    path = request.url.path

    # 2. Исключаем служебные и статические пути
    if (
            path.startswith("/static")
            or path.startswith("/api/docs")
            or path.startswith("/api/openapi.json")
            or path.startswith("/api/redoc")
    ):
        return response

    try:
        db_generator = get_db()
        db: Session = next(db_generator)

        log_page_view(db, request, path)
        try:
            next(db_generator)
        except StopIteration:
            pass

    except Exception as db_exc:
        print(f"Ошибка при записи лога посещения в БД: {db_exc}")

    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Глобальный обработчик исключений, который логирует все ошибки в БД
    """
    try:
        db_generator = get_db()
        db: Session = next(db_generator)
        
        level = "ERROR"
        if isinstance(exc, HTTPException):
            if exc.status_code >= 500:
                level = "ERROR"
            elif exc.status_code >= 400:
                level = "WARNING"
        
        log_error(db, exc, level=level)
        try:
            next(db_generator)
        except StopIteration:
            pass
    except Exception as db_exc:
        print(f"Ошибка при записи ошибки в БД: {db_exc}")
    
    # Если это HTTPException, возвращаем стандартный ответ FastAPI
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    # Для остальных исключений возвращаем 500
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


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
