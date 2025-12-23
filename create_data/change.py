import re
from pathlib import Path
import os

# Папка с объединенными CSV-файлами
INPUT_DIR = Path('genre_with_info')


def process_file(file_path):
    """
    Читает файл, заменяет запятые на точки с запятой,
    если после запятой нет пробельного символа, и сохраняет изменения
    """
    print(f"-> Обработка файла: {file_path.name}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        pattern = re.compile(r',(?![\s])')

        new_content = pattern.sub(';', content)

        if new_content == content:
            print("   Изменений не обнаружено.")
            return

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print("   [УСПЕХ] Разделители заменены на точку с запятой.")

    except FileNotFoundError:
        print(f"   [ОШИБКА] Файл не найден: {file_path.name}")
    except Exception as e:
        print(f"   [ОШИБКА] Не удалось обработать файл {file_path.name}: {e}")


def main():
    if not INPUT_DIR.exists():
        print(f"Ошибка: Папка '{INPUT_DIR}' не найдена.")
        return

    print("--- ЗАМЕНА РАЗДЕЛИТЕЛЕЙ В CSV-ФАЙЛАХ ---")
    print(f"Папка для обработки: {INPUT_DIR}")
    print("Внимание: Оригинальные файлы будут изменены.")
    print("-" * 40)

    processed_count = 0
    for input_file_path in INPUT_DIR.iterdir():
        if input_file_path.suffix.lower() == '.csv':
            process_file(input_file_path)
            processed_count += 1

    print("-" * 40)
    print(f"Обработано {processed_count} CSV-файлов.")
    print("Замена разделителей завершена.")


if __name__ == '__main__':
    main()
