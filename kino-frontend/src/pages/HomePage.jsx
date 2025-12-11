import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { getMovies, getCurrentUser, ensureWatchlist, addMoviesToList, removeMoviesFromList, createReview, getMovieById, getListById } from '../api';

const GENRES = [
  'Боевик', 'Драма', 'Комедия', 'Фантастика', 'Фэнтези',
  'Триллер', 'Ужасы', 'Приключения', 'Семейный', 'Детектив',
  'Криминал', 'Исторический', 'Мелодрама'
];

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


const getDirectorName = (directorData) => {
    if (!directorData || (Array.isArray(directorData) && directorData.length === 0)) return 'Неизвестен';
    // directorData уже нормализован до списка строк в БД
    if (Array.isArray(directorData)) {
        const first = directorData[0];
        return typeof first === 'string' ? first : 'Неизвестен';
    }
    if (typeof directorData === 'string') return directorData;
    return 'Неизвестен';
};

const getMainActors = (personsArray) => {
    if (!personsArray || personsArray.length === 0) return 'Актеры не указаны';
    // persons уже нормализованы до списка строк в БД
    const actorNames = personsArray.slice(0, 3).map((p) => (typeof p === 'string' ? p : null)).filter(Boolean);
    return actorNames.join(', ') || 'Актеры не указаны';
};


const HomePage = () => {
  const [movies, setMovies] = useState([]);
  const [me, setMe] = useState(null);
  const [watchlistId, setWatchlistId] = useState(null);
  const [pending, setPending] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const [searchParams] = useSearchParams();
  const [search, setSearch] = useState(searchParams.get('q') || '');
  const [genre, setGenre] = useState('');
  const [year, setYear] = useState('');
  const [minRating, setMinRating] = useState('');
  const [sortBy, setSortBy] = useState('rating'); // rating | votes
  const [activeRatingMovie, setActiveRatingMovie] = useState(null);
  const [userRatings, setUserRatings] = useState({});
  const [watchlistSet, setWatchlistSet] = useState(new Set());

  const fetchMovies = () => {
    setIsLoading(true);
    setError(null);
    const params = {
      limit: 250,
      sort_by: sortBy,
    };
    if (search) params.q = search;
    if (genre) params.genre = genre;
    if (year) params.year = year;
    if (minRating) params.min_rating = minRating;

    getMovies(params)
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
  };

  useEffect(() => {
    const qParam = searchParams.get('q') || '';
    setSearch(qParam);
  }, [searchParams]);

  useEffect(() => {
    fetchMovies();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sortBy, search, genre, year, minRating]);

  useEffect(() => {
    getCurrentUser()
      .then(async (resp) => {
        setMe(resp.data);
        const wl = await ensureWatchlist(resp.data.id);
        setWatchlistId(wl.id);
        try {
          const wlData = await getListById(wl.id);
          const ids = new Set((wlData.data.movies || []).map((m) => m.id));
          setWatchlistSet(ids);
        } catch (e) {
          setWatchlistSet(new Set());
        }
      })
      .catch(() => setMe(null));
  }, []);

  const toggleWatchLater = async (movieId, inWatchlist) => {
    if (!me || !watchlistId) return;
    setPending(true);
    try {
      if (inWatchlist) {
        await removeMoviesFromList(watchlistId, [movieId]);
        setWatchlistSet((prev) => {
          const next = new Set(prev);
          next.delete(movieId);
          return next;
        });
      } else {
        await addMoviesToList(watchlistId, [movieId]);
        setWatchlistSet((prev) => new Set(prev).add(movieId));
      }
    } finally {
      setPending(false);
    }
  };

  const submitQuickRating = async (movieId, rating) => {
    if (!me) return;
    try {
      await createReview({ movie_id: movieId, rating, content: '' });
      // перезагрузим одну карточку
      const updated = await getMovieById(movieId);
      setMovies((prev) => prev.map((m) => (m.id === movieId ? updated.data : m)));
      setUserRatings((prev) => ({ ...prev, [movieId]: rating }));
      setActiveRatingMovie(null);
    } catch (e) {
      console.error('rating error', e);
    }
  };

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
            <span style={{color:'#9aa0b5'}}>Показано: {movies.length} из 250</span>
            <select value={genre} onChange={(e)=>setGenre(e.target.value)}>
              <option value="">Любой жанр</option>
              {GENRES.map(g => <option key={g} value={g}>{g}</option>)}
            </select>
            <input placeholder="Год" value={year} onChange={(e)=>setYear(e.target.value)} />
            <input placeholder="Мин. рейтинг" value={minRating} onChange={(e)=>setMinRating(e.target.value)} />
            <select value={sortBy} onChange={(e)=>setSortBy(e.target.value)}>
              <option value="rating">Рейтинг</option>
              <option value="votes">Популярность</option>
            </select>
            <button onClick={fetchMovies}>Применить</button>
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
                    const inWatchlist = watchlistSet.has(movie.id);
                    const reviewsCount = movie.reviews_count ?? (Array.isArray(movie.reviews) ? movie.reviews.length : 0);

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
                            <div className="votes">
                              {movie.sum_votes ? movie.sum_votes.toLocaleString() : '0'}
                              {reviewsCount ? ` • отзывов: ${reviewsCount}` : ''}
                            </div>
                        </div>

                        {/* 5. Действия (Кнопки) */}
                        <div className="actions" style={{display:'flex', gap:'8px', alignItems:'center', flexWrap:'wrap'}}>
                            {me ? (
                              <button
                                className={`btn-watch-later ${inWatchlist ? 'in-list' : ''}`}
                                disabled={pending}
                                onClick={() => toggleWatchLater(movie.id, inWatchlist)}
                              >
                                {inWatchlist ? '✓ В списке' : '+ Буду смотреть'}
                              </button>
                            ) : (
                              <Link to="/login" className="btn-watch-later">+ Буду смотреть</Link>
                            )}
                            <div className="stars" style={{position:'relative'}}>
                              <button
                                className="star-btn"
                                style={{
                                  padding:'0 6px',
                                  fontSize:'16px',
                                  lineHeight:'1.2',
                                  color: userRatings[movie.id] ? '#f2c94c' : '#9aa0b5'
                                }}
                                onClick={() => setActiveRatingMovie(activeRatingMovie === movie.id ? null : movie.id)}
                                title="Поставить оценку"
                              >
                                ★
                              </button>
                              {activeRatingMovie === movie.id && (
                                <div className="rating-popover" style={{position:'absolute', top:'28px', left:0, background:'#11141d', border:'1px solid #2a2f3f', borderRadius:'8px', padding:'6px', display:'flex', gap:'4px', zIndex:5}}>
                                  {[...Array(10)].map((_, i) => {
                                    const starVal = i + 1;
                                    const rated = userRatings[movie.id] || 0;
                                    return (
                                      <button
                                        key={starVal}
                                        className="star-btn"
                                        style={{
                                          padding:'2px 6px',
                                          fontSize:'14px',
                                          lineHeight:'1.2',
                                          color: starVal <= rated ? '#f2c94c' : '#9aa0b5'
                                        }}
                                        onClick={() => submitQuickRating(movie.id, starVal)}
                                        title={`Оценить на ${starVal}`}
                                      >
                                        ★
                                      </button>
                                    );
                                  })}
                                </div>
                              )}
                            </div>
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