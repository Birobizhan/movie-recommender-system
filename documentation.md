# Папка app/
Основные файлы приложения

1. main.py - Точка входа FastAPI приложения

Настройки CORS для React фронтенда

Подключение всех маршрутов API

Корневые эндпоинты (/health, /)


2. database.py - Конфигурация базы данных

SQLAlchemy настройки для SQLite

Создание engine и session factory

Функция get_db() для dependency injection


3. auth.py - Аутентификация и JWT

Хеширование паролей (bcrypt)

Создание и верификация JWT токенов

Настройки SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


4. dependencies.py - FastAPI зависимости

Зависимость get_current_user для JWT аутентификации

HTTPBearer для извлечения токена из заголовков


# Папка app/models/ - SQLAlchemy модели

1. user.py - Модель пользователя

class User(Base):

    # Поля: id, email, username, hashed_password, created_at

    # Связи: reviews, lists (one-to-many)


2. movie.py - Модель фильма

class Movie(Base):

    # Поля: id, title, year, genre, description, rating, poster_url

    # Связи: reviews (one-to-many)


3. review.py - Модель отзыва

class Review(Base):

    # Поля: id, content, rating, author_id, movie_id

    # Внешние ключи: author_id → users.id, movie_id → movies.id


4. list.py - Модель списка фильмов

class MovieList(Base):

    # Поля: id, title, description, owner_id

    # Связь many-to-many с Movie через list_movie_association


# Папка app/schemas/ - Pydantic схемы

1. user.py - Схемы для пользователей

UserBase       # Базовые поля (email, username)

UserCreate     # Для регистрации (+ password)

UserResponse   # Для ответов API (+ id, created_at)

UserLogin      # Для входа (email, password)

Token          # JWT ответ (access_token, token_type, user)


2. movie.py - Схемы для фильмов

MovieBase      # Базовые поля фильма

MovieResponse  # Ответ API (+ id)

MovieSearchFilters  # Параметры поиска


3. review.py - Схемы для отзывов

ReviewBase     # Базовые поля (content, rating)

ReviewCreate   # Для создания (+ movie_id)

ReviewResponse # Для ответов (+ id, author_id, movie_id, timestamps)


4. list.py - Схемы для списков

MovieListBase           # Базовые поля

MovieListCreate         # Для создания (+ movie_ids)

MovieListResponse       # Для ответов (+ id, owner_id, timestamps)

MovieListAddRemoveMovies # Для управления фильмами в списке


# Папка app/routes/ - API маршруты

1. users.py - Эндпоинты пользователей

POST /register     # Регистрация нового пользователя

POST /login        # Аутентификация, возвращает JWT

GET  /me           # Информация о текущем пользователе

GET  /{user_id}    # Публичный профиль пользователя


2. movies.py - Эндпоинты фильмов

GET /              # Список фильмов с фильтрацией

GET /search        # Поиск фильмов по названию

GET /{movie_id}    # Детальная информация о фильме

GET /{movie_id}/similar  # Похожие фильмы


3. reviews.py - Эндпоинты отзывов

POST   /              # Создание отзыва (требует аутентификации)

PUT    /{review_id}   # Обновление отзыва

DELETE /{review_id}   # Удаление отзыва

GET    /movie/{movie_id}  # Отзывы на фильм

GET    /user/{user_id}    # Отзывы пользователя


4. lists.py - Эндпоинты списков фильмов

POST   /              # Создание списка

GET    /{list_id}     # Получение списка с фильмами

PUT    /{list_id}     # Обновление списка

DELETE /{list_id}     # Удаление списка

POST   /{list_id}/movies    # Добавление фильмов в список

DELETE /{list_id}/movies    # Удаление фильмов из списка

GET    /user/{user_id}      # Списки пользователя


JWT Flow:
- Пользователь логинится через /api/users/login
- Сервер возвращает access_token
- Клиент включает токен в заголовки: Authorization: Bearer <token>
- Защищенные эндпоинты используют get_current_user dependency

