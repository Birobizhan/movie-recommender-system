import csv
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values, Json
from environs import Env
import ast  # Добавляем импорт для безопасного парсинга строк

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

env = Env()
# Явно читаем .env из корня проекта, чтобы переменные были доступны
env_path = ROOT_DIR / ".env"
if env_path.exists():
    env.read_env(env_path)
else:
    env.read_env()

# Папка с объединенными CSV-файлами
INPUT_DIR = BASE_DIR / 'genre_with_dbinfo'
# Название существующей таблицы, в которую вставляем данные
NEW_DB_TABLE_NAME = 'movies'

# Заголовки из вашего объединенного CSV
HEADER = [
    'ID', 'Title_RU', 'Title_EN', 'Year', 'Age_Rating', 'Runtime', 'Image_URL', 'Synopsis',
    'DB_Genres', 'Countries', 'Director', 'Cast',
    'DB_Rating_1', 'DB_Rating_2', 'DB_Rating_3', 'Budget',
    'CSV_Title_RU', 'CSV_Category_1', 'CSV_Category_2', 'CSV_Category_3', 'CSV_Category_4',
    'CSV_Rating_1', 'CSV_Rating_2', 'CSV_Rating_3',
    'Source'
]

# Список столбцов в таблице 'movies', в которые мы будем вставлять данные.
DB_TARGET_COLUMNS = [
    'kp_id',
    'title',
    'english_title',
    'kp_rating',
    'imdb_rating',
    'combined_rating',
    'poster_url',
    'movie_length',
    'description',
    'budget',
    'year_release',
    'age_rating',
    'genres',
    'countries',
    'persons',
    'director',
]

# Сопоставление заголовков CSV с именами столбцов БД
CSV_TO_DB_MAPPING = {
    'ID': 'kp_id',
    'Title_RU': 'title',
    'Title_EN': 'english_title',
    'DB_Rating_1': 'kp_rating',
    'DB_Rating_2': 'imdb_rating',
    'DB_Rating_3': 'combined_rating',
    'Image_URL': 'poster_url',
    'Runtime': 'movie_length',
    'Synopsis': 'description',
    'Budget': 'budget',
    'Year': 'year_release',
    'Age_Rating': 'age_rating',
    'DB_Genres': 'genres',
    'Countries': 'countries',
    'Cast': 'persons',
    'Director': 'director',
}


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ПРЕОБРАЗОВАНИЯ ТИПОВ ---
def safe_int(value):
    """Преобразует строку в int, обрабатывая пустые строки как None."""
    value = value.strip()
    if not value:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def safe_float(value):
    """Преобразует строку в float, обрабатывая пустые строки как None."""
    value = value.strip()
    if not value:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def safe_literal_eval(string_value):
    """Безопасно парсит строку в Python-объект (список/словарь), обрабатывая пустые строки как None."""
    string_value = string_value.strip()
    if not string_value:
        return None
    try:
        return ast.literal_eval(string_value)
    except (ValueError, SyntaxError, TypeError) as e:
        # Если парсинг не удался, возвращаем None
        # print(f"   [ОШИБКА ПАРСИНГА] Не удалось распарсить '{string_value[:50]}...'. Ошибка: {e}")
        return None


def normalize_people(value):
    """
    Приводит список вида [[id, 'Имя'], ...] или [id, 'Имя'] к списку строк с именами.
    Дополнительно:
    - если пришла строка или число, оборачиваем в список строк;
    - пустые результаты -> None.
    """
    if value is None:
        return None

    # Строка или число — оборачиваем в список строк
    if isinstance(value, (str, int, float)):
        value = [value]

    if not isinstance(value, list):
        return None

    def take_name(item):
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            return str(item[1])
        return str(item)

    try:
        result = [take_name(item) for item in value]
        return result or None
    except Exception:
        return None


def fix_year_from_title(record: list):
    """
    Если год явно некорректен (< 1900) и в english_title есть суффикс ',YYYY',
    переносим этот год в year_release и чистим title_en.
    record — список значений в порядке DB_TARGET_COLUMNS.
    """
    # Преобразуем в dict для удобства
    rec = {col: record[i] for i, col in enumerate(DB_TARGET_COLUMNS)}

    year_val = rec.get("year_release")
    title_en = rec.get("english_title")

    if isinstance(year_val, int) and year_val < 1900 and isinstance(title_en, str) and "," in title_en:
        base, tail = title_en.rsplit(",", 1)
        tail_digits = tail.strip()
        if tail_digits.isdigit() and len(tail_digits) == 4:
            rec["english_title"] = base.strip()
            rec["year_release"] = int(tail_digits)
            # Пересобираем список в порядке колонок
            return [rec[col] for col in DB_TARGET_COLUMNS]

    return record


# Карта преобразования: Имя столбца БД -> Функция преобразования
CONVERSION_MAP = {
    'kp_id': safe_int,
    'kp_rating': safe_float,
    'imdb_rating': safe_float,
    'movie_length': safe_int,
    'year_release': safe_int,
    'age_rating': safe_int,
    'genres': safe_literal_eval,
    'countries': safe_literal_eval,
    'persons': safe_literal_eval,
    'director': safe_literal_eval,
}


# --------------------------------------------------------


def read_csv_data(file_path):
    """Читает данные из одного CSV-файла и возвращает список кортежей для вставки."""
    data_to_insert = []

    db_to_csv_mapping = {v: k for k, v in CSV_TO_DB_MAPPING.items()}
    extraction_order = [db_to_csv_mapping[db_col]
                        for db_col in DB_TARGET_COLUMNS]

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')

            for row in reader:
                record_list = []
                for db_col_name, csv_header_name in zip(DB_TARGET_COLUMNS, extraction_order):
                    raw_value = row.get(csv_header_name, "") or ""

                    # Применяем соответствующую функцию преобразования
                    converter = CONVERSION_MAP.get(db_col_name)
                    try:
                        if converter:
                            converted = converter(raw_value)
                        else:
                            # Для всех остальных (TEXT/VARCHAR) просто используем строку
                            converted = raw_value.strip() if raw_value else None
                    except Exception as conv_err:
                        # Логируем и пропускаем проблемное поле
                        print(
                            f"   [WARN] Ошибка преобразования поля '{db_col_name}' в файле {file_path.name}: {conv_err}")
                        converted = None

                    # Нормализуем людей (берём только имена) и оборачиваем в JSON
                    if db_col_name in {"persons", "director"}:
                        normalized = normalize_people(converted)
                        record_list.append(
                            Json(normalized) if normalized is not None else None)
                    else:
                        record_list.append(converted)

                # Исправляем год, если он приписан к english_title
                record_list = fix_year_from_title(record_list)
                data_to_insert.append(tuple(record_list))

    except Exception as e:
        print(f"   [ОШИБКА] Ошибка чтения CSV {file_path.name}: {e}")

    return data_to_insert


def upload_data(conn, all_data):
    """Загружает все собранные данные в таблицу movies."""
    if not all_data:
        print("Нет данных для загрузки.")
        return

    cursor = conn.cursor()

    db_column_names = DB_TARGET_COLUMNS

    insert_query = f"""
    INSERT INTO {NEW_DB_TABLE_NAME} ({', '.join(db_column_names)})
    VALUES %s
    ON CONFLICT (kp_id) DO NOTHING;
    """

    try:
        execute_values(cursor, insert_query, all_data)
        conn.commit()
        print(
            f"[УСПЕХ] Загружено {len(all_data)} записей в таблицу '{NEW_DB_TABLE_NAME}'.")
    except psycopg2.Error as e:
        print(f"[ОШИБКА] Ошибка при загрузке данных: {e}")
        conn.rollback()
    finally:
        cursor.close()


def main():
    all_data_for_upload = []

    print("--- ЗАГРУЗКА ОБЪЕДИНЕННЫХ ДАННЫХ В БД ---")
    print(f"Чтение файлов из: {INPUT_DIR}")

    if not INPUT_DIR.exists():
        print(f"[КРИТИЧЕСКАЯ ОШИБКА] Папка с данными не найдена: {INPUT_DIR}")
        return

    # 1. Сбор данных из всех CSV-файлов
    for input_file_path in INPUT_DIR.iterdir():
        if input_file_path.suffix.lower() == '.csv':
            print(f"-> Чтение файла: {input_file_path.name}")
            data = read_csv_data(input_file_path)
            all_data_for_upload.extend(data)

    print("-" * 40)
    print(f"Всего собрано {len(all_data_for_upload)} записей для загрузки.")

    if not all_data_for_upload:
        print("Загрузка отменена.")
        return

    # 2. Подключение к БД и загрузка
    db_url = env.str("DATABASE_URL_LOCAL", None) or env.str(
        "DATABASE_URL", None)
    if not db_url:
        print("[КРИТИЧЕСКАЯ ОШИБКА] Не задан DATABASE_URL_LOCAL или DATABASE_URL в .env")
        return

    conn = None
    try:
        conn = psycopg2.connect(db_url, client_encoding='utf8')
        upload_data(conn, all_data_for_upload)

    except psycopg2.Error as e:
        print(f"[КРИТИЧЕСКАЯ ОШИБКА] Не удалось подключиться к БД: {e}")
    except Exception as e:
        print(f"[КРИТИЧЕСКАЯ ОШИБКА] Непредвиденная ошибка: {e}")
    finally:
        if conn:
            conn.close()

    print("-" * 40)
    print("Загрузка данных завершена.")


if __name__ == '__main__':
    main()
