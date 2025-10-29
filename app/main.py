from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Импортируем роутеры напрямую из каждого файла
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
    openapi_url="/api/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "docs": "/api/docs"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "API работает корректно"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)