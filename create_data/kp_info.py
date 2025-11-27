import re
import requests
from environs import Env
import csv

# --- КОНСТАНТЫ И ИНИЦИАЛИЗАЦИЯ ---
env = Env()
env.read_env()
KINOPISK_KEY = env("KINOPOISK_TOKEN")

HEADERS = {
    'X-API-KEY': KINOPISK_KEY,
    'accept': 'application/json'
}


def process_and_write_data(input_filename, output_filename):
    """
    Обрабатывает данные фильмов, запрашивает информацию через API
    и записывает ее в CSV-файл с разделителем колонок ';'.
    """
    with open(input_filename, 'r', encoding='utf-8') as f:
        with open(output_filename, 'a', encoding='utf-8', newline='') as input_file:

            # Инициализация CSV-писателя
            # Используем точку с запятой (;) в качестве разделителя колонок
            csv_writer = csv.writer(input_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            information = f.readlines()

            print(f"Начало обработки {len(information)} строк...")

            for i, line in enumerate(information):
                # Используем ваш regex для разделения исходной строки
                res = re.split(r',(?=\S)', line.strip())

                if len(res) < 10:
                    print(f"Пропуск строки {i + 1}: Недостаточно данных в исходном CSV.")
                    continue

                film_id = res[6]
                url = f'https://api.kinopoisk.dev/v1.4/movie/{film_id}'

                params = {'query': film_id}

                # 2. Исходные данные
                initial_info = [
                    res[6], res[7], res[5], res[8], res[9].strip(), '0'
                ]

                # 3. Запрос к API
                response = requests.get(url, headers=HEADERS, params=params)

                if response.status_code == 200:
                    data = response.json()

                    # --- Извлечение и форматирование данных ---

                    # Обработка сборов и бюджета
                    fees_data = data.get('fees', {}).get('world', {})
                    fees = f"{fees_data.get('value') or ''}{fees_data.get('currency') or ''}" if fees_data.get(
                        'value') else "N/A"

                    budget_data = data.get('budget', {})
                    budget = f"{budget_data.get('value') or ''}{budget_data.get('currency') or ''}" if budget_data.get(
                        'value') else "N/A"

                    # Голоса
                    votes = data.get('votes', {})
                    sum_votes = votes.get('kp', 0) + votes.get('imdb', 0) + votes.get('filmCritics', 0)

                    # Списки (Жанры, Страны) - используем ', '.join() для внутреннего разделения
                    genres = ', '.join([genre.get('name') for genre in data.get('genres', []) if genre.get('name')])
                    countries = ', '.join(
                        [country.get('name') for country in data.get('countries', []) if country.get('name')])

                    # Персоны
                    persons_list = data.get('persons', [])
                    persons_to_db = []
                    director = [None, None]
                    counter = 0

                    for person in persons_list:
                        profession = person.get('profession')
                        name = person.get('name')
                        person_id = person.get('id')

                        if profession == 'режиссеры' and director[0] is None:
                            director = [person_id, name]
                        elif counter < 10 and person_id and name:
                            # Храним персон в формате ID:Name
                            persons_to_db.append(f"{person_id}:{name}")
                            counter += 1

                    persons_final = ', '.join(persons_to_db)  # Объединяем персон

                    # 8. Сборка строки API-данных
                    api_info_row = [
                        data.get('name'),
                        fees,
                        sum_votes,
                        data.get('poster', {}).get('url'),
                        data.get('movieLength'),
                        # Очищаем описание от переводов строк
                        data.get('description', '').replace('\n', ' ').replace('\r', '').strip(),
                        data.get('premiere', {}).get('world'),
                        budget,
                        data.get('year'),
                        genres,
                        countries,
                        persons_final,
                        director[0],
                        director[1],
                        data.get('ageRating')
                    ]

                    # 9. Объединение и запись
                    # Заменяем None на пустую строку
                    final_row = initial_info + [str(item) if item is not None else '' for item in api_info_row]

                    csv_writer.writerow(final_row)

                    print(f"✅ Успешно обработан фильм ID: {film_id}")

                else:
                    print(f"Ошибка API для фильма ID: {film_id}. Статус: {response.status_code}")


# Вызов функции
# Убедитесь, что пути 'genre_with_info/Проверка.csv' и 'movies_with_all_info/check.csv' верны
process_and_write_data(f'genre_with_info/Проверка.csv', f'movies_with_all_info/check.csv')