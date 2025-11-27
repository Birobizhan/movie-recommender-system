import requests
from bs4 import BeautifulSoup
import time


def fetch_page(page_number, session):
    """
    Функция для загрузки и парсинга одной страницы.
    Принимает номер страницы и сессию requests для переиспользования соединения.
    """
    url = f'https://kino.mail.ru/cinema/all/?year=1960&year=2022&page={page_number}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 YaBrowser/25.8.0.0 Safari/537.36'
    }

    try:
        with session.get(url, headers=headers, timeout=10) as response:
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            films = [header.text for header in soup.find_all('span', class_='link__text')]
            return films

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении страницы {page_number}: {e}")
        return []


def optimized_scraper():
    pages_to_scrape = [1]
    time.sleep(1)
    with requests.Session() as session:
        results = [fetch_page(p, session) for p in pages_to_scrape]

    films_list = [film for page_films in results for film in page_films]

    return films_list


start_time = time.time()
films = optimized_scraper()
end_time = time.time()
films = list(set(films))
films.remove('Скрыть')
films.remove('Отменить')
films.remove('Показать')

print(f"Общее количество фильмов: {len(films)}")
print(f"Время выполнения: {end_time - start_time:.2f} секунд")
print(films)

with open('all_films.txt', 'a', encoding='utf-8') as file:
    for i in films:
        file.write(f'{i}\n')
