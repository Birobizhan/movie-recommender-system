import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getMovies } from '../api';

// --- ФУНКЦИЯ ДЛЯ КОМБИНИРОВАННОГО РЕЙТИНГА ---
const calculateCombinedRating = (movie) => {
    const ratings = [];

    // Проверяем и добавляем только положительные оценки
    const kp = Number(movie.kp_rating) || 0;
    if (kp > 0) ratings.push(kp);

    const imdb = Number(movie.imdb_rating) || 0;
    if (imdb > 0) ratings.push(imdb);

    const critics = Number(movie.critics_rating) || 0;
    if (critics > 0) ratings.push(critics);

    const count = ratings.length;

    // Если нет оценок для учета, возвращаем N/A
    if (count === 0) return 'N/A';

    const sum = ratings.reduce((a, b) => a + b, 0);
    const average = sum / count;

    // Форматируем до одной цифры после запятой
    return average.toFixed(1);
};
// ----------------------------------------------------


// --- БЕЗОПАСНОЕ ИЗВЛЕЧЕНИЕ РЕЖИССЕРА (Оставлена без изменений) ---
const getDirectorName = (directorData) => {
    // Проверка на пустые данные или не-массив
    if (!Array.isArray(directorData) || directorData.length === 0) return 'Неизвестен';

    // В списке, данные о режиссере часто приходят как массив с одной строкой: ["55971; Пол Верховен"]
    const directorString = directorData[0];

    // Проверяем, что это строка, и безопасно извлекаем имя
    if (typeof directorString === 'string') {
        // Разделяем строку по ';' и берем последний элемент (имя), убирая пробелы
        const parts = directorString.split(';');
        return parts.pop().trim() || 'Неизвестен';
    }

    return 'Неизвестен';
};

// --- БЕЗОПАСНОЕ ИЗВЛЕЧЕНИЕ АКТЕРОВ (ИСПРАВЛЕНО ДЛЯ ДВОЙНОЙ ВЛОЖЕННОСТИ) ---
const getMainActors = (personsArray) => {
    if (!personsArray || personsArray.length === 0) return 'Актеры не указаны';

    let castList = personsArray;

    // Если структура [[[...]]], то нужно распаковать внешний массив
    if (Array.isArray(castList) && castList.length === 1 && Array.isArray(castList[0])) {
        // Если castList[0] — это массив, содержащий другой массив, как в вашем первом примере
        if (Array.isArray(castList[0][0]) && castList[0].length === 1) {
             castList = castList[0][0]; // [[[...]]] -> [...]
        } else {
             castList = castList[0]; // [[...]] -> [...]
        }
    }

    // После распаковки убеждаемся, что мы имеем дело с массивом [ID, Name]
    if (!Array.isArray(castList)) return 'Актеры не указаны';

    const actorNames = castList
      .slice(0, 3) // Берем только первых 3 актеров для списка
      .map(person => {
        // Каждый person должен быть массивом [ID, Name]
        return Array.isArray(person) && person.length >= 2 ? person[1] : null;
      })
      .filter(name => name); // Фильтруем пустые имена

    return actorNames.join(', ') || 'Актеры не указаны';
}


const HomePage = () => {
  const [movies, setMovies] = useState([]);
  const [isLoading, setIsLoading] = useState(true); // Состояние загрузки
  const [error, setError] = useState(null); // Состояние ошибки

  useEffect(() => {
    setIsLoading(true);
    setError(null);

    getMovies()
      .then((response) => {
        setMovies(response.data);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error("Ошибка при загрузке фильмов:", err);
        const status = err.response?.status || 'Network Error';
        setError(`Не удалось загрузить фильмы. Проверьте бэкенд (Status: ${status}).`);
        setIsLoading(false);
      });
  }, []);

  if (isLoading) {
    return (
      <main>
        <div className="page-container">
          <div className="main-content">
            <h1>Топ фильмов</h1>
            <p style={{ color: "#aaa" }}>Загрузка...</p>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="error-screen">
        <div className="page-container">
          <h1 style={{ color: "red" }}>Ошибка!</h1>
          <p style={{ color: "#f0f0f0" }}>{error}</p>
          <p style={{ color: "#f0f0f0" }}>Пожалуйста, убедитесь, что ваш бэкенд (http://localhost:8000) запущен и отвечает.</p>
        </div>
      </main>
    );
  }

  return (
    <main>
      <div className="page-container">
        {/* === ОСНОВНОЕ СОДЕРЖИМОЕ (ЛЕВАЯ КОЛОНКА) === */}
        <div className="main-content top-movies">
          <h1>Топ 250 фильмов</h1>
          <p className="subtitle">
            По формуле: среднее арифметическое оценок (Кинопоиск, IMDb, Критики).
          </p>
          <div className="filters">
            <span>Просмотрено: {movies.length} из 250 фильмов</span>
            <a href="#">Жанр &#x25BC;</a>
            <a href="#">Дата выхода &#x25BC;</a>
            <a href="#">Сортировать по &#x25BC;</a>
          </div>

          <ul className="movie-list">
            {movies.length === 0 ? (
                <p style={{ color: "#aaa", padding: "20px 0" }}>Фильмов пока нет. Запустите скрипт импорта данных.</p>
            ) : (
                movies.map((movie, index) => {
                    // ИСПОЛЬЗУЕМ УПРОЩЕННУЮ ЛОГИКУ ИЗВЛЕЧЕНИЯ
                    const directorName = getDirectorName(movie.director);
                    const actors = getMainActors(movie.persons);
                    // Безопасная обработка genres
                    const genres = Array.isArray(movie.genres) ? movie.genres.join(', ') : (movie.genres || '—');
                    const combinedRating = calculateCombinedRating(movie);

                    return (
                    <li className="movie-item" key={movie.id}>
                        {/* 1. Номер (rank) - используем индекс + 1 */}
                        <span className="rank">{movie.rank || index + 1}</span>

                        {/* 2. Постер */}
                        {movie.poster_url ? (
                            <img
                                src={movie.poster_url}
                                alt={movie.title}
                                className="poster-placeholder"
                                style={{width: '60px', height: '90px', objectFit: 'cover'}}
                                // Добавляем обработку ошибки загрузки постера
                                onError={(e) => { e.target.onerror = null; e.target.style.display = 'none'; }}
                            />
                        ) : (
                            <div className="poster-placeholder" style={{width: '60px', height: '90px'}}></div>
                        )}

                        {/* 3. Детали */}
                        <div className="details">
                            <h4>
                                <Link to={`/movie/${movie.id}`}>
                                    {movie.title || movie.english_title || 'Название неизвестно'}
                                </Link>
                            </h4>
                            {/* Мета: Год, Длительность */}
                            <div className="meta">
                                {movie.year_release || 'N/A'}, {movie.movie_length ? `${movie.movie_length} мин.` : 'N/A'}
                            </div>
                            {/* Описание/Жанры/Режиссер/Актеры */}
                            <div className="crew">
                                {genres} | Режиссер: {directorName}
                            </div>
                            <div className="cast">
                                В ролях: {actors}
                            </div>
                        </div>

                        {/* 4. Рейтинг */}
                        <div className="rating">
                            <span className="rating-value">
                                {combinedRating}
                            </span>
                            <div className="votes">{movie.sum_votes ? movie.sum_votes.toLocaleString() : '0'}</div>
                        </div>

                        {/* 5. Действия (Кнопки) */}
                        <div className="actions">
                            <button className="btn-watch-later">+ Буду смотреть</button>
                            <span className="icon">★</span>
                            <span className="icon">•••</span>
                        </div>
                    </li>
                    )
                })
            )}
          </ul>
        </div>

        {/* === САЙДБАР (ПРАВАЯ КОЛОНКА) === */}
        <div className="sidebar">
            <h3>Популярные списки</h3>
            <div className="sidebar-list">
                {[...Array(5)].map((_, i) => (
                    <div className="sidebar-item" key={i}>
                        <div className="sidebar-details">
                            <h5>Самые популярные фильмы</h5>
                            <p>Фильмы с наибольшим количеством просмотров на сайте</p>
                            <p>100 фильмов</p>
                        </div>
                        <div
                            className="sidebar-poster"
                            style={{
                                backgroundImage: `url(https://placehold.co/80x110/333333/ffffff?text=Poster)`,
                                backgroundSize: 'cover',
                                backgroundPosition: 'center'
                            }}
                        ></div>
                    </div>
                ))}
            </div>
        </div>
      </div>
    </main>
  );
};

export default HomePage;