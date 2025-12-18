import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { getMovies, getCurrentUser, ensureWatchlist, addMoviesToList, removeMoviesFromList, createReview, getMovieById, getListById, getUserReviews, getUserLists } from '../api';

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
  // Фильтры для ввода (не применяются сразу)
  const [genreInput, setGenreInput] = useState('');
  const [yearInput, setYearInput] = useState('');
  const [minRatingInput, setMinRatingInput] = useState('');
  const [sortByInput, setSortByInput] = useState('rating');
  // Применённые фильтры (используются для запроса)
  const [genre, setGenre] = useState('');
  const [year, setYear] = useState('');
  const [minRating, setMinRating] = useState('');
  const [sortBy, setSortBy] = useState('rating'); // rating | votes
  const [page, setPage] = useState(1);
  const pageSize = 250;
  const [activeRatingMovie, setActiveRatingMovie] = useState(null);
  const [userRatings, setUserRatings] = useState({});
  const [watchlistSet, setWatchlistSet] = useState(new Set());
  const [seenSet, setSeenSet] = useState(new Set());
  const [seenListId, setSeenListId] = useState(null);

  const fetchMovies = () => {
    setIsLoading(true);
    setError(null);
    const params = {
      limit: pageSize,
      skip: (page - 1) * pageSize,
      sort_by: sortBy,
    };
    if (search) params.q = search;
    if (genre) params.genre = genre;
    if (year) params.year = year;
    if (minRating) params.min_rating = minRating;

    getMovies(params)
      .then((response) => {
        const list = response.data || [];
        setMovies(list);
        // если у нас уже есть карта оценок пользователя — оставляем, иначе попытка построить из списка (если сервер вернул reviews)
        if (me && Object.keys(userRatings).length === 0) {
          const ratingsMap = {};
          list.forEach((m) => {
            if (Array.isArray(m.reviews)) {
              const own = m.reviews.find((r) => r.author_id === me.id || r.author?.id === me.id);
              if (own) ratingsMap[m.id] = own.rating;
            }
          });
          if (Object.keys(ratingsMap).length) {
            setUserRatings(ratingsMap);
          }
        }
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

  // Загрузка при изменении применённых фильтров или страницы
  useEffect(() => {
    fetchMovies();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, genre, year, minRating, sortBy, page]);

  // Синхронизация инпутов с применёнными фильтрами при первой загрузке
  useEffect(() => {
    setGenreInput(genre);
    setYearInput(year);
    setMinRatingInput(minRating);
    setSortByInput(sortBy);
  }, []);

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
        } catch {
          setWatchlistSet(new Set());
        }
        try {
          const listsResp = await getUserLists(resp.data.id);
          const viewed = listsResp.data?.find((l) => l.title?.toLowerCase() === 'просмотренные');
          if (viewed) {
            setSeenListId(viewed.id);
            try {
              const seenData = await getListById(viewed.id);
              const seenIds = new Set((seenData.data.movies || []).map((m) => m.id));
              setSeenSet(seenIds);
            } catch {
              setSeenSet(new Set());
            }
          }
        } catch {
          setSeenSet(new Set());
        }
        // Подтянем свои оценки один раз
        try {
          const reviewsResp = await getUserReviews(resp.data.id);
          const ratingsMap = {};
          (reviewsResp.data || []).forEach((r) => {
            if (r.movie_id && r.rating) ratingsMap[r.movie_id] = r.rating;
          });
          setUserRatings(ratingsMap);
        } catch {
          setUserRatings({});
        }
      })
      .catch(() => setMe(null));
  }, []);

  const applyFilters = () => {
    setGenre(genreInput);
    setYear(yearInput);
    setMinRating(minRatingInput);
    setSortBy(sortByInput);
    setPage(1);
  };

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

  const toggleSeen = async (movieId, isSeen) => {
    if (!me || !seenListId) return;
    try {
      if (isSeen) {
        await removeMoviesFromList(seenListId, [movieId]);
        setSeenSet((prev) => {
          const next = new Set(prev);
          next.delete(movieId);
          return next;
        });
      } else {
        await addMoviesToList(seenListId, [movieId]);
        setSeenSet((prev) => new Set(prev).add(movieId));
      }
    } catch (e) {
      console.error('toggle seen error', e);
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

  const canPrev = page > 1;
  const canNext = movies.length === pageSize;
  const pageButtons = Array.from({ length: 5 }, (_, i) => page - 2 + i).filter((p) => p > 0);

  return (
    <main>
      <div className="page-container">
        {/* === ОСНОВНОЕ СОДЕРЖИМОЕ (ЛЕВАЯ КОЛОНКА) === */}
        <div className="main-content top-movies">
          <h1>Фильмы</h1>
          <p className="subtitle">
            Показано по {pageSize} фильмов на страницу.
          </p>
          <div className="filters">
            <span style={{color:'#9aa0b5'}}>Показано: {movies.length}</span>
            <select value={genreInput} onChange={(e)=>setGenreInput(e.target.value)}>
              <option value="">Любой жанр</option>
              {GENRES.map(g => <option key={g} value={g}>{g}</option>)}
            </select>
            <input placeholder="Год" value={yearInput} onChange={(e)=>setYearInput(e.target.value)} />
            <input placeholder="Мин. рейтинг" value={minRatingInput} onChange={(e)=>setMinRatingInput(e.target.value)} />
            <select value={sortByInput} onChange={(e)=>setSortByInput(e.target.value)}>
              <option value="rating">Рейтинг</option>
              <option value="votes">Популярность</option>
            </select>
            <button onClick={applyFilters}>Применить</button>
          </div>

          <ul className="movie-list">
            {movies.length === 0 ? (
                <p style={{ color: "#aaa", padding: "20px 0" }}>Фильмов пока нет. Запустите скрипт импорта данных.</p>
            ) : (
                movies.map((movie, index) => {
                    const displayRank = (page - 1) * pageSize + index + 1;
                    const directorName = getDirectorName(movie.director);
                    const actors = getMainActors(movie.persons);
                    // Безопасная обработка genres
                    const genres = Array.isArray(movie.genres) ? movie.genres.join(', ') : (movie.genres || '—');
                    const combinedRating = calculateCombinedRating(movie);
                    const inWatchlist = watchlistSet.has(movie.id);
                    const reviewsCount = movie.reviews_count ?? (Array.isArray(movie.reviews) ? movie.reviews.length : 0);
                    const userRating = userRatings[movie.id];

                    return (
                    <li className="movie-item" key={movie.id}>
                        {/* 1. Номер (rank) с учётом пагинации */}
                        <span className="rank">{displayRank}</span>

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

                        {/* 4. Рейтинг и кнопки */}
                        <div className="actions">
                          <div className="rating">
                              <span className="rating-value">
                                  {combinedRating}
                              </span>
                              <div className="votes">
                                {movie.sum_votes ? movie.sum_votes.toLocaleString() : '0'}
                                {reviewsCount ? ` • отзывов: ${reviewsCount}` : ''}
                              </div>
                          </div>
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
                          <div className="stars">
                            {me && (
                              <button
                                className="icon-eye"
                                title={seenSet.has(movie.id) ? 'Просмотрено' : 'Отметить просмотренным'}
                                style={{
                                  color: seenSet.has(movie.id) ? '#6ab4ff' : '#9aa0b5'
                                }}
                                onClick={() => toggleSeen(movie.id, seenSet.has(movie.id))}
                              >
                                👁
                              </button>
                            )}
                            <button
                              className="star-btn"
                              style={{
                                color: userRating ? '#f2c94c' : '#9aa0b5'
                              }}
                              onClick={() => setActiveRatingMovie(activeRatingMovie === movie.id ? null : movie.id)}
                              title="Поставить оценку"
                            >
                              ★
                            </button>
                            {activeRatingMovie === movie.id && (
                              <div className="rating-popover">
                                {[...Array(10)].map((_, i) => {
                                  const starVal = i + 1;
                                  const rated = userRating || 0;
                                  return (
                                    <button
                                      key={starVal}
                                      className="star-btn"
                                      style={{
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
                        </div>
                    </li>
                    )
                })
            )}
          </ul>
          <div style={{ display: 'flex', gap: 12, marginTop: 16, alignItems: 'center', flexWrap: 'wrap' }}>
            <button
              disabled={!canPrev}
              onClick={() => canPrev && setPage((p) => Math.max(1, p - 1))}
              style={{
                padding: '10px 14px',
                borderRadius: 10,
                background: canPrev ? '#2f2f37' : '#1c1c22',
                color: '#f0f0f0',
                border: '1px solid #3a3a3d',
                cursor: canPrev ? 'pointer' : 'not-allowed'
              }}
            >
              Назад
            </button>
            <span style={{ color: '#9aa0b5' }}>Страница {page}</span>
            {pageButtons.map((p) => (
              <button
                key={p}
                onClick={() => setPage(p)}
                style={{
                  padding: '8px 12px',
                  borderRadius: 8,
                  background: p === page ? '#6ab4ff' : '#2f2f37',
                  color: p === page ? '#0f0f10' : '#f0f0f0',
                  border: '1px solid #3a3a3d',
                  cursor: 'pointer'
                }}
              >
                {p}
              </button>
            ))}
            <button
              disabled={!canNext}
              onClick={() => canNext && setPage((p) => p + 1)}
              style={{
                padding: '10px 14px',
                borderRadius: 10,
                background: canNext ? '#2f2f37' : '#1c1c22',
                color: '#f0f0f0',
                border: '1px solid #3a3a3d',
                cursor: canNext ? 'pointer' : 'not-allowed'
              }}
            >
              Вперёд
            </button>
          </div>
        </div>

        {/* Сайдбар убран по запросу пользователя */}
      </div>
    </main>
  );
};

export default HomePage;