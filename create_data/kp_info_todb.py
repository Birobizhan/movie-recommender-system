import re
import requests
from environs import Env
import json

env = Env()
env.read_env()
KINOPISK_KEY = env("KINOPOISK_TOKEN")
BACKEND_API_URL = "http://localhost:8000/api"

HEADERS_KP = {
    'X-API-KEY': KINOPISK_KEY,
    'accept': 'application/json'
}

HEADERS_BACKEND = {
    'Content-Type': 'application/json'
}


def safe_float(s):
    """Преобразует строку в float, возвращая 0.0, если строка пуста или не является числом."""
    try:
        if s is None or s.strip() == '':
            return 0.0
        return float(s.strip())
    except ValueError:
        return 0.0


def safe_int(s):
    """Преобразует строку в int, возвращая 0, если строка пуста или не является числом."""
    try:
        if s is None:
            return 0
        return int(s)
    except ValueError:
        return 0


def process_and_add_to_db(input_filename):
    """
    Обрабатывает данные фильмов, запрашивает информацию через API Кинопоиска
    и отправляет данные на ваш бэкенд для сохранения в БД.
    """
    MOVIE_CREATE_URL = f'{BACKEND_API_URL}/movies/'

    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            information = f.readlines()
            print(f"Начало обработки {len(information)} строк...")
    except FileNotFoundError:
        print(f"Ошибка: Файл {input_filename} не найден.")
        return

    for i, line in enumerate(information):
        res = re.split(r',(?=\S)', line.strip())

        if len(res) < 10:
            print(f"Пропуск строки {i + 1}: Недостаточно данных в исходном CSV ({len(res)}).")
            continue

        try:

            kp_rating = safe_float(res[5])
            film_id_str = res[6].strip()
            imdb_rating = safe_float(res[8])
            critics_rating = safe_float(res[9])

            film_id = safe_int(film_id_str)

        except IndexError:
            print(
                f"Пропуск строки {i + 1}: Ошибка доступа к индексу при парсинге исходного CSV. Проверьте структуру строки.")
            continue

        if film_id == 0:
            print(f"Пропуск строки {i + 1}: Не удалось извлечь Film ID.")
            continue

        user_rating = 0.0

        url_kp = f'https://api.kinopoisk.dev/v1.4/movie/{film_id}'

        try:
            response_kp = requests.get(url_kp, headers=HEADERS_KP, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса к Kinopoisk API для ID {film_id}: {e}")
            continue

        if response_kp.status_code == 200:
            try:
                data = response_kp.json()
            except json.JSONDecodeError:
                print(f"Ошибка декодирования JSON для ID {film_id}")
                continue


            fees_data = data.get('fees', {}).get('world', {})
            fees_world = f"{fees_data.get('value') or ''}{fees_data.get('currency') or ''}" if fees_data.get(
                'value') else None

            budget_data = data.get('budget', {})
            budget = f"{budget_data.get('value') or ''}{budget_data.get('currency') or ''}" if budget_data.get(
                'value') else None

            votes = data.get('votes', {})
            sum_votes = safe_int(votes.get('kp', 0)) + safe_int(votes.get('imdb', 0)) + safe_int(
                votes.get('filmCritics', 0))

            genres = [genre.get('name') for genre in data.get('genres', []) if genre.get('name')]
            countries = [country.get('name') for country in data.get('countries', []) if country.get('name')]

            persons_list = data.get('persons', [])
            director = []
            persons = []

            for person in persons_list:
                profession = person.get('profession', '')
                name = person.get('name')
                person_id = person.get('id')

                if person_id and name:
                    if profession == 'режиссеры' and not director:
                        director = [person_id, name]
                    elif len(persons) < 10:
                        persons.append([person_id, name])

            ratings = []
            if kp_rating > 0: ratings.append(kp_rating)
            if imdb_rating > 0: ratings.append(imdb_rating)
            if critics_rating > 0: ratings.append(critics_rating)

            if ratings:
                combined_rating = round(sum(ratings) / len(ratings), 1)
            else:
                combined_rating = 0.0
            description = None
            if data.get('description', ''):
                description = data.get('description', '').replace('\n', ' ').replace('\r', '').strip() or None
            movie_data = {
                "kp_id": film_id_str,
                "title": data.get('name'),
                "english_title": data.get('enName'),
                "kp_rating": kp_rating,
                "imdb_rating": imdb_rating,
                "critics_rating": critics_rating,
                "user_rating": user_rating,

                "fees_world": fees_world,
                "sum_votes": sum_votes,
                "poster_url": data.get('poster', {}).get('url') or data.get('poster', {}).get('previewUrl') or None,
                "movie_length": data.get('movieLength'),
                "description": description,
                "world_premiere": data.get('premiere', {}).get('world'),
                "budget": budget,
                "year_release": data.get('year'),
                "genres": genres,
                "countries": countries,
                "persons": persons,
                "director": director,
                "age_rating": data.get('ageRating'),
                "combined_rating": combined_rating
            }
            try:
                response_db = requests.post(
                    MOVIE_CREATE_URL,
                    headers=HEADERS_BACKEND,
                    json=movie_data,
                    timeout=10
                )

                if response_db.status_code in [200, 201]:
                    print(f"Успешно добавлен фильм ID: {film_id} в БД. Статус: {response_db.status_code}")
                else:
                    print(
                        f"Ошибка добавления в БД для ID {film_id}. Статус: {response_db.status_code}. Ответ: {response_db.text}")

            except requests.exceptions.RequestException as e:
                print(f"Ошибка POST запроса к бэкенду для ID {film_id}: {e}")

        else:
            print(
                f"Ошибка API Кинопоиска для фильма ID: {film_id}. Статус: {response_kp.status_code}. Ответ: {response_kp.text}")


process_and_add_to_db('genre_with_info/Исторический.csv')