import csv
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Movie
from app.database import get_db, engine


def parse_list_field(field_str: str) -> list[str]:
    """Разделяет строку по запятой с пробелом (', ') и очищает пустые элементы."""
    # Используется для полей genres и countries
    return [item.strip() for item in field_str.split(', ') if item.strip()]


def load_data_from_csv(csv_filepath: str):
    """Читает CSV-файл и загружает данные в базу данных."""

    db_generator = get_db()
    db: Session = next(db_generator)

    try:
        with open(csv_filepath, mode='r', encoding='utf-8-sig', newline='') as f:
            csv_reader = csv.reader(f, delimiter=';', quotechar='"')

            records_count = 0

            for row in csv_reader:
                if not row or len(row) < 19:
                    continue

                try:
                    kp_id = int(row[0])
                    english_title = row[1]
                    title = row[6]

                    kp_rating = float(row[2]) if row[2] else 0.0
                    imdb_rating = float(row[3]) if row[3] else 0.0
                    critics_rating = float(row[4]) if row[4] else 0.0
                    sum_votes = int(row[8]) if row[8] else 0

                    movie_length = int(row[10]) if row[10] else None
                    age_rating = int(row[20]) if row[20] else None

                    fees_world = row[7].strip()
                    budget = row[13].strip()
                    year_release = int(row[14]) if row[14] else None

                    description = row[11].strip()
                    poster_url = row[9].strip()

                    premiere_str = row[12].split('T')[0] if row[12] and 'T' in row[12] else None
                    world_premiere = datetime.strptime(premiere_str, '%Y-%m-%d').date() if premiere_str else None

                    genres = parse_list_field(row[15])
                    countries = parse_list_field(row[16])


                    persons_list = []
                    if row[17]:
                        persons_list = [[int(item.split(':')[0]), item.split(':')[1]]
                                        for item in row[17].split(', ') if ':' in item]

                    director_id = row[18]
                    director_name = row[19]
                    director = [director_id, director_name] if director_id else None

                    movie = Movie(
                        kp_id=kp_id,
                        title=title,
                        english_title=english_title,
                        poster_url=poster_url,
                        description=description,
                        kp_rating=kp_rating,
                        imdb_rating=imdb_rating,
                        critics_rating=critics_rating,
                        sum_votes=sum_votes,
                        movie_length=movie_length,
                        age_rating=age_rating,
                        year_release=year_release,
                        fees_world=fees_world,
                        budget=budget,
                        world_premiere=world_premiere,
                        genres=genres,
                        countries=countries,
                        persons=persons_list,
                        director=director,
                    )

                    db.add(movie)
                    records_count += 1

                except Exception as e:
                    db.rollback()
                    print(
                        f"Ошибка парсинга/конвертации строки {records_count + 1} (ID: {row[6] if len(row) > 6 else 'N/A'}): {e}. Строка: {row}")
                    continue

            # 4. Коммит
            db.commit()
            print(f"✅ Успешно добавлено {records_count} записей в БД.")

    except FileNotFoundError:
        print(f"Файл {csv_filepath} не найден.")
    finally:
        db_generator.close()


if __name__ == "__main__":
    load_data_from_csv('movies_with_all_info/new.csv')