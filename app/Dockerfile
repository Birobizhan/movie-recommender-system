# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY ./requirements.txt /app/requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY ./app /app/app

# Команда запуска (используется в docker-compose, но полезна для standalone)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
