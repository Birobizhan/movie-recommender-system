import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMovieById } from '../api';

// --- ФУНКЦИЯ ДЛЯ КОМБИНИРОВАННОГО РЕЙТИНГА ---
const calculateCombinedRating = (movie) => {
    const ratings = [];
    const kp = Number(movie?.kp_rating) || 0;
    if (kp > 0) ratings.push(kp);
    const imdb = Number(movie?.imdb_rating) || 0;
    if (imdb > 0) ratings.push(imdb);
    const critics = Number(movie?.critics_rating) || 0;
    if (critics > 0) ratings.push(critics);
    const count = ratings.length;

    if (count === 0) return 'N/A';

    const sum = ratings.reduce((a, b) => a + b, 0);
    const average = sum / count;
    return average.toFixed(1);
};
// ----------------------------------------------------

// --- УНИВЕРСАЛЬНАЯ ПРОВЕРКА ЗНАЧЕНИЯ ---
const hasValue = (value) => {
    if (value === null || value === undefined) return false;
    // Для массивов: проверяем, что массив не пуст
    if (Array.isArray(value)) {
        if (value.length === 0) return false;
        // Для массивов внутри массивов (как актеры) проверяем, что хотя бы один элемент не пуст
        return value.some(item => hasValue(item));
    }
    // Для строк: проверяем, что не пустая строка и не "None"
    if (typeof value === 'string') return value.trim() !== '' && value.trim().toLowerCase() !== 'none';
    // Для чисел: проверяем, что не 0 (если 0 - это не валидное значение, как для года)
    if (typeof value === 'number') return value !== 0 && !isNaN(value);
    // Для объектов: проверяем, что это не пустой объект
    if (typeof value === 'object' && Object.keys(value).length === 0) return false;

    return true;
};
// ----------------------------------------------------

// --- БЕЗОПАСНОЕ ИЗВЛЕЧЕНИЕ РЕЖИССЕРА ---
const getDirectorName = (directorData) => {
    if (!directorData) return '';

    // Если directorData - это массив [ID, Имя]
    if (Array.isArray(directorData) && directorData.length > 1 && typeof directorData[1] === 'string') {
      return directorData[1];
    }

    // Если данные пришли как массив, содержащий строку с разделителем "; ID; Name"
    if (Array.isArray(directorData) && typeof directorData[0] === 'string') {
        const parts = directorData[0].split(';');
        return parts.length > 1 ? parts.pop().trim() : directorData[0].trim();
    }

    // Если directorData - это просто строка
    if (typeof directorData === 'string') {
      return directorData;
    }

    return '';
};
// ----------------------------------------------------

// --- БЕЗОПАСНОЕ ИЗВЛЕЧЕНИЕ АКТЕРОВ (ИСПРАВЛЕНО ДЛЯ ДВОЙНОЙ ВЛОЖЕННОСТИ) ---
const renderCastList = (personsData) => {
    if (!hasValue(personsData) || !Array.isArray(personsData)) return null;

    let castList = personsData;

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
    if (!Array.isArray(castList)) return null;

    return castList
      .map((person, index) => {
        // Проверяем, что person - это массив [ID, Name]
        if (Array.isArray(person) && person.length >= 2) {
            const personId = person[0];
            const personName = person[1];
            return (
              <li key={personId || index}>
                {/* Используем Link, даже если ID может быть undefined, для целостности UI */}
                <Link to={personId ? `/person/${personId}` : '#'}>{personName || 'Неизвестный актер'}</Link>
              </li>
            );
        }
        return null;
      })
      .filter(item => item) // Убираем null-элементы
      .slice(0, 10); // Ограничиваем список до 10 актеров
}


const MoviePage = () => {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null); // Добавляем состояние ошибки

  useEffect(() => {
    setLoading(true);
    setError(null);
    getMovieById(id)
      .then((response) => {
        setMovie(response.data);
      })
      .catch((err) => {
        console.error("Ошибка при загрузке фильма:", err);
        const status = err.response?.status || 'Network Error';
        if (status === 404) {
             setError(`Фильм с ID ${id} не найден.`);
        } else {
             setError(`Не удалось загрузить данные фильма. Проверьте соединение и бэкенд (Status: ${status}).`);
        }
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return (
      <main>
          <div className="page-container" style={{color: "#f0f0f0", padding: "20px"}}>Загрузка...</div>
      </main>
  );

  if (error) return (
      <main>
          <div className="page-container" style={{color: "red", padding: "20px"}}>
              <h1>Ошибка загрузки</h1>
              <p>{error}</p>
              <Link to="/" style={{color: "#55aaff", marginTop: "15px", display: "inline-block"}}>← Назад</Link>
          </div>
      </main>
  );

  // Фильм загружен, но может быть пуст (например, если API вернуло {} и не выдало 404)
  if (!movie || Object.keys(movie).length === 0) return (
    <main>
        <div className="page-container" style={{color: "#f0f0f0", padding: "20px"}}>
            Фильм не найден или база данных пуста.
            <Link to="/" style={{color: "#55aaff", marginTop: "15px", display: "inline-block"}}>← Назад</Link>
        </div>
    </main>
  );


  // --- Расчеты и форматирование с защитой ---
  const combinedRating = calculateCombinedRating(movie);

  const genresString = Array.isArray(movie.genres) ? movie.genres.join(', ') : '';
  const directorName = getDirectorName(movie.director);
  const castList = renderCastList(movie.persons);

  const totalMinutes = movie.movie_length || 0;
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  const runtimeFormatted = totalMinutes > 0 ? `${hours} ч ${minutes} мин` : '';

  const movieYear = movie.year_release;
  const ageRating = movie.age_rating;
  const budget = movie.budget;
  const feesWorld = movie.fees_world;
  const premiere = movie.world_premiere;

  return (
    <main>
        <div className="page-container movie-detail-page">
            <Link to="/" style={{color: "#888", marginBottom: "20px", display: "block"}}>←Назад</Link>
            <div className="movie-header-section">

                {/* === ЛЕВАЯ КОЛОНКА: ПОСТЕР И ДЕЙСТВИЯ === */}
                <div className="poster-column">
                    {movie.poster_url ? (
                        <img
                            src={movie.poster_url}
                            alt={movie.title}
                            className="detail-poster"
                            onError={(e) => {
                                e.target.onerror = null;
                                e.target.src="https://placehold.co/300x450/333333/ffffff?text=Poster+Not+Found";
                            }}
                        />
                    ) : (
                        <div className="detail-poster-placeholder" style={{backgroundImage: "url(https://placehold.co/300x450/333333/ffffff?text=Poster+Not+Available)"}}></div>
                    )}

                    <div className="action-button-group">
                        <button className="add-to-list-btn">
                            <span className="icon">+</span>
                            Добавить в списки
                        </button>
                    </div>
                </div>

                {/* === ЦЕНТРАЛЬНАЯ КОЛОНКА: ИНФО И ОПИСАНИЕ === */}
                <div className="info-column">
                    <h1 className="movie-title-header">
                        {movie.title || movie.english_title || 'Название неизвестно'} ({hasValue(movieYear) ? movieYear : '—'})
                    </h1>

                    {/* Кнопки действий */}
                    <div className="action-buttons-line">
                        <button className="btn-watch-later">+ Буду смотреть</button>
                        <span className="icon">•••</span>
                    </div>

                    <h2>О фильме</h2>
                    <div className="movie-meta-table">
                        {/* 1. Год производства */}
                        {hasValue(movieYear) && (
                            <div className="meta-item"><span className="label">Год производства: </span><span className="value">{movieYear}</span></div>
                        )}
                        {/* 2. Страна */}
                        {hasValue(movie.countries) && (
                            <div className="meta-item"><span className="label">Страна: </span><span className="value">{movie.countries.join(', ')}</span></div>
                        )}
                        {/* 3. Жанры */}
                        {hasValue(genresString) && (
                            <div className="meta-item"><span className="label">Жанры: </span><span className="value">{genresString}</span></div>
                        )}
                        {/* 4. Режиссер */}
                        {hasValue(directorName) && (
                            <div className="meta-item"><span className="label">Режиссер: </span><span className="value">{directorName}</span></div>
                        )}
                        {/* 5. Бюджет */}
                        {hasValue(budget) && (
                            <div className="meta-item"><span className="label">Бюджет: </span><span className="value">{budget}</span></div>
                        )}
                        {/* 6. Сборы */}
                        {hasValue(feesWorld) && (
                            <div className="meta-item"><span className="label">Сборы: </span><span className="value">{feesWorld}</span></div>
                        )}
                        {/* 7. Премьера */}
                        {hasValue(premiere) && (
                            <div className="meta-item"><span className="label">Премьера: </span><span className="value">{premiere}</span></div>
                        )}
                        {/* 8. Возраст */}
                        {hasValue(ageRating) && (
                            <div className="meta-item"><span className="label">Возраст: </span><span className="value">{ageRating}+</span></div>
                        )}
                        {/* 9. Время */}
                        {hasValue(runtimeFormatted) && (
                            <div className="meta-item"><span className="label">Время: </span><span className="value">{runtimeFormatted}</span></div>
                        )}

                        {/* Дополнительные рейтинги для прозрачности */}
                        <div className="meta-item"><span className="label">Рейтинг КП: </span><span className="value">{hasValue(movie.kp_rating) ? movie.kp_rating.toFixed(3) : '—'}</span></div>
                        <div className="meta-item"><span className="label">Рейтинг IMDb: </span><span className="value">{hasValue(movie.imdb_rating) ? movie.imdb_rating.toFixed(1) : '—'}</span></div>
                        <div className="meta-item"><span className="label">Рейтинг Критиков: </span><span className="value">{hasValue(movie.critics_rating) ? movie.critics_rating.toFixed(1) : '—'}</span></div>
                    </div>

                    {/* === БЛОК ОПИСАНИЯ === */}
                    {hasValue(movie.description) && (
                        <>
                            <h2>Описание</h2>
                            <div className="movie-description">
                                <p>{movie.description}</p>
                            </div>
                        </>
                    )}
                </div>

                {/* === ПРАВАЯ КОЛОНКА: РЕЙТИНГ И АКТЕРЫ === */}
                <div className="rating-column">
                    <div className="main-rating">{combinedRating}</div>
                    <p className="rating-subtitle">{hasValue(movie.sum_votes) ? movie.sum_votes.toLocaleString() : '0'} оценок</p>
                    {/* Примерное число просмотров, если есть sum_votes */}
                    {hasValue(movie.sum_votes) && (
                        <p className="rating-subtitle">{(movie.sum_votes * 5).toLocaleString()} просмотров (прим.)</p>
                    )}

                    <button className="rate-button">Оценить ★</button>

                    {/* Показываем актеров, только если есть список */}
                    {hasValue(castList) && (
                        <>
                            <h2 className="cast-header">Актерский состав:</h2>
                            <ul className="cast-list">{castList}</ul>
                        </>
                    )}
                </div>

            </div>
        </div>
    </main>
  );
};

export default MoviePage;