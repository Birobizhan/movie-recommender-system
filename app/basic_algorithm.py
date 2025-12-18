import pandas as pd
import os

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
            # Если значение уже число
            if isinstance(value, (int, float)):
                return float(value) if float(value) > 0 else None
            # Если значение строка
            if not str(value).strip() or str(value).strip().lower() in ['nan', 'none', '']:
                return None
            num = float(str(value).replace(',', '.'))
            return num if num > 0 else None
        except (ValueError, TypeError):
            return None
    
    # Оценка Кинопоиска (колонка 5)
    if len(row) > 5:
        kp_rating = safe_float(row[5])
        if kp_rating is not None:
            ratings.append(kp_rating)
    
    # Оценка IMDB (колонка 8)
    if len(row) > 8:
        imdb_rating = safe_float(row[8])
        if imdb_rating is not None:
            ratings.append(imdb_rating)
    
    # Оценка критиков (колонка 9)
    if len(row) > 9:
        critics_rating = safe_float(row[9])
        if critics_rating is not None:
            ratings.append(critics_rating)
    
    if not ratings:
        return 0.0
    
    return round(sum(ratings) / len(ratings), 1)

def safe_str_clean(value):
    """Безопасно преобразует значение в строку и очищает"""
    if pd.isna(value) or value is None:
        return ""
    try:
        return str(value).strip()
    except:
        return ""

def load_genre_data(file_path):
    """Загружает данные жанра, автоматически определяя формат файла"""
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден")
        return None
    
    try:
        if is_excel_file(file_path):
            print(f"Обнаружен Excel-файл: {os.path.basename(file_path)}")
            # Читаем Excel-файл
            df = pd.read_excel(file_path, header=0)
            
            # Если данные в одной колонке, разделяем их
            if len(df.columns) == 1:
                print("Данные в одной колонке, разделяем...")
                # Разделяем первую колонку по запятым
                expanded = df.iloc[:, 0].astype(str).str.split(',', expand=True, n=EXPECTED_COLUMNS-1)
                # Заменяем исходный DataFrame
                df = expanded
            
            # Обрезаем или дополняем до нужного количества колонок
            if len(df.columns) > EXPECTED_COLUMNS:
                df = df.iloc[:, :EXPECTED_COLUMNS]
            elif len(df.columns) < EXPECTED_COLUMNS:
                for i in range(EXPECTED_COLUMNS - len(df.columns)):
                    df[f'empty_{i}'] = ''
        else:
            print(f"Читаем как CSV-файл: {os.path.basename(file_path)}")
            
            # Пробуем разные кодировки для CSV
            encodings = ['utf-8', 'cp1251', 'windows-1251', 'iso-8859-1']
            df = None
            
            for encoding in encodings:
                try:
                    # Читаем весь файл как текст
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    
                    # Разбиваем на строки и убираем пустые
                    lines = [line.strip() for line in content.split('\n') if line.strip()]
                    
                    # Разбиваем каждую строку по точке с запятой
                    data = []
                    for line in lines:
                        # Убираем лишние пробелы вокруг точек с запятой
                        line = line.replace(' ;', ';').replace('; ', ';')
                        parts = line.split(';')
                        
                        # Очищаем каждую часть
                        cleaned_parts = [part.strip() for part in parts]
                        
                        # Если частей меньше, чем ожидаемых колонок, дополняем
                        if len(cleaned_parts) < EXPECTED_COLUMNS:
                            cleaned_parts.extend([''] * (EXPECTED_COLUMNS - len(cleaned_parts)))
                        # Если больше - обрезаем
                        elif len(cleaned_parts) > EXPECTED_COLUMNS:
                            cleaned_parts = cleaned_parts[:EXPECTED_COLUMNS]
                        
                        data.append(cleaned_parts)
                    
                    if data:  # Если есть данные
                        df = pd.DataFrame(data)
                        print(f"Успешно прочитано с кодировкой: {encoding}")
                        print(f"Загружено {len(df)} строк, {len(df.columns)} колонок")
                        break
                        
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"Ошибка с кодировкой {encoding}: {e}")
                    continue
            
            if df is None:
                print("Не удалось прочитать файл ни с одной кодировкой")
                return None
        
        # Убеждаемся, что у нас достаточно колонок
        if len(df.columns) < 6:
            print(f"Недостаточно колонок: {len(df.columns)}")
            return None
        
        # Заполняем NaN значения
        df = df.fillna('')
        
        # Для отладки: выведем первые 3 строки
        if not df.empty:
            print("\nПервые 3 строки данных:")
            for i in range(min(3, len(df))):
                print(f"  Строка {i+1}: {df.iloc[i].tolist()}")
        
        # Вычисляем среднюю оценку для каждой строки
        avg_ratings = []
        for _, row in df.iterrows():
            avg_ratings.append(calculate_average_rating(row))
        
        # Создаем новый DataFrame с нужными колонками
        result_df = df.iloc[:, :6].copy()
        result_df['Средняя оценка'] = avg_ratings
        
        # Безопасно очищаем строковые данные в первых 6 колонках
        for i in range(6):
            if i < len(result_df.columns):
                result_df.iloc[:, i] = result_df.iloc[:, i].apply(safe_str_clean)
        
        print(f"\nУспешно загружено {len(result_df)} фильмов")
        return result_df
        
    except Exception as e:
        print(f"Ошибка при чтении {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return None

def recommend_movies(user_input):
    if not user_input or len(user_input) == 0:
        return []
    
    # Определяем жанр и путь к файлу
    genre = user_input[0]
    base_path = r"app/genre_with_info/"
    file_path = os.path.join(base_path, f"{genre}.csv")
    print(file_path)
    # Загружаем данные
    df = load_genre_data(file_path)
    if df is None or df.empty:
        print(f"Не удалось загрузить данные из {file_path}")
        return []
    
    # Проверяем структуру данных
    if len(df.columns) < 7:
        print(f"Неверная структура данных. Колонок: {len(df.columns)}, ожидалось: 7")
        return df.iloc[:, 0].head(5).tolist() if len(df.columns) > 0 else []
    
    # Рассчитываем паттерн совпадений для каждого фильма
    match_patterns = []
    exact_matches_counts = []
    
    for _, row in df.iterrows():
        pattern = ""
        exact_matches = 0
        
        # user_input[0] - это жанр, который должен совпадать с колонкой 1 в данных
        # user_input[1] - сравниваем с колонкой 2
        # user_input[2] - сравниваем с колонкой 3
        # user_input[3] - сравниваем с колонкой 4
        
        # Сначала проверим жанр (колонка 1)
        movie_genre = ""
        if pd.notna(row[1]):
            movie_genre = str(row[1]).strip().strip('"')
        
        # Первая цифра паттерна - всегда 1, так как файл загружен по жанру
        pattern += "1"
        if movie_genre == user_input[0].strip():
            exact_matches += 1
        
        # Теперь проверяем остальные критерии
        for i in range(1, min(len(user_input), 5)):  # максимум 4 критерия (включая жанр)
            user_val = user_input[i].strip()
            col_idx = i + 1  # Колонки 2-4 в DataFrame (индексы 2,3,4)
            
            if col_idx < len(row):
                # Получаем значение из фильма и очищаем его
                movie_val_raw = row[col_idx]
                movie_val = ""
                if pd.notna(movie_val_raw):
                    movie_val = str(movie_val_raw).strip().strip('"')
                
                # Сравниваем
                if movie_val == user_val:
                    pattern += "1"
                    exact_matches += 1
                else:
                    pattern += "2"
            else:
                pattern += "2"
        
        # Дополняем паттерн до 4 символов если нужно
        while len(pattern) < 4:
            pattern += "2"
        
        match_patterns.append(pattern)
        exact_matches_counts.append(exact_matches - 1)  # Вычитаем 1, так как жанр не считается в exact_matches
    
    df['match_pattern'] = match_patterns
    df['exact_matches'] = exact_matches_counts
    
    # Отладочный вывод: покажем первые 20 фильмов с их паттернами
    print("\nПервые 20 фильмов с паттернами для отладки:")
    print(f"{'Название':<40} | {'Жанр':<15} | {'Крит2':<20} | {'Крит3':<25} | {'Крит4':<30} | {'Паттерн':<6}")
    print("-" * 140)
    
    for idx, row in df.head(20).iterrows():
        title = ""
        if pd.notna(row.iloc[0]):
            title = str(row.iloc[0]).strip().strip('"')
        if not title:
            title = "Без названия"
        if len(title) > 39:
            title = title[:36] + "..."
        
        # Получаем значения критериев
        genre_val = str(row[1]).strip().strip('"') if pd.notna(row[1]) else ""
        crit2_val = str(row[2]).strip().strip('"') if len(row) > 2 and pd.notna(row[2]) else ""
        crit3_val = str(row[3]).strip().strip('"') if len(row) > 3 and pd.notna(row[3]) else ""
        crit4_val = str(row[4]).strip().strip('"') if len(row) > 4 and pd.notna(row[4]) else ""
        
        print(f"{title:<40} | {genre_val:<15} | {crit2_val:<20} | {crit3_val:<25} | {crit4_val:<30} | {row['match_pattern']:<6}")
    
    # Создаем числовую оценку для сортировки
    # Паттерны сортируем по алфавиту: "1111" < "1112" < "1121" < "1122" < ... < "2222"
    df_sorted = df.sort_values(
        by=['exact_matches', 'match_pattern', 'Средняя оценка'],
        ascending=[False, True, False]  # exact_matches по убыванию, паттерн по возрастанию, оценка по убыванию
    )
    
    # Выводим результаты для отладки
    print(f"\nТоп-5 фильмов для запроса {user_input}:")
    print(f"{'Название':<40} | {'Совпадений':>10} | {'Паттерн':>6} | {'Средняя оценка':>12}")
    print("-" * 78)
    
    for idx, row in df_sorted.head(5).iterrows():  # Покажем 10 для отладки
        title = ""
        if pd.notna(row.iloc[0]):
            title = str(row.iloc[0]).strip().strip('"')
        if not title:
            title = "Без названия"
        if len(title) > 39:
            title = title[:36] + "..."
        print(f"{title:<40} | {row['exact_matches']:>10} | {row['match_pattern']:>6} | {row['Средняя оценка']:>12.1f}")
    
    # Возвращаем топ-5 названий
    result = []
    for idx, row in df_sorted.head(10).iterrows():
        title = ""
        if pd.notna(row.iloc[0]):
            title = str(row.iloc[0]).strip().strip('"')
        if not title:
            title = "Без названия"
        result.append(title)
    
    return result

# #Пример использования
# if __name__ == "__main__":
#     user_selection = ['Биографический', 'Семейный', 'Спортивные легенды', 'Современное кино (2000–2020)']
#
#
#     recommended = recommend_movies(user_selection)
#     print("\nРекомендованные фильмы:", recommended)
