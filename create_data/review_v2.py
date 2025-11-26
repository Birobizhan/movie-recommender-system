from environs import Env
from openai import OpenAI
import time
import logging
import re
import csv
from openai.types.chat import ChatCompletion
from typing import Callable, TypeVar, List, Tuple
import concurrent.futures
import threading

# --- Настройка логирования (Остается без изменений) ---
logging.basicConfig(level=logging.INFO, filename="create_films_review_log.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")
T = TypeVar('T')

# --- ГЛОБАЛЬНАЯ БЛОКИРОВКА ДЛЯ БЕЗОПАСНОСТИ ЗАПИСИ В CSV ---
# Это критически важно при параллельной записи в файлы
CSV_LOCK = threading.Lock()
# Установим максимальное количество потоков (зависит от лимитов API и производительности)
MAX_WORKERS = 8


# --- Декоратор Retry (Остается без изменений) ---
class Retry:
    def __init__(self, max_retries: int):
        if max_retries < 1:
            raise ValueError("Количество попыток должно быть не меньше 1.")
        self.max_retries = max_retries

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            for attempt in range(self.max_retries):
                try:
                    return func(*args, **kwargs)

                except TypeError as error:
                    logging.warning('Ошибка типов, скорее всего закончились попытки на токене', exc_info=True)
                    print(f"Попытка {attempt + 1} из {self.max_retries} завершилась с ошибкой: {error}")

                except IndexError as error:
                    logging.error('Ошибка индексирования, пришел не тот ответ', exc_info=True)
                    print(f"Попытка {attempt + 1} из {self.max_retries} завершилась с ошибкой: {error}")

                except ValueError as error:
                    logging.error(f'{error}, скорее всего не совпадают названия фильмов на запросе и ответе',
                                  exc_info=True)
                    print(f"Попытка {attempt + 1} из {self.max_retries} завершилась с ошибкой: {error}")

                except Exception as e:
                    logging.error(e, exc_info=True)
                    print(f"Попытка {attempt + 1} из {self.max_retries} завершилась с ошибкой: {e}")

                # Небольшая пауза между попытками, чтобы не перегружать API
                time.sleep(1)

            raise Exception(f"Все {self.max_retries} попыток завершились ошибкой")

        return wrapper


# --- Класс prompter (Остается для сохранения структуры) ---
class prompter:
    def __init__(self, client: OpenAI):
        self.client = client

    def prompt(self, user_query: str) -> ChatCompletion:
        # Убрана задержка, так как она не нужна при использовании потоков
        response = self.client.chat.completions.create(
            model="x-ai/grok-4.1-fast",
            messages=[{"role": "user", "content": user_query}]
        )
        return response


# --- ФУНКЦИЯ: Работа с CSV (ДОБАВЛЕНА БЛОКИРОВКА) ---
def add_to_csv_file_safe(result_data: List[str], part_title: str, information_ans: str) -> bool:
    """
    Проверяет совпадение заголовков и записывает данные в CSV файл,
    используя модуль csv, с использованием потокобезопасной блокировки.
    """
    title_from_response = result_data[0].strip()
    title_from_request = part_title.strip()

    logging.info(f'Запрос и ответ одинаковые: {title_from_response == title_from_request}')
    print(f"Название из запроса: {title_from_request}")
    print(f"Название из ответа: {title_from_response}")
    print(f"Совпадение: {title_from_response == title_from_request}")

    if title_from_response == title_from_request:
        genre = result_data[1]

        # --- КРИТИЧЕСКАЯ СЕКЦИЯ: ИСПОЛЬЗУЕМ БЛОКИРОВКУ ---
        with CSV_LOCK:
            try:
                # Запись данных в CSV
                with open(f'genre_csv/{genre}.csv', 'a', encoding='utf-8', newline='') as file_add:
                    writer = csv.writer(file_add)
                    writer.writerow(result_data)

                with open('count.txt', 'a', encoding='utf-8') as file_add:
                    file_add.write(f'{title_from_request}\n')

                logging.info(f'Удачно добавлен фильм {title_from_request} в файл {genre}.csv')
                return True
            except Exception as e:
                logging.error(f'Ошибка при записи в CSV: {e}', exc_info=True)
                return False
    else:
        # Логирование различий, если они есть
        for i in range(min(len(title_from_response), len(title_from_request))):
            if title_from_response[i] != title_from_request[i]:
                logging.info(f"Различие в позиции {i}: '{title_from_response[i]}' vs '{title_from_request[i]}'")
        return False


@Retry(max_retries=2)
def process(film: str, prompt_template: str) -> List[str]:
    """
    Обрабатывает один фильм: форматирует промпт, вызывает API, парсит ответ и сохраняет.
    Возвращает результат, или вызывает исключение при ошибке.
    """
    # 1. Форматирование промпта
    film_title = film.strip()
    request_prompt = prompt_template.format(title=film_title)

    # 2. Вызов API
    answer = client_user.prompt(request_prompt)

    # 3. Парсинг ответа
    try:
        information_ans = answer.choices[0].message.content.split('\n')[1]
    except IndexError:
        information_ans = answer.choices[0].message.content

    # Парсинг CSV-подобной строки
    res = [item.strip() for item in re.split(r',(?=\S)', information_ans)]

    logging.info(f'Ответ на промпт (строка): {information_ans}')
    logging.info(f'Парсинг (список): {res}')

    if len(res) < 2:
        raise IndexError(
            f"Недостаточно элементов в ответе для парсинга (получено {len(res)}). Ответ: {information_ans}")

    # 4. Сохранение данных и проверка заголовка
    # Эта функция теперь потокобезопасна благодаря CSV_LOCK
    responds = add_to_csv_file_safe(res, film_title, information_ans)
    print(responds)
    return res


# --- Главный блок выполнения (Оптимизированная инициализация) ---

env = Env()
env.read_env()
api_key = env("API_KEY")

# Инициализация клиента
client_user = prompter(OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key))

# ОПТИМИЗАЦИЯ 1: Загрузка шаблона промпта один раз
try:
    with open("prompt1.txt", "r", encoding="utf-8") as file_for_prompt:
        content = file_for_prompt.read()
        prompt_template = content.replace(content.split('\n')[0], "Название фильма: {title}")
    logging.info('Шаблон промпта успешно загружен.')
except FileNotFoundError:
    logging.error("Файл 'prompt1.txt' не найден.", exc_info=True)
    raise

# Загрузка списка фильмов
try:
    with open('films_for_review.txt', 'r', encoding='utf-8') as file:
        films_list = [f.strip() for f in file.readlines() if f.strip()]
except FileNotFoundError:
    logging.error("Файл 'films_for_review.txt' не найден.", exc_info=True)
    raise

print(f"Найдено {len(films_list)} фильмов для обработки. Используется {MAX_WORKERS} потоков.")
start_time = time.time()

# --- ОПТИМИЗАЦИЯ 2: ПАРАЛЛЕЛЬНАЯ ОБРАБОТКА С ИСПОЛЬЗОВАНИЕМ ThreadPoolExecutor ---
# Используем executor.map для применения функции process ко всем элементам films_list
# Передаем prompt_template как дополнительный аргумент.

with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    # `executor.map` применяет функцию `process` к каждому элементу `films_list`.
    # `prompt_template` передается как второй (и последующий) аргумент всем вызовам `process`.
    # `executor.map` возвращает итератор результатов в том же порядке, что и входные данные.
    results = executor.map(process, films_list, [prompt_template] * len(films_list))

    # Обработка результатов и исключений
    for i, future in enumerate(concurrent.futures.as_completed(results)):
        film = films_list[i] # Примечание: as_completed не сохраняет порядок, но для логирования это не критично
        try:
            result = future.result()
            print(f"[{i+1}/{len(films_list)}] Успешно обработан фильм: {result[0]}")
        except Exception as e:
            # Исключения, поднятые внутри process (включая Retry) будут пойманы здесь
            print(f"[{i+1}/{len(films_list)}] Критическая ошибка при обработке фильма {film}: {e}")
            logging.error(f"Критическая ошибка при обработке фильма {film}", exc_info=True)

end_time = time.time()
print(f"\nОбработка завершена. Общее время: {end_time - start_time:.2f} секунд.")
