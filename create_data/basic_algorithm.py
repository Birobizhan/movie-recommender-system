import pandas as pd
import os
import numpy as np

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
                    df = pd.read_csv(file_path, encoding=encoding, header=0)
                    print(f"Успешно прочитано с кодировкой: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"Ошибка с кодировкой {encoding}: {e}")
                    continue
            
            if df is None:
                print("Не удалось прочитать файл ни с одной кодировкой")
                return None
            
            # Если в CSV данные в одной колонке, разделяем их
            if len(df.columns) == 1:
                print("Данные в одной колонке, разделяем...")
                expanded = df.iloc[:, 0].astype(str).str.split(',', expand=True, n=EXPECTED_COLUMNS-1)
                df = expanded
        
        # Убеждаемся, что у нас достаточно колонок
        if len(df.columns) < 6:
            print(f"Недостаточно колонок: {len(df.columns)}")
            return None
        
        # Заполняем NaN значения
        df = df.fillna('')
        
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
        
        print(f"Успешно загружено {len(result_df)} фильмов")
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
    base_path = r"C:\Users\User\Desktop\genre_with_info"
    file_path = os.path.join(base_path, f"{genre}.csv")
    
    # Загружаем данные
    df = load_genre_data(file_path)
    if df is None or df.empty:
        print(f"Не удалось загрузить данные из {file_path}")
        return []
    
    # Проверяем структуру данных
    if len(df.columns) < 7:
        print(f"Неверная структура данных. Колонок: {len(df.columns)}, ожидалось: 7")
        return df.iloc[:, 0].head(5).tolist() if len(df.columns) > 0 else []
    
    # Веса характеристик
    priority_weights = [1000, 100, 10, 1]
    
    # Рассчитываем релевантность
    df['relevance'] = 0
    df['exact_matches'] = 0
    
    # Для каждой характеристики пользователя
    for i in range(1, min(len(user_input) + 1, 5)):
        user_val = user_input[i-1]
        col_idx = i  # Колонки 1-4 в DataFrame
        
        # Создаем маску для точных совпадений
        mask = df.iloc[:, col_idx].apply(safe_str_clean) == user_val
        
        # Обновляем релевантность
        df.loc[mask, 'relevance'] += priority_weights[i-1]
        df.loc[mask, 'exact_matches'] += 1
        
        # Частичные совпадения с предыдущими характеристиками
        if i > 1:
            for prev_i in range(i-1):
                prev_user_val = user_input[prev_i]
                prev_col_idx = prev_i + 1
                
                prev_mask = df.iloc[:, prev_col_idx].apply(safe_str_clean) == prev_user_val
                curr_not_mask = df.iloc[:, col_idx].apply(safe_str_clean) != user_val
                
                partial_mask = prev_mask & curr_not_mask
                df.loc[partial_mask, 'relevance'] += priority_weights[prev_i] * 0.1
    
    # Сортируем по релевантности
    df_sorted = df.sort_values(
        by=['exact_matches', 'relevance', 'Средняя оценка'],
        ascending=[False, False, False]
    )
    
    # Выводим результаты для отладки
    print(f"\nТоп-5 фильмов для запроса {user_input}:")
    print(f"{'Название':<40} | {'Полных совпад.':>12} | {'Релевантность':>12} | {'Средняя оценка':>12}")
    print("-" * 80)
    
    for idx, row in df_sorted.head(5).iterrows():
        title = safe_str_clean(row.iloc[0])
        if not title:
            title = "Без названия"
        if len(title) > 39:
            title = title[:36] + "..."
        print(f"{title:<40} | {row['exact_matches']:>12} | {row['relevance']:>12.1f} | {row['Средняя оценка']:>12.1f}")
    
    # Возвращаем топ-5 названий
    result = []
    for idx, row in df_sorted.head(5).iterrows():
        title = safe_str_clean(row.iloc[0])
        if not title:
            title = "Без названия"
        result.append(title)
    
    return result

# Пример использования
if __name__ == "__main__":
    user_selection = [
        "Военный",
        "Драма", 
        "Личные драмы солдат",
        "Классика (до 2000 года)"
    ]

    recommended = recommend_movies(user_selection)
    print("\nРекомендованные фильмы:", recommended)
