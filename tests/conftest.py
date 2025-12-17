import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, TypeDecorator, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.sqlite import JSON
import json

from app.db.base import Base
from app.main import app
from app.db.session import get_db

# Импортируем все модели для создания схемы БД
from app.models import movie, review, user, list, analytics  # noqa: F401


# TypeDecorator для преобразования ARRAY в JSON для SQLite
class ArrayAsJSON(TypeDecorator):
    """Преобразует PostgreSQL ARRAY в JSON для SQLite."""
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(ARRAY(String))
        else:
            return dialect.type_descriptor(JSON)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        return json.dumps(value) if value else None

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        if isinstance(value, str):
            return json.loads(value) if value else None
        return value


# Создаем тестовую БД в памяти (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Заменяем ARRAY на JSON для SQLite при создании таблиц
@event.listens_for(engine, "connect", insert=True)
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Настройка SQLite для работы с JSON."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Функция для замены ARRAY на JSON в метаданных перед созданием таблиц
def patch_metadata_for_sqlite():
    """Заменяет ARRAY на ArrayAsJSON в метаданных для SQLite."""
    for table in Base.metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, ARRAY):
                # Заменяем ARRAY на ArrayAsJSON
                column.type = ArrayAsJSON()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Создает тестовую БД для каждого теста."""
    # Применяем патч для SQLite перед созданием схемы
    patch_metadata_for_sqlite()
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Создает тестовый клиент с переопределенной БД."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Тестовые данные пользователя."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }


@pytest.fixture
def test_movie_data():
    """Тестовые данные фильма."""
    return {
        "kp_id": 12345,
        "title": "Тестовый фильм",
        "english_title": "Test Movie",
        "kp_rating": 8.5,
        "imdb_rating": 8.0,
        "year_release": 2020,
        "genres": ["Драма", "Комедия"],
        "description": "Описание тестового фильма"
    }
