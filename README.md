# Movie recommendation system
Сначала создайте .env файл по примеру файла .example.env и при надобности замените url к базе данных, затем

Для запуска перейдите в корневую папку movie-recommender-system и введите команду:

```docker-compose up --build -d ```

После этого создадутся и запустятся докер-контейнеры

Возможно нужно будет обновить миграции для бд, для этого напишите команды:

```docker exec moviehub_backend alembic revision --autogenerate -m "some change"```

```docker exec moviehub_backend alembic upgrade head```

Миграции применятся и все должно работать исправно, фронтенд сайта будет доступен по адресу: http://localhost:5173/

API документация доступна по адресу http://localhost:8000/api/docs

Затем чтобы остановить контетйнеры напишите команду:

```docker-compose stop```