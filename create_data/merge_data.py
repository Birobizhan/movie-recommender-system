import csv
import os
import re
from pathlib import Path
import psycopg2
from psycopg2.extras import DictCursor, execute_values
from environs import Env

env = Env()
env.read_env()

# Пути к папкам
INPUT_DIR = Path('genre_with_info')
OUTPUT_DIR = Path('genre_with_dbinfo')

# Название таблицы в PostgreSQL
DB_TABLE_NAME = 'movies'

# Заголовки для итогового CSV-файла (объединение всех нужных полей)
HEADER = [
    'ID', 'Title_RU', 'Title_EN', 'Year', 'Age_Rating', 'Runtime', 'Image_URL', 'Synopsis',
    'DB_Genres', 'Countries', 'Director', 'Cast',
    'DB_Rating_1', 'DB_Rating_2', 'DB_Rating_3', 'Budget',
    'CSV_Title_RU', 'CSV_Category_1', 'CSV_Category_2', 'CSV_Category_3', 'CSV_Category_4',
    'CSV_Rating_1', 'CSV_Rating_2', 'CSV_Rating_3',
    'Source'
]


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def fetch_db_data(movie_ids):
    """
    Подключается к БД и извлекает данные для заданного списка ID.
    Возвращает словарь {movie_id: db_data}.
    """
    if not movie_ids:
        return {}

    db_data = {}
    conn = None
    try:
        conn = psycopg2.connect(env('DATABASE_URL_LOCAL'),
                                client_encoding='utf8'  # Явно указываем кодировку клиента
                                )

        # Используем DictCursor, чтобы получать данные как словари (по имени столбца)
        cursor = conn.cursor(cursor_factory=DictCursor)

        # Список столбцов, которые мы извлекаем из БД
        columns = [
            'kp_id', 'title', 'english_title', 'kp_rating', 'imdb_rating', 'critics_rating', 'site_rating',
            'fees_world', 'sum_votes', 'poster_url', 'movie_length', 'description', 'world_premiere',
            'budget', 'year_release', 'age_rating', 'genres', 'countries', 'persons', 'director', 'combined_rating'
        ]

        query = f"SELECT {', '.join(columns)} FROM {DB_TABLE_NAME} WHERE kp_id IN %s"

        # Преобразуем список ID в кортеж для SQL
        id_tuple = tuple(movie_ids)

        cursor.execute(query, (id_tuple,))

        for row in cursor:
            # Преобразуем DictRow в обычный словарь для удобства
            data = dict(row)
            # Используем kp_id как ключ для словаря данных
            db_data[str(data['kp_id'])] = data

        cursor.close()

    except psycopg2.Error as e:
        print(f"Ошибка при работе с PostgreSQL: {e}")
        # В реальном приложении здесь должна быть более сложная обработка ошибок

    finally:
        if conn:
            conn.close()

    return db_data


def process_file(input_file_path, output_file_path):
    """
    Обрабатывает один CSV-файл: извлекает ID, запрашивает БД, объединяет и записывает.
    """
    print(f"-> Обработка файла: {input_file_path.name}")

    csv_rows = []
    movie_ids = set()

    # 1. Чтение CSV и сбор ID
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                # Пропускаем пустые строки или строки с недостаточным количеством столбцов
                if len(row) > 6:
                    movie_id = row[6].strip()
                    if movie_id.isdigit():  # Проверка, что ID - число
                        movie_ids.add(movie_id)
                        csv_rows.append(row)
    except FileNotFoundError:
        print(f"   [ОШИБКА] Файл не найден: {input_file_path}")
        return
    except Exception as e:
        print(f"   [ОШИБКА] Ошибка чтения CSV {input_file_path.name}: {e}")
        return

    if not movie_ids:
        print("   Нет действительных ID для запроса.")
        return

    # 2. Запрос к БД
    db_data_map = fetch_db_data(list(movie_ids))
    print(f"   Получено {len(db_data_map)} записей из БД.")

    # 3. Объединение данных
    merged_data = []
    for csv_row in csv_rows:
        movie_id = csv_row[6].strip()
        db_record = db_data_map.get(movie_id)

        # Пропускаем, если запись не найдена в БД
        if not db_record:
            continue

        # Создаем базовый словарь из CSV данных
        csv_map = {
            'ID': movie_id,
            'CSV_Title_RU': csv_row[0].strip(),
            'CSV_Category_1': csv_row[1].strip(),
            'CSV_Category_2': csv_row[2].strip(),
            'CSV_Category_3': csv_row[3].strip(),
            'CSV_Category_4': csv_row[4].strip(),
            'CSV_Rating_1': csv_row[5].strip(),
            'CSV_Rating_2': csv_row[8].strip() if len(csv_row) > 8 else '',
            'CSV_Rating_3': csv_row[9].strip() if len(csv_row) > 9 else '',
        }

        # Добавляем данные из БД (db_record гарантированно существует здесь)
        # --- ИЗМЕНЕННЫЙ БЛОК db_fields ---
        db_fields = {
            'Title_RU': db_record.get('title', ''),
            'Title_EN': db_record.get('english_title', ''),
            'DB_Rating_1': db_record.get('kp_rating', ''),
            'DB_Rating_2': db_record.get('imdb_rating', ''),
            'DB_Rating_3': db_record.get('combined_rating', ''),  # Используем combined_rating как DB_Rating_3
            'Budget': db_record.get('budget', ''),
            'Image_URL': db_record.get('poster_url', ''),
            'Runtime': db_record.get('movie_length', ''),
            'Synopsis': db_record.get('description', ''),
            'Year': db_record.get('year_release', ''),
            'Age_Rating': db_record.get('age_rating', ''),
            'DB_Genres': db_record.get('genres', ''),
            'Countries': db_record.get('countries', ''),
            'Cast': db_record.get('persons', ''),  # Предполагаем, что 'persons' содержит информацию об актерах/персонах
            'Director': db_record.get('director', ''),
            'Source': 'DB & CSV'
        }
        # ---------------------------------

        # Объединяем CSV и DB данные
        final_record = {**db_fields, **csv_map}

        merged_data.append(final_record)

    # 4. Запись объединенных данных
    try:
        with open(output_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(HEADER)

            for record in merged_data:
                row = [record.get(field, '') for field in HEADER]
                writer.writerow(row)

        print(f"   [УСПЕХ] Записано {len(merged_data)} строк в {output_file_path.name}")

    except Exception as e:
        print(f"   [ОШИБКА] Ошибка записи CSV {output_file_path.name}: {e}")


def main():
    # Создание выходной папки, если она не существует
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"Входная папка: {INPUT_DIR}")
    print(f"Выходная папка: {OUTPUT_DIR}")
    print("-" * 30)

    # Итерация по всем файлам во входной папке
    for input_file_path in INPUT_DIR.iterdir():
        if input_file_path.suffix.lower() == '.csv':
            output_file_path = OUTPUT_DIR / input_file_path.name
            process_file(input_file_path, output_file_path)

    print("-" * 30)
    print("Объединение данных завершено.")


if __name__ == '__main__':
    main()
