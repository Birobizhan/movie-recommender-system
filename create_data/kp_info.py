import re
import requests
from environs import Env

all_info = []

with open(f'genre_with_info/Проверка.csv', 'r', encoding='utf-8') as f:
    information = f.readlines()
    for i in range(0, len(information)):
        res = re.split(r',(?=\S)', information[i])
        film_id = res[6]
        url = f'https://api.kinopoisk.dev/v1.4/movie/{film_id}'
        params = {
            'page': 1,
            'limit': 10,
            'query': f'{film_id}'
        }
        env = Env()
        env.read_env()
        kinopoisk_key = env("KINOPOISK_TOKEN")
        headers = {
            'X-API-KEY': f'{kinopoisk_key}',
            'accept': 'application/json'
        }
        info_to_db = [res[6], res[7], res[5], res[8], res[9], 'our_site_rating']
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        if response.status_code == 200:
            data = response.json()  # Предполагаем, что data получается так

            # 1. Безопасное извлечение простых значений
            film_name = data.get('name')
            poster = data.get('poster', {}).get('url')
            movie_length = data.get('movieLength')
            description = data.get('description')
            world_premiere = data.get('premiere', {}).get('world')
            year_release = data.get('year')
            ageRating = data.get('ageRating')

            # 2. Безопасное извлечение сборов (Fees)
            fees_data = data.get('fees', {}).get('world', {})
            fees_world = fees_data.get('value')
            fees_currency = fees_data.get('currency')
            fees = f"{fees_world or ''}{fees_currency or ''}" if fees_world else "N/A"

            # 3. Безопасное извлечение бюджета (Budget)
            budget_data = data.get('budget', {})
            budget_value = budget_data.get('value')
            budget_curr = budget_data.get('currency')
            budget = f"{budget_value or ''}{budget_curr or ''}" if budget_value else "N/A"

            # 4. Безопасное извлечение и суммирование голосов
            votes = data.get('votes', {})
            # Используем .get() с дефолтом 0, чтобы гарантировать, что это число
            kp_votes = votes.get('kp', 0)
            imdb_votes = votes.get('imdb', 0)
            filmCritics_votes = votes.get('filmCritics', 0)
            sum_votes = kp_votes + imdb_votes + filmCritics_votes

            # 5. Генераторы списков (ОК)
            genres = [genre.get('name') for genre in data.get('genres', []) if genre.get('name')]
            countries = [country.get('name') for country in data.get('countries', []) if country.get('name')]

            # 6. Обработка персон (Режиссер + 10 первых)
            persons = data.get('persons', [])
            persons_to_db = []
            director = None  # Инициализируем как None
            counter = 0

            for person in persons:
                profession = person.get('profession')
                name = person.get('name')
                person_id = person.get('id')

                if profession == 'режиссеры' and director is None:
                    # Находим первого режиссера
                    director = [person_id, name]
                elif counter < 10 and person_id and name:
                    # Добавляем до 10 других персон
                    persons_to_db.append([person_id, name])
                    counter += 1

            # 7. Похожие фильмы
            similarMovies = [[movie.get('id'), movie.get('name')]
                             for movie in data.get('similarMovies', [])
                             if movie.get('id') and movie.get('name')]

            # 8. Сборка результата в СЛОВАРЬ (Рекомендуется!)
            film_info = {
                "film_name": film_name,
                "fees": fees,
                "sum_votes": sum_votes,
                "poster": poster,
                "movie_length": movie_length,
                "description": description,
                "world_premiere": world_premiere,
                "budget": budget,
                "year_release": year_release,
                "genres": genres,
                "countries": countries,
                "persons": persons_to_db,
                "director": director,
                "ageRating": ageRating,
                "similarMovies": similarMovies
            }
            all_info.append(film_info)
            print(film_info)

# Сильнее,Биографический,Драма,Спортивные легенды,Современное кино (2000–2020), kp_rating
# id_kinopoisk,name_english, imdb_rating, filmCrtitics_rating