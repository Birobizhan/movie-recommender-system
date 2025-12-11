import os
import re
import requests
import json
from pathlib import Path
from environs import Env
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

# === Настройка ===
env = Env()
env.read_env()

# Получаем список токенов Кинопоиска
KINOPOISK_TOKENS = [t.strip() for t in env("KINOPOISK_TOKEN").split(",") if t.strip()]
if not KINOPOISK_TOKENS:
    raise ValueError("Не заданы токены KINOPOISK_TOKENS в .env")

DATABASE_URL = env("DATABASE_URL_LOCAL")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

HEADERS_KP_BASE = {'accept': 'application/json'}
HEADERS_DB = {'Content-Type': 'application/json'}

# === Вспомогательные функции ===
def safe_float(s):
    try:
        if s is None or (isinstance(s, str) and s.strip() == ''):
            return 0.0
        return float(s)
    except (ValueError, TypeError):
        return 0.0

def safe_int(s):
    try:
        return int(s) if s is not None else 0
    except (ValueError, TypeError):
        return 0

# === Основная логика ===
def extract_film_data_from_line(line: str, current_line_num: int):
    """Разбирает строку CSV и возвращает film_id и рейтинговые данные."""
    line = line.strip()
    if not line:
        print(f"  Пропуск пустой строки {current_line_num}")
        return None

    # Разделяем по точке с запятой
    res = line.split(';')
    if len(res) < 10:
        print(f"  Пропуск строки {current_line_num}: недостаточно данных ({len(res)})")
        return None

    try:
        kp_rating = safe_float(res[5])
        film_id_str = res[6].strip()
        imdb_rating = safe_float(res[8])
        critics_rating = safe_float(res[9])
        film_id = safe_int(film_id_str)

        if film_id == 0:
            print(f"  Пропуск строки {current_line_num}: Film ID не распознан")
            return None

        return {
            "film_id": film_id,
            "film_id_str": film_id_str,
            "kp_rating": kp_rating,
            "imdb_rating": imdb_rating,
            "critics_rating": critics_rating
        }
    except Exception as e:
        print(f"  Ошибка парсинга строки {current_line_num}: {e}")
        return None

def fetch_movie_from_kinopoisk(film_id: int, token_index: int):
    """Запрашивает фильм у Кинопоиска, возвращает (data, новый_token_index, success)."""
    token = KINOPOISK_TOKENS[token_index]
    headers = {**HEADERS_KP_BASE, 'X-API-KEY': token}
    url = f'https://api.kinopoisk.dev/v1.4/movie/{film_id}'

    try:
        resp = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"  Ошибка сети при запросе ID {film_id}: {e}")
        return None, token_index, False

    if resp.status_code == 200:
        try:
            data = resp.json()
            return data, token_index, True
        except json.JSONDecodeError:
            print(f"  Некорректный JSON для ID {film_id}")
            return None, token_index, False

    elif resp.status_code == 403:
        # Токен исчерпан — пробуем следующий
        next_index = (token_index + 1) % len(KINOPOISK_TOKENS)
        print(f"  Токен исчерпан (403). Переключаемся на токен #{next_index + 1}")
        return None, next_index, False

    else:
        print(f"  Ошибка API Кинопоиска для ID {film_id}: {resp.status_code} – {resp.text}")
        return None, token_index, False

def prepare_movie_record(raw_data, ratings_info):
    """Формирует запись фильма для вставки в БД."""
    data = raw_data

    if data.get('type') != 'movie':
        print(f"    Пропуск: тип = {data.get('type')}, не 'movie'")
        return None

    # Финансы
    fees_data = (data.get('fees') or {}).get('world') or {}
    fees_world = f"{fees_data.get('value', '')}{fees_data.get('currency', '')}" if fees_data.get('value') else None

    budget_data = data.get('budget') or {}
    budget = f"{budget_data.get('value', '')}{budget_data.get('currency', '')}" if budget_data.get('value') else None

    # Голоса
    votes = data.get('votes', {})
    sum_votes = (
        safe_int(votes.get('kp', 0)) +
        safe_int(votes.get('imdb', 0)) +
        safe_int(votes.get('filmCritics', 0))
    )

    # Жанры и страны
    genres = [g.get('name') for g in data.get('genres', []) if g.get('name')]
    countries = [c.get('name') for c in data.get('countries', []) if c.get('name')]

    # Персоны — только имена
    persons_list = data.get('persons', [])
    director = None
    persons = []

    for p in persons_list:
        name = p.get('name')
        prof = p.get('profession', '')
        if name:
            if prof == 'режиссеры' and director is None:
                director = name
            elif len(persons) < 10:
                persons.append(name)

    # Рейтинг
    ratings = []
    if ratings_info["kp_rating"] > 0: ratings.append(ratings_info["kp_rating"])
    if ratings_info["imdb_rating"] > 0: ratings.append(ratings_info["imdb_rating"])
    if ratings_info["critics_rating"] > 0: ratings.append(ratings_info["critics_rating"])
    combined_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0.0

    # Описание
    desc = data.get('description') or ''
    if desc:
        desc = desc.replace('\n', ' ').replace('\r', '').strip() or None
    else:
        desc = None

    return {
        "kp_id": ratings_info["film_id_str"],
        "title": data.get('name'),
        "english_title": data.get('enName'),
        "kp_rating": ratings_info["kp_rating"],
        "imdb_rating": ratings_info["imdb_rating"],
        "critics_rating": ratings_info["critics_rating"],
        "site_rating": 0.0,
        "fees_world": fees_world,
        "sum_votes": sum_votes,
        "poster_url": (data.get('poster') or {}).get('url') or (data.get('poster') or {}).get('previewUrl'),
        "movie_length": data.get('movieLength'),
        "description": desc,
        "world_premiere": (data.get('premiere') or {}).get('world'),
        "budget": budget,
        "year_release": data.get('year'),
        "genres": genres,
        "countries": countries,
        "persons": persons,
        "director": director,
        "age_rating": data.get('ageRating'),
        "combined_rating": combined_rating
    }

def insert_movie_to_db(movie_record, session):
    try:
        # НЕ сериализуем в JSON! Передаём списки как есть.
        insert_query = text("""
            INSERT INTO movies (
                kp_id, title, english_title, kp_rating, imdb_rating, critics_rating,
                site_rating, fees_world, sum_votes, poster_url, movie_length,
                description, world_premiere, budget, year_release, genres,
                countries, persons, director, age_rating, combined_rating
            ) VALUES (
                :kp_id, :title, :english_title, :kp_rating, :imdb_rating, :critics_rating,
                :site_rating, :fees_world, :sum_votes, :poster_url, :movie_length,
                :description, :world_premiere, :budget, :year_release, :genres,
                :countries, :persons, :director, :age_rating, :combined_rating
            ) ON CONFLICT (kp_id) DO NOTHING;
        """)

        session.execute(insert_query, {
            "kp_id": movie_record["kp_id"],
            "title": movie_record["title"],
            "english_title": movie_record["english_title"],
            "kp_rating": movie_record["kp_rating"],
            "imdb_rating": movie_record["imdb_rating"],
            "critics_rating": movie_record["critics_rating"],
            "site_rating": movie_record["site_rating"],
            "fees_world": movie_record["fees_world"],
            "sum_votes": movie_record["sum_votes"],
            "poster_url": movie_record["poster_url"],
            "movie_length": movie_record["movie_length"],
            "description": movie_record["description"],
            "world_premiere": movie_record["world_premiere"],
            "budget": movie_record["budget"],
            "year_release": movie_record["year_release"],
            "genres": movie_record["genres"],          # ← list, не строка!
            "countries": movie_record["countries"],    # ← list
            "persons": movie_record["persons"],        # ← list of lists
            "director": movie_record["director"],      # ← list
            "age_rating": movie_record["age_rating"],
            "combined_rating": movie_record["combined_rating"]
        })
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"  Ошибка вставки в БД: {e}")
        return False

def process_file(filepath: Path, start_line: int = 1):
    """Обрабатывает один CSV-файл."""
    print(f"\n📁 Обработка файла: {filepath.name}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"  ❌ Не удалось прочитать файл: {e}")
        return

    # Начинаем с указанной строки (1-индексировано)
    lines_to_process = lines[start_line - 1:]
    current_token_index = 0

    session = SessionLocal()
    try:
        for i, line in enumerate(lines_to_process):
            current_line_num = i + start_line

            # Парсим строку
            rating_info = extract_film_data_from_line(line, current_line_num)
            if not rating_info:
                continue

            film_id = rating_info["film_id"]

            # Запрашиваем данные у Кинопоиска
            data = None
            attempts = 0
            max_attempts = len(KINOPOISK_TOKENS) + 1
            while attempts < max_attempts:
                data, current_token_index, success = fetch_movie_from_kinopoisk(film_id, current_token_index)
                if success:
                    break
                elif data is None and attempts < max_attempts - 1:
                    attempts += 1
                    continue
                else:
                    break

            if not data:
                print(f"  ❌ Пропуск ID {film_id} (строка {current_line_num}): не удалось получить данные")
                continue

            # Проверяем тип
            if data.get('type') != 'movie':
                print(f"  ⚠️ Пропуск ID {film_id}: тип = {data.get('type')}")
                continue

            # Формируем запись
            movie_record = prepare_movie_record(data, rating_info)
            if not movie_record:
                continue

            # Вставляем в БД
            if insert_movie_to_db(movie_record, session):
                print(f"  ✅ Добавлен фильм ID {film_id} (строка {current_line_num})")
            else:
                print(f"  ❌ Ошибка вставки фильма ID {film_id}")

    finally:
        session.close()

def main():
    folder = Path("genre_with_info")
    if not folder.exists():
        print(f"Папка {folder} не найдена!")
        return

    csv_files = sorted([f for f in folder.glob("*.csv") if f.is_file()])
    if not csv_files:
        print("CSV-файлы не найдены в папке genre_with_info")
        return

    print(f"Найдено {len(csv_files)} CSV-файлов. Начинаем обработку...")

    for csv_file in csv_files:
        process_file(csv_file, start_line=1)

    print("\n✅ Обработка завершена.")

if __name__ == "__main__":
    main()