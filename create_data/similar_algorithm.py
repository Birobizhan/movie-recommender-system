import pandas as pd
import os
import re

# Ожидаемое количество колонок в данных
EXPECTED_COLUMNS = 10

def is_excel_file(file_path):
    """Проверяет, является ли файл Excel-файлом по сигнатуре"""
    try:
        with open(file_path, 'rb') as f:
            signature = f.read(4)
            return signature == b'PK\x03\x04'  # Сигнатура ZIP/XLSX
    except:
        return False

def calculate_average_rating(row):
    """Вычисляет среднюю оценку из доступных данных, игнорируя пропуски и нули"""
    ratings = []
    
    def safe_float(value):
        if value is None or pd.isna(value):
            return None
        try:
            if isinstance(value, (int, float)):
                return float(value) if float(value) > 0 else None
            
            str_val = str(value).strip()
            if not str_val or str_val.lower() in ['nan', 'none', '']:
                return None
            
            str_val = str_val.replace(',', '.')
            str_val = re.sub(r'[^\d\.]', '', str_val)
            if not str_val:
                return None
            return float(str_val) if float(str_val) > 0 else None
        except (ValueError, TypeError):
            return None
    
    if len(row) > 5:
        kp_rating = safe_float(row[5])
        if kp_rating is not None:
            ratings.append(kp_rating)
    
    if len(row) > 8:
        imdb_rating = safe_float(row[8])
        if imdb_rating is not None:
            ratings.append(imdb_rating)
    
    if len(row) > 9:
        critics_rating = safe_float(row[9])
        if critics_rating is not None:
            ratings.append(critics_rating)
    
    return round(sum(ratings) / len(ratings), 1) if ratings else 0.0

def clean_text(value):
    """Очищает текст от кавычек и лишних символов"""
    if pd.isna(value) or value is None:
        return ""
    
    text = str(value).strip()
    text = text.strip('"')
    text = re.sub(r'\s+', ' ', text)
    return text

def load_genre_data(file_path):
    """Загружает данные жанра с обработкой CSV файлов"""
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден")
        return None
    
    try:
        if is_excel_file(file_path):
            df = pd.read_excel(file_path, header=None)
        else:
            # Читаем весь файл как текст
            with open(file_path, 'r', encoding='cp1251') as f:
                content = f.read()
            
            # Разбиваем на строки и убираем пустые
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            # Разбиваем каждую строку по точке с запятой
            data = []
            for line in lines:
                parts = line.split(';')
                
                # Очищаем каждую часть
                cleaned_parts = [clean_text(part) for part in parts]
                
                # Если частей меньше, чем ожидаемых колонок, дополняем
                if len(cleaned_parts) < EXPECTED_COLUMNS:
                    cleaned_parts.extend([''] * (EXPECTED_COLUMNS - len(cleaned_parts)))
                # Если больше - обрезаем
                elif len(cleaned_parts) > EXPECTED_COLUMNS:
                    cleaned_parts = cleaned_parts[:EXPECTED_COLUMNS]
                
                data.append(cleaned_parts)
            
            if not data:
                return None
                
            df = pd.DataFrame(data)
        
        # Обрезаем или дополняем до нужного количества колонок
        if len(df.columns) > EXPECTED_COLUMNS:
            df = df.iloc[:, :EXPECTED_COLUMNS]
        elif len(df.columns) < EXPECTED_COLUMNS:
            for i in range(EXPECTED_COLUMNS - len(df.columns)):
                df[f'empty_{i}'] = ''
        
        # Заполняем NaN значения
        df = df.fillna('')
        
        # Удаляем полностью пустые строки
        df = df[df.apply(lambda row: any(cell != '' for cell in row), axis=1)]
        
        # Вычисляем среднюю оценку для каждой строки
        avg_ratings = []
        for _, row in df.iterrows():
            avg_ratings.append(calculate_average_rating(row))
        
        # Создаем новый DataFrame с нужными колонками
        result_df = df.iloc[:, :6].copy()
        result_df['Средняя оценка'] = avg_ratings
        
        return result_df
        
    except Exception as e:
        print(f"Ошибка при чтении {file_path}: {e}")
        return None

def find_similar_movies_by_movie(genre, movie_title, top_n=20):
    """
    Находит похожие фильмы на основе указанного фильма
    
    Args:
        genre: Жанр фильма (для выбора CSV файла)
        movie_title: Название фильма для поиска похожих
        top_n: Количество возвращаемых рекомендаций (по умолчанию 20)
    
    Returns:
        Список похожих фильмов (топ-20)
    """
    base_path = r"C:\Users\User\Desktop\genre_with_info"
    file_path = os.path.join(base_path, f"{genre}.csv")
    
    # Загружаем данные
    df = load_genre_data(file_path)
    if df is None or df.empty:
        print(f"Не удалось загрузить данные из {file_path}")
        return []
    
    # Ищем фильм в данных
    found_movie = None
    movie_index = -1
    
    # Нормализуем название для поиска
    search_title = clean_text(movie_title).lower()
    
    for idx, row in df.iterrows():
        title = clean_text(row.iloc[0]).lower()
        
        # Проверяем точное совпадение
        if title == search_title:
            found_movie = row
            movie_index = idx
            break
    
    if found_movie is None:
        print(f"Фильм '{movie_title}' не найден в файле {genre}.csv")
        return []
    
    # Извлекаем характеристики найденного фильма
    movie_name = clean_text(found_movie.iloc[0])
    movie_genre = clean_text(found_movie[1]) if len(found_movie) > 1 else ""
    movie_crit2 = clean_text(found_movie[2]) if len(found_movie) > 2 else ""
    movie_crit3 = clean_text(found_movie[3]) if len(found_movie) > 3 else ""
    movie_crit4 = clean_text(found_movie[4]) if len(found_movie) > 4 else ""
    movie_rating = found_movie['Средняя оценка']
    
    print(f"\nНайденный фильм: '{movie_name}'")
    print(f"Характеристики:")
    print(f"  1. Жанр: {movie_genre}")
    print(f"  2. {movie_crit2}")
    print(f"  3. {movie_crit3}")
    print(f"  4. {movie_crit4}")
    print(f"  Средняя оценка: {movie_rating:.1f}\n")
    
    # Рассчитываем паттерн совпадений для каждого фильма
    match_patterns = []
    exact_matches_counts = []
    crit2_matches = []
    crit3_matches = []
    crit4_matches = []
    
    for idx, row in df.iterrows():
        # Пропускаем исходный фильм
        if idx == movie_index:
            match_patterns.append("1111")
            exact_matches_counts.append(3)  # Все 3 критерия совпадают
            crit2_matches.append("✓")
            crit3_matches.append("✓")
            crit4_matches.append("✓")
            continue
        
        pattern = "1"  # Первая цифра всегда 1 (жанр совпадает)
        exact_matches = 0
        
        # Проверяем критерий 2
        current_crit2 = clean_text(row[2]) if len(row) > 2 else ""
        if current_crit2 == movie_crit2:
            pattern += "1"
            exact_matches += 1
            crit2_matches.append("✓")
        else:
            pattern += "2"
            crit2_matches.append("✗")
        
        # Проверяем критерий 3
        current_crit3 = clean_text(row[3]) if len(row) > 3 else ""
        if current_crit3 == movie_crit3:
            pattern += "1"
            exact_matches += 1
            crit3_matches.append("✓")
        else:
            pattern += "2"
            crit3_matches.append("✗")
        
        # Проверяем критерий 4
        current_crit4 = clean_text(row[4]) if len(row) > 4 else ""
        if current_crit4 == movie_crit4:
            pattern += "1"
            exact_matches += 1
            crit4_matches.append("✓")
        else:
            pattern += "2"
            crit4_matches.append("✗")
        
        match_patterns.append(pattern)
        exact_matches_counts.append(exact_matches)
    
    df['match_pattern'] = match_patterns
    df['exact_matches'] = exact_matches_counts
    df['crit2_match'] = crit2_matches
    df['crit3_match'] = crit3_matches
    df['crit4_match'] = crit4_matches
    df['is_original'] = df.index == movie_index
    
    # Сортируем по релевантности
    df_sorted = df.sort_values(
        by=['exact_matches', 'match_pattern', 'Средняя оценка'],
        ascending=[False, True, False]
    )
    
    # Исключаем исходный фильм из результатов и берем топ-20
    result_df = df_sorted[~df_sorted['is_original']].head(top_n)
    
    # Выводим таблицу
    print(f"Топ-{top_n} похожих фильмов на '{movie_name}':")
    print(f"{'№':<3} {'Название':<30} | {'Совпад.':>7} | {'Паттерн':>7} | {'Оценка':>7} | {'Крит2':>6} | {'Крит3':>6} | {'Крит4':>6}")
    print("-" * 85)
    
    result = []
    for i, (idx, row) in enumerate(result_df.iterrows(), 1):
        title = clean_text(row.iloc[0])
        if not title:
            title = "Без названия"
        
        # Обрезаем название если слишком длинное
        display_title = title[:28] + "..." if len(title) > 30 else title
        
        print(f"{i:<3} {display_title:<30} | {row['exact_matches']:>7} | {row['match_pattern']:>7} | {row['Средняя оценка']:>7.1f} | {row['crit2_match']:>6} | {row['crit3_match']:>6} | {row['crit4_match']:>6}")
        
        result.append(title)
    
    return result

# Пример использования с заданными параметрами
if __name__ == "__main__":
    # Словарь с тестовыми примерами
    test_cases = [
        {"genre": "Криминал", "movie_title": "Суши гёл"},
        {"genre": "Биографический", "movie_title": "Дело Ричарда Джуэлла"},
        # Можно добавить больше тестовых случаев
        # {"genre": "Фэнтези", "movie_title": "Хоббит"},
    ]
    
    for test_case in test_cases:
        genre = test_case["genre"]
        movie_title = test_case["movie_title"]
        
        print("=" * 85)
        print(f"Поиск похожих фильмов для: {movie_title} (жанр: {genre})")
        print("=" * 85)
        
        similar_movies = find_similar_movies_by_movie(genre, movie_title, top_n=20)
        print(f"\nВсего найдено похожих фильмов: {len(similar_movies)}")
        print(f"Топ-20 рекомендаций: {similar_movies}")
        print("\n")
