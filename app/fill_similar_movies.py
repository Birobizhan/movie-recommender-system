"""
Скрипт для заполнения таблицы movie_similarities из CSV файлов в папке update_films.
Формат CSV: первая строка - заголовки, вторая колонка (индекс 1) - название фильма,
последняя колонка (индекс 20) - список похожих фильмов через точку с запятой.
"""
import os
import csv
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import SessionLocal
from app.models.movie import Movie, movie_similarities
from sqlalchemy import insert, select


def normalize_title(title: str) -> str:
    """Нормализует название фильма для сравнения."""
    if not title:
        return ""
    # Убираем лишние пробелы, приводим к нижнему регистру
    return title.strip().lower()


def find_movie_by_title(db, title: str) -> Movie | None:
    """Находит фильм по названию (с учетом нормализации)."""
    normalized = normalize_title(title)
    movies = db.query(Movie).all()
    for movie in movies:
        if normalize_title(movie.title) == normalized:
            return movie
        # Также проверяем english_title
        if movie.english_title and normalize_title(movie.english_title) == normalized:
            return movie
    return None


def process_csv_file(db, file_path: Path):
    """Обрабатывает один CSV файл и добавляет похожие фильмы в БД."""
    print(f"Обработка файла: {file_path.name}")
    
    added_count = 0
    skipped_count = 0
    not_found_count = 0
    
    try:
        with open(file_path, 'r', encoding='windows-1251') as f:
            reader = csv.reader(f, delimiter=';')
            
            # Пропускаем заголовок
            next(reader, None)
            
            for row_num, row in enumerate(reader, start=2):
                if len(row) < 21:
                    continue
                
                # Название фильма во второй колонке (индекс 1)
                movie_title = row[1].strip() if len(row) > 1 else ""
                if not movie_title:
                    continue
                
                # Похожие фильмы в последней колонке (индекс 20)
                similar_movies_str = row[20].strip() if len(row) > 20 else ""
                if not similar_movies_str:
                    continue
                
                # Находим основной фильм
                main_movie = find_movie_by_title(db, movie_title)
                if not main_movie:
                    not_found_count += 1
                    if not_found_count <= 5:  # Показываем первые 5 не найденных
                        print(f"  Не найден фильм: {movie_title}")
                    continue
                
                # Разбиваем список похожих фильмов
                similar_titles = [t.strip() for t in similar_movies_str.split(';') if t.strip()]
                
                # Добавляем связи
                for similar_title in similar_titles:
                    similar_movie = find_movie_by_title(db, similar_title)
                    if not similar_movie:
                        continue
                    
                    # Проверяем, нет ли уже такой связи
                    existing = db.execute(
                        select(movie_similarities).where(
                            movie_similarities.c.movie_id == main_movie.id,
                            movie_similarities.c.similar_movie_id == similar_movie.id
                        )
                    ).first()
                    
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # Добавляем связь
                    try:
                        db.execute(
                            insert(movie_similarities).values(
                                movie_id=main_movie.id,
                                similar_movie_id=similar_movie.id
                            )
                        )
                        added_count += 1
                    except Exception as e:
                        # Игнорируем ошибки дубликатов (если связь уже существует)
                        if "duplicate" not in str(e).lower() and "unique" not in str(e).lower():
                            print(f"  Ошибка при добавлении связи {main_movie.title} -> {similar_title}: {e}")
                        skipped_count += 1
                
                # Коммитим каждые 100 фильмов
                if (row_num - 1) % 100 == 0:
                    db.commit()
                    print(f"  Обработано {row_num - 1} строк, добавлено {added_count} связей")
    
    except Exception as e:
        print(f"Ошибка при обработке файла {file_path.name}: {e}")
        db.rollback()
        return
    
    # Финальный коммит
    db.commit()
    print(f"  Файл {file_path.name}: добавлено {added_count} связей, пропущено {skipped_count}, не найдено фильмов {not_found_count}")


def main():
    """Основная функция для заполнения похожих фильмов."""
    update_films_dir = project_root / "create_data" / "update_films"
    
    if not update_films_dir.exists():
        print(f"Папка {update_films_dir} не найдена!")
        return
    
    db = SessionLocal()
    
    try:
        # Получаем все CSV файлы
        csv_files = list(update_films_dir.glob("*.csv"))
        
        if not csv_files:
            print(f"CSV файлы не найдены в {update_films_dir}")
            return
        
        print(f"Найдено {len(csv_files)} CSV файлов")
        
        # Очищаем существующие связи (опционально, раскомментируйте если нужно)
        # print("Очистка существующих связей...")
        # db.execute(movie_similarities.delete())
        # db.commit()
        
        # Обрабатываем каждый файл
        for csv_file in csv_files:
            process_csv_file(db, csv_file)
        
        print("\nГотово! Все похожие фильмы добавлены в БД.")
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
