from imdb import IMDb

# Создаем экземпляр объекта IMDb
ia = IMDb()

# Ищем фильм
movie_title = 'everything everywhere all at once'
search_results = ia.search_movie(movie_title)

if search_results:
    # Берем первый результат (наиболее релевантный)
    movie = search_results[0]
    # Загружаем полную информацию о фильме
    ia.update(movie)

    print(f"Название: {movie['title']}")
    print(f"Год выпуска: {movie['year']}")
    if 'rating' in movie:
        print(f"Рейтинг IMDb: {movie['rating']}")
    if 'plot' in movie:
        print(f"Сюжет: {movie['plot'][0]}")
else:
    print(f"Фильм '{movie_title}' не найден.")
