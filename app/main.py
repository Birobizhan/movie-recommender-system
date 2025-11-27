from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # 1. Импорт для раздачи картинок
from contextlib import asynccontextmanager

# Импортируем настройки БД (предполагаем, что они у вас в app/database.py)
# Если файла database нет, закомментируйте эти строки пока что
from app.database import engine, Base

from app.routes.users import router as users_router
from app.routes.movies import router as movies_router
from app.routes.reviews import router as reviews_router
from app.routes.lists import router as lists_router


app = FastAPI(
    title="MovieHub API",
    version="1.0.0",
    description="Backend API для аналога Кинопоиска/Letterboxd",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# 3. CORS: Добавляем порты для Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Стандартный React
        "http://localhost:5173",      # <--- ВАЖНО: Стандартный порт Vite
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Подключение статики (Картинок)
# Теперь файлы из папки "static" будут доступны по адресу /static/filename.jpg
# Создайте папку 'static' в корне проекта, если её нет.
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    print("⚠️ Папка 'static' не найдена. Создайте её для хранения постеров.")

# Подключаем роутеры
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(movies_router, prefix="/api/movies", tags=["Movies"])
app.include_router(reviews_router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(lists_router, prefix="/api/lists", tags=["Lists"])

@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в MovieHub API!",
        "version": "1.0.0",
        "docs_url": "http://localhost:8000/api/docs"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "API работает корректно"}

if __name__ == "__main__":
    import uvicorn
    # reload=True нужен только для разработки
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)