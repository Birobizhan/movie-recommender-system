
FROM python:3.10-slim

WORKDIR /src
ENV PYTHONPATH=/src
# 1. Сначала копируем зависимости (они в корне)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Копируем весь проект (папки app, static, alembic, main.py попадут внутрь)
# Благодаря .dockerignore папка kino-frontend сюда НЕ попадет
COPY . .

# 3. Запуск
# Предполагаем, что файл main.py лежит в КОРНЕ (рядом с папкой app)
# Если main.py внутри папки app, то команда будет: "app.main:app"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]