import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getListById, removeMoviesFromList, updateList, createReview } from '../api';

const getDirectorName = (directorData) => {
  if (!directorData || (Array.isArray(directorData) && directorData.length === 0)) return 'Неизвестен';
  if (Array.isArray(directorData)) {
    const first = directorData[0];
    return typeof first === 'string' ? first : 'Неизвестен';
  }
  if (typeof directorData === 'string') return directorData;
  return 'Неизвестен';
};

const getMainActors = (personsArray) => {
  if (!personsArray || personsArray.length === 0) return 'Актеры не указаны';
  const actorNames = personsArray.slice(0, 3).map((p) => (typeof p === 'string' ? p : null)).filter(Boolean);
  return actorNames.join(', ') || 'Актеры не указаны';
};

const calculateCombinedRating = (movie) => {
  const ratings = [];
  const kp = Number(movie.kp_rating) || 0;
  if (kp > 0) ratings.push(kp);
  const imdb = Number(movie.imdb_rating) || 0;
  if (imdb > 0) ratings.push(imdb);
  const critics = Number(movie.critics_rating) || 0;
  if (critics > 0) ratings.push(critics);
  if (ratings.length === 0) return 'N/A';
  return (ratings.reduce((a, b) => a + b, 0) / ratings.length).toFixed(1);
};

const ListDetailPage = () => {
  const { id } = useParams();
  const [list, setList] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeRatingMovie, setActiveRatingMovie] = useState(null);
  const [userRatings, setUserRatings] = useState({});
  const [editMode, setEditMode] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editDesc, setEditDesc] = useState('');
  const protectedTitles = ['буду смотреть', 'любимое', 'любимые', 'просмотренно', 'просмотрено', 'просмотренные'];

  useEffect(() => {
    setLoading(true);
    setError(null);
    getListById(id)
      .then((resp) => setList(resp.data))
      .catch((err) => setError(err.response?.data?.detail || 'Не удалось загрузить список'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <main><div className="page-container">Загрузка...</div></main>;
  if (error) return <main><div className="page-container" style={{color:'red'}}>{error}</div></main>;
  if (!list) return <main><div className="page-container">Список не найден</div></main>;

  const movies = list.movies || [];
  const isProtected = protectedTitles.includes(list.title?.toLowerCase());

  const handleRemoveMovie = async (movieId) => {
    try {
      await removeMoviesFromList(list.id, [movieId]);
      setList((prev) => ({
        ...prev,
        movies: (prev.movies || []).filter((m) => m.id !== movieId),
      }));
    } catch (e) {
      console.error('remove movie error', e);
    }
  };

  const submitQuickRating = async (movieId, rating) => {
    try {
      await createReview({ movie_id: movieId, rating, content: '' });
      setUserRatings((prev) => ({ ...prev, [movieId]: rating }));
      setActiveRatingMovie(null);
    } catch (e) {
      console.error('rating error', e);
    }
  };

  const startEdit = () => {
    setEditTitle(list.title || '');
    setEditDesc(list.description || '');
    setEditMode(true);
  };

  const saveEdit = async () => {
    try {
      const payload = { title: editTitle, description: editDesc };
      const resp = await updateList(list.id, payload);
      setList(resp.data);
      setEditMode(false);
    } catch (e) {
      console.error('update list error', e);
    }
  };

  return (
    <main>
      <div className="page-container">
        <div className="main-content top-movies">
          <div style={{display:'flex', alignItems:'center', gap:'12px', flexWrap:'wrap'}}>
            <h1>{list.title}</h1>
            {!isProtected && (
              <button
                className="icon-button"
                title="Редактировать список"
                onClick={startEdit}
              >✎</button>
            )}
          </div>
          {list.description && <p className="subtitle">{list.description}</p>}
          {!list.description && <p className="subtitle" style={{color:'#666'}}></p>}

          {editMode && (
            <div className="review-form" style={{marginTop:'12px'}}>
              <h3>Редактировать список</h3>
              <input value={editTitle} onChange={(e)=>setEditTitle(e.target.value)} placeholder="Название" />
              <textarea rows={2} value={editDesc} onChange={(e)=>setEditDesc(e.target.value)} placeholder="Описание" />
              <div style={{display:'flex', gap:'8px', flexWrap:'wrap'}}>
                <button type="button" onClick={saveEdit}>Сохранить</button>
                <button type="button" onClick={()=>setEditMode(false)} style={{background:'#dfe1e6', color:'#111'}}>Отмена</button>
              </div>
            </div>
          )}

          <div className="filters">
            <span style={{color:'#9aa0b5'}}>Фильмов: {movies.length}</span>
          </div>

          <ul className="movie-list">
            {movies.length === 0 ? (
              <p style={{ color: "#aaa", padding: "20px 0" }}>В этом списке пока нет фильмов.</p>
            ) : (
              movies.map((movie, index) => {
                const directorName = getDirectorName(movie.director);
                const actors = getMainActors(movie.persons);
                const genres = Array.isArray(movie.genres) ? movie.genres.join(', ') : (movie.genres || '—');
                const combinedRating = calculateCombinedRating(movie);

                return (
                  <li className="movie-item" key={movie.id}>
                    <span className="rank">{index + 1}</span>
                    {movie.poster_url ? (
                      <img
                        src={movie.poster_url}
                        alt={movie.title}
                        className="poster-placeholder"
                        style={{width: '60px', height: '90px', objectFit: 'cover'}}
                        onError={(e) => { e.target.onerror = null; e.target.style.display = 'none'; }}
                      />
                    ) : (
                      <div className="poster-placeholder" style={{width: '60px', height: '90px'}}></div>
                    )}
                    <div className="details">
                      <h4>
                        <Link to={`/movie/${movie.id}`}>
                          {movie.title || movie.english_title || 'Название неизвестно'}
                        </Link>
                      </h4>
                      <div className="meta">
                        {movie.year_release || 'N/A'}, {movie.movie_length ? `${movie.movie_length} мин.` : 'N/A'}
                      </div>
                      <div className="crew">
                        {genres} | Режиссер: {directorName}
                      </div>
                      <div className="cast">
                        В ролях: {actors}
                      </div>
                    </div>
                    <div className="actions" style={{display:'flex', alignItems:'center', gap:'10px', flexWrap:'nowrap'}}>
                      <div className="rating" style={{minWidth:'80px'}}>
                        <span className="rating-value">
                          {combinedRating}
                        </span>
                        <div className="votes">{movie.sum_votes ? movie.sum_votes.toLocaleString() : '0'}</div>
                      </div>
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
                          <div className="rating-popover" style={{position:'absolute', top:'28px', right:0, background:'#11141d', border:'1px solid #2a2f3f', borderRadius:'8px', padding:'6px', display:'flex', gap:'4px', zIndex:1000}}>
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
                      <button
                        className="icon-button"
                        title="Удалить из списка"
                        onClick={() => handleRemoveMovie(movie.id)}
                        style={{fontSize:'18px', padding:'4px 8px'}}
                      >
                        🗑
                      </button>
                    </div>
                  </li>
                );
              })
            )}
          </ul>
        </div>
      </div>
    </main>
  );
};

export default ListDetailPage;
