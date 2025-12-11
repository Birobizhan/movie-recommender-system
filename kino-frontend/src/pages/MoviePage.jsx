import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMovieById, getMovieReviews, createReview, getCurrentUser, getUserLists, addMoviesToList, removeMoviesFromList, ensureWatchlist, getListById } from '../api';

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
  const [reviews, setReviews] = useState([]);
  const [reviewRating, setReviewRating] = useState('');
  const [reviewContent, setReviewContent] = useState('');
  const [reviewError, setReviewError] = useState('');
  const [myLists, setMyLists] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [watchlistId, setWatchlistId] = useState(null);
  const [inWatchlist, setInWatchlist] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      getMovieById(id).then((r)=>r.data),
      getMovieReviews(id).then((r)=>r.data)
    ])
      .then(([movieData, reviewsData]) => {
        setMovie(movieData);
        setReviews(reviewsData || []);
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

    getCurrentUser()
      .then((resp) => {
        setCurrentUser(resp.data);
        return Promise.all([
          getUserLists(resp.data.id),
          ensureWatchlist(resp.data.id)
        ]);
      })
      .then(async ([listsResp, wl]) => {
        setMyLists(listsResp.data || []);
        setWatchlistId(wl.id);
        try {
          const wlData = await getListById(wl.id);
          const ids = new Set((wlData.data.movies || []).map((m) => m.id));
          setInWatchlist(ids.has(Number(id)));
        } catch (e) {
          setInWatchlist(false);
        }
      })
      .catch(() => {});
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

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    setReviewError('');
    if (!reviewRating) {
      setReviewError('Укажите оценку');
      return;
    }
    try {
      const payload = {
        rating: Number(reviewRating),
        content: reviewContent || null,
        movie_id: Number(id),
      };
      const resp = await createReview(payload);
      setReviews([resp.data, ...reviews]);
      setReviewRating('');
      setReviewContent('');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Не удалось отправить отзыв';
      setReviewError(msg);
    }
  };

  const toggleWatchLater = async () => {
    if (!currentUser || !watchlistId) return;
    try {
      if (inWatchlist) {
        await removeMoviesFromList(watchlistId, [Number(id)]);
        setInWatchlist(false);
      } else {
        await addMoviesToList(watchlistId, [Number(id)]);
        setInWatchlist(true);
      }
    } catch (err) {
      console.error('watchlist toggle error', err);
    }
  };

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
                        {currentUser && (
                          <button
                            className={`btn-watch-later big ${inWatchlist ? 'in-list' : ''}`}
                            onClick={toggleWatchLater}
                          >
                            {inWatchlist ? '✓ В списке' : '+ Буду смотреть'}
                          </button>
                        )}
                    </div>
                </div>

                {/* === ЦЕНТРАЛЬНАЯ КОЛОНКА: ИНФО И ОПИСАНИЕ === */}
                <div className="info-column">
                    <h1 className="movie-title-header">
                        {movie.title || movie.english_title || 'Название неизвестно'} ({hasValue(movieYear) ? movieYear : '—'})
                    </h1>

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
                    {hasValue(movie.sum_votes) && (
                        <p className="rating-subtitle">{(movie.sum_votes * 5).toLocaleString()} просмотров (прим.)</p>
                    )}

                    {hasValue(castList) && (
                        <>
                            <h2 className="cast-header">Актерский состав:</h2>
                            <ul className="cast-list">{castList}</ul>
                        </>
                    )}
                </div>

            </div>

            {/* --- Отзывы --- */}
            <div style={{marginTop: '32px', display:'grid', gridTemplateColumns:'1fr 1fr', gap:'20px'}}>
              <div>
                <h2>Отзывы</h2>
                {reviews.length === 0 && <p style={{color:'#aaa'}}>Отзывов пока нет</p>}
                <ul style={{listStyle:'none', padding:0, display:'flex', flexDirection:'column', gap:'12px'}}>
                  {reviews.map((rev) => (
                    <li key={rev.id} style={{padding:'12px', border:'1px solid #333', borderRadius:'8px'}}>
                      <div style={{display:'flex', justifyContent:'space-between'}}>
                        <strong>Оценка: {rev.rating}</strong>
                        {rev.created_at && <span style={{color:'#888', fontSize:'0.85rem'}}>{new Date(rev.created_at).toLocaleString()}</span>}
                      </div>
                      {rev.content && <p style={{marginTop:'8px'}}>{rev.content}</p>}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h2>Оставить отзыв</h2>
                <form className="review-form" onSubmit={handleReviewSubmit}>
                    <div className="rating-row">
                        <span style={{color:'#ccc'}}>Ваша оценка:</span>
                        <div className="rating-stars-block">
                            {[...Array(10)].map((_, i) => {
                                const val = i + 1;
                                return (
                                    <button
                                        key={val}
                                        type="button"
                                        className={`star-btn ${val <= reviewRating ? 'active' : ''}`}
                                        onClick={() => setReviewRating(val)}
                                    >
                                        ★
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                    <textarea
                        rows={4}
                        placeholder="Ваш отзыв..."
                        value={reviewContent}
                        onChange={(e)=>setReviewContent(e.target.value)}
                    />
                    {!currentUser && <p style={{color:'#888', fontSize:'0.9rem'}}>Для отправки нужен вход.</p>}
                    {reviewError && <p style={{color:'red'}}>{reviewError}</p>}
                    <button type="submit">Отправить</button>
                </form>
              </div>
            </div>
        </div>
    </main>
  );
};

export default MoviePage;