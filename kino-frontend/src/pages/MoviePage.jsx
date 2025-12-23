import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMovieById, getMovieReviews, createReview, getCurrentUser, getUserLists, addMoviesToList, removeMoviesFromList, ensureWatchlist, getListById, getSimilarMovies } from '../api';

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

const hasValue = (value) => {
    if (value === null || value === undefined) return false;
    if (Array.isArray(value)) {
        if (value.length === 0) return false;
        return value.some(item => hasValue(item));
    }
    if (typeof value === 'string') return value.trim() !== '' && value.trim().toLowerCase() !== 'none';
    if (typeof value === 'number') return value !== 0 && !isNaN(value);
    if (typeof value === 'object' && Object.keys(value).length === 0) return false;

    return true;
};

const getDirectorName = (directorData) => {
    if (!directorData) return '';

    if (Array.isArray(directorData) && directorData.length > 1 && typeof directorData[1] === 'string') {
      return directorData[1];
    }

    if (Array.isArray(directorData) && typeof directorData[0] === 'string') {
        const parts = directorData[0].split(';');
        return parts.length > 1 ? parts.pop().trim() : directorData[0].trim();
    }

    if (typeof directorData === 'string') {
      return directorData;
    }

    return '';
};

const renderCastList = (personsData) => {
    if (!personsData || !Array.isArray(personsData) || personsData.length === 0) return null;

    if (typeof personsData[0] === 'string') {
      return personsData
        .slice(0, 10)
        .map((name, index) => (
          <li key={index}>{name}</li>
        ));
    }

    let castList = personsData;
    if (Array.isArray(castList) && castList.length === 1 && Array.isArray(castList[0])) {
        if (Array.isArray(castList[0][0]) && castList[0].length === 1) {
             castList = castList[0][0];
        } else {
             castList = castList[0];
        }
    }

    if (!Array.isArray(castList)) return null;

    return castList
      .map((person, index) => {
        if (Array.isArray(person) && person.length >= 2) {
            const personId = person[0];
            const personName = person[1];
            return (
              <li key={personId || index}>
                <Link to={personId ? `/person/${personId}` : '#'}>{personName || 'Неизвестный актер'}</Link>
              </li>
            );
        }
        return null;
      })
      .filter(Boolean)
      .slice(0, 10);
};


const MoviePage = () => {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [reviewRating, setReviewRating] = useState('');
  const [reviewContent, setReviewContent] = useState('');
  const [reviewError, setReviewError] = useState('');
  const [myLists, setMyLists] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [watchlistId, setWatchlistId] = useState(null);
  const [inWatchlist, setInWatchlist] = useState(false);
  const [showListPicker, setShowListPicker] = useState(false);
  const [listMembership, setListMembership] = useState({});
  const [similarMovies, setSimilarMovies] = useState([]);

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
             setError(`Фильм с ID ${id} не найден`);
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
        const lists = listsResp.data || [];
        setMyLists(lists);
        const currentMovieId = Number(id);
        const membership = {};
        lists.forEach((l) => {
          const ids = (l.movies || []).map((m) => m.id);
          membership[l.id] = ids.includes(currentMovieId);
        });
        setListMembership(membership);
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

    getSimilarMovies(id, 10)
      .then((resp) => {
        setSimilarMovies(resp.data || []);
      })
      .catch(() => {
        setSimilarMovies([]);
      });
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

  if (!movie || Object.keys(movie).length === 0) return (
    <main>
        <div className="page-container" style={{color: "#f0f0f0", padding: "20px"}}>
            Фильм не найден или база данных пуста.
            <Link to="/" style={{color: "#55aaff", marginTop: "15px", display: "inline-block"}}>← Назад</Link>
        </div>
    </main>
  );


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
  const formatMoney = (val) => {
    if (!val) return '';
    const raw = String(val).trim();

    const prefixMatch = raw.match(/^[^\d-+]+/);
    const suffixMatch = raw.match(/[^\d.,\s]+$/);
    const prefix = prefixMatch ? prefixMatch[0].trim() : '';
    const suffix = suffixMatch ? suffixMatch[0].trim() : '';


    const numericPart = raw
      .replace(prefix, '')
      .replace(suffix, '')
      .replace(/[^\d.,-]/g, '')
      .replace(/\s+/g, '');

    const num = Number(numericPart.replace(',', '.'));
    if (Number.isNaN(num)) return val;
    const formatted = new Intl.NumberFormat('ru-RU').format(num);

    const left = prefix ? `${prefix} ` : '';
    const right = suffix ? ` ${suffix}` : '';
    return `${left}${formatted}${right}`;
  };

  const budget = movie.budget;
  const feesWorld = movie.fees_world;
  const budgetFormatted = formatMoney(budget);
  const feesWorldFormatted = formatMoney(feesWorld);
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

  const toggleListMembership = async (listId) => {
    if (!currentUser) return;
    const movieIdNum = Number(id);
    const isIn = !!listMembership[listId];
    try {
      if (isIn) {
        await removeMoviesFromList(listId, [movieIdNum]);
      } else {
        await addMoviesToList(listId, [movieIdNum]);
      }
      setListMembership((prev) => ({ ...prev, [listId]: !isIn }));
      if (listId === watchlistId) {
        setInWatchlist(!isIn);
      }
    } catch (err) {
      console.error('toggle list membership error', err);
    }
  };

  return (
    <main>
        <div className="page-container movie-detail-page">
            <Link to="/" style={{color: "#888", marginBottom: "20px", display: "block"}}>←Назад</Link>
            <div className="movie-header-section">

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
                        {currentUser && myLists.length > 0 && (
                          <div style={{marginTop:'8px'}}>
                            <button
                              type="button"
                              className="btn-watch-later big"
                              onClick={() => setShowListPicker((v) => !v)}
                              style={{ width: '100%' }}
                            >
                              Добавить в списки
                            </button>
                            {showListPicker && (
                              <div className="list-picker">
                                <div className="list-picker-header">Выберите списки</div>
                                <div className="list-picker-body">
                                  {myLists.map((lst) => (
                                    <div className="list-picker-row" key={lst.id}>
                                      <span className="list-picker-title">{lst.title}</span>
                                      <input
                                        type="checkbox"
                                        checked={!!listMembership[lst.id]}
                                        onChange={() => toggleListMembership(lst.id)}
                                      />
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                    </div>
                </div>

                <div className="info-column">
                    <h1 className="movie-title-header">
                        {movie.title || movie.english_title || 'Название неизвестно'} ({hasValue(movieYear) ? movieYear : '—'})
                    </h1>

                    <h2>О фильме</h2>
                    <div className="movie-meta-table">
                        {hasValue(movieYear) && (
                            <div className="meta-item"><span className="label">Год производства: </span><span className="value">{movieYear}</span></div>
                        )}

                        {hasValue(movie.countries) && (
                            <div className="meta-item"><span className="label">Страна: </span><span className="value">{movie.countries.join(', ')}</span></div>
                        )}

                        {hasValue(genresString) && (
                            <div className="meta-item"><span className="label">Жанры: </span><span className="value">{genresString}</span></div>
                        )}

                        {hasValue(directorName) && (
                            <div className="meta-item"><span className="label">Режиссер: </span><span className="value">{directorName}</span></div>
                        )}

                        {hasValue(budget) && (
                            <div className="meta-item"><span className="label">Бюджет: </span><span className="value">{budgetFormatted}</span></div>
                        )}

                        {hasValue(feesWorld) && (
                            <div className="meta-item"><span className="label">Сборы: </span><span className="value">{feesWorldFormatted}</span></div>
                        )}

                        {hasValue(premiere) && (
                            <div className="meta-item"><span className="label">Премьера: </span><span className="value">{premiere}</span></div>
                        )}

                        {hasValue(ageRating) && (
                            <div className="meta-item"><span className="label">Возраст: </span><span className="value">{ageRating}+</span></div>
                        )}

                        {hasValue(runtimeFormatted) && (
                            <div className="meta-item"><span className="label">Время: </span><span className="value">{runtimeFormatted}</span></div>
                        )}

                        <div className="meta-item"><span className="label">Рейтинг КП: </span><span className="value">{hasValue(movie.kp_rating) ? movie.kp_rating.toFixed(3) : '—'}</span></div>
                        <div className="meta-item"><span className="label">Рейтинг IMDb: </span><span className="value">{hasValue(movie.imdb_rating) ? movie.imdb_rating.toFixed(1) : '—'}</span></div>
                        <div className="meta-item"><span className="label">Рейтинг Критиков: </span><span className="value">{hasValue(movie.critics_rating) ? movie.critics_rating.toFixed(1) : '—'}</span></div>
                    </div>

                    {hasValue(movie.description) && (
                        <>
                            <h2>Описание</h2>
                            <div className="movie-description">
                                <p>{movie.description}</p>
                            </div>
                        </>
                    )}

                    {similarMovies.length > 0 && (
                        <>
                            <h2 style={{ marginTop: '2rem', color: '#111' }}>Похожие фильмы</h2>
                            <div 
                                className="similar-movies-carousel similar-movies-carousel-light"
                                style={{
                                    width: '100%',
                                    maxWidth: 'calc(4 * 130px + 3 * 0.9rem)',
                                    overflowX: 'auto',
                                    overflowY: 'hidden',
                                    marginTop: '1rem',
                                    paddingBottom: '0.5rem',
                                    WebkitOverflowScrolling: 'touch',
                                }}
                            >
                                <div style={{
                                    display: 'flex',
                                    gap: '0.9rem',
                                    width: 'max-content',
                                }}>
                                    {similarMovies.map((similarMovie) => (
                                        <Link
                                            key={similarMovie.id}
                                            to={`/movie/${similarMovie.id}`}
                                            style={{
                                                textDecoration: 'none',
                                                color: 'inherit',
                                                flexShrink: 0,
                                                width: '130px',
                                            }}
                                        >
                                            <div className="similar-movie-card-light" style={{
                                                backgroundColor: '#ffffff',
                                                border: '1px solid #e0e0e5',
                                                borderRadius: '10px',
                                                overflow: 'hidden',
                                                transition: 'transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease',
                                                cursor: 'pointer',
                                                width: '130px',
                                                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                                            }}
                                            onMouseEnter={(e) => {
                                                e.currentTarget.style.transform = 'translateY(-4px)';
                                                e.currentTarget.style.borderColor = '#6ab4ff';
                                                e.currentTarget.style.boxShadow = '0 4px 12px rgba(106, 180, 255, 0.3)';
                                            }}
                                            onMouseLeave={(e) => {
                                                e.currentTarget.style.transform = 'translateY(0)';
                                                e.currentTarget.style.borderColor = '#e0e0e5';
                                                e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
                                            }}
                                            >
                                                {similarMovie.poster_url ? (
                                                    <img
                                                        src={similarMovie.poster_url}
                                                        alt={similarMovie.title}
                                                        style={{
                                                            width: '100%',
                                                            height: '180px',
                                                            objectFit: 'cover',
                                                        }}
                                                    />
                                                ) : (
                                                    <div style={{
                                                        width: '100%',
                                                        height: '180px',
                                                        backgroundColor: '#f5f5f7',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        justifyContent: 'center',
                                                        color: '#999',
                                                        fontSize: '0.85rem'
                                                    }}>
                                                        Нет постера
                                                    </div>
                                                )}
                                                <div style={{ padding: '0.6rem', backgroundColor: '#ffffff' }}>
                                                    <h3 style={{
                                                        fontSize: '0.85rem',
                                                        marginBottom: '0.2rem',
                                                        overflow: 'hidden',
                                                        textOverflow: 'ellipsis',
                                                        whiteSpace: 'nowrap',
                                                        color: '#111',
                                                    }}>
                                                        {similarMovie.title}
                                                    </h3>
                                                    {similarMovie.year_release && (
                                                        <p style={{ color: '#666', fontSize: '0.75rem' }}>{similarMovie.year_release}</p>
                                                    )}
                                                </div>
                                            </div>
                                        </Link>
                                    ))}
                                </div>
                            </div>
                        </>
                    )}
                </div>

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

            <div style={{marginTop: '32px', display:'grid', gridTemplateColumns:'1fr 1fr', gap:'20px'}}>
              <div className="reviews-section reviews-section-light">
                <h2 style={{color:'#111'}}>Отзывы</h2>
                {reviews.length === 0 && <p style={{color:'#555'}}>Отзывов пока нет</p>}
                <ul className="reviews-list reviews-list-light">
                  {reviews.map((rev) => (
                    <li key={rev.id} className="review-card review-card-light">
                      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', gap: '10px'}}>
                        <strong style={{color:'#111'}}>Оценка: {rev.rating}</strong>
                        {rev.created_at && <span style={{color:'#777', fontSize:'0.85rem'}}>{new Date(rev.created_at).toLocaleString()}</span>}
                      </div>
                      {rev.content && <p style={{marginTop:'8px', color:'#333'}}>{rev.content}</p>}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="reviews-section reviews-section-light">
                <h2 style={{color:'#111'}}>Оставить отзыв</h2>
                <form className="review-form" onSubmit={handleReviewSubmit}>
                    <div className="rating-row">
                        <span style={{color:'#444'}}>Ваша оценка:</span>
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
                        style={{background:'#fafafa', color:'#111', border:'1px solid #d9dbe5', borderRadius:'10px'}}
                    />
                    {!currentUser && <p style={{color:'#666', fontSize:'0.9rem'}}>Для отправки нужен вход.</p>}
                    {reviewError && <p style={{color:'red'}}>{reviewError}</p>}
                    <button type="submit" className="btn-watch-later big">Отправить</button>
                </form>
              </div>
            </div>
        </div>
    </main>
  );
};

export default MoviePage;