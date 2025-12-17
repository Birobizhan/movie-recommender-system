import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getUserProfile, updatePassword, setAuthToken } from '../api';
import '../style.css';

const ProfilePage = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const response = await getUserProfile();
      setProfile(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate('/login');
      } else {
        setError('Не удалось загрузить профиль');
      }
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess('');

    if (passwordData.new_password !== passwordData.confirm_password) {
      setPasswordError('Новые пароли не совпадают');
      return;
    }

    if (passwordData.new_password.length < 6) {
      setPasswordError('Пароль должен содержать минимум 6 символов');
      return;
    }

    try {
      setPasswordLoading(true);
      await updatePassword({
        old_password: passwordData.old_password,
        new_password: passwordData.new_password,
      });
      setPasswordSuccess('Пароль успешно изменен. Вы будете перенаправлены на страницу входа...');
      setPasswordData({
        old_password: '',
        new_password: '',
        confirm_password: '',
      });
      // Очищаем токен и перенаправляем на страницу входа через 2 секунды
      setTimeout(() => {
        setAuthToken(null);
        navigate('/login', { 
          state: { 
            message: 'Пароль успешно изменен. Пожалуйста, войдите с новым паролем.' 
          } 
        });
      }, 2000);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Не удалось изменить пароль';
      setPasswordError(msg);
    } finally {
      setPasswordLoading(false);
    }
  };

  if (loading) {
    return (
      <main style={{ padding: '2rem', textAlign: 'center' }}>
        <p>Загрузка профиля...</p>
      </main>
    );
  }

  if (error || !profile) {
    return (
      <main style={{ padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: 'red' }}>{error || 'Профиль не найден'}</p>
      </main>
    );
  }

  const memberSince = profile.created_at ? new Date(profile.created_at).toLocaleDateString() : null;
  const watchedCount = profile.recent_watched_movies?.length || 0;
  const stats = [
    { label: 'Отзывов', value: profile.reviews_count || 0 },
    { label: 'Списков', value: profile.lists_count || 0 },
    { label: 'Средняя оценка', value: profile.average_rating ? profile.average_rating.toFixed(1) : '—' },
    { label: 'Просмотрено фильмов', value: watchedCount },
  ];

  return (
    <main style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>Профиль</h1>

        {/* Шапка профиля с метриками */}
        <div style={{
          backgroundColor: '#15151a',
          padding: '1.75rem',
          borderRadius: '14px',
          marginBottom: '2rem',
          border: '1px solid #26262f',
          display: 'grid',
          gridTemplateColumns: 'minmax(220px, 1fr) 2fr',
          gap: '16px',
          alignItems: 'center',
          flexWrap: 'wrap'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{
              width: 50,
              height: 50,
              minWidth: 50,
              minHeight: 50,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #6ab4ff, #5f8bff)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '1.6rem', fontWeight: 700, color: '#0f0f10'
            }}>
              {(profile.username || profile.email || 'U').slice(0, 1).toUpperCase()}
            </div>
            <div>
              <h2 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>{profile.username}</h2>
              <p style={{ color: '#9aa0b5', marginBottom: 4 }}>{profile.email}</p>
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '10px' }}>
            {stats.map((stat) => (
              <div key={stat.label} style={{
                background: '#1d1d24',
                border: '1px solid #2a2a33',
                borderRadius: '10px',
                padding: '12px 14px'
              }}>
                <div style={{ color: '#9aa0b5', fontSize: '0.9rem' }}>{stat.label}</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 600, marginTop: 4 }}>{stat.value}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Любимые жанры */}
        {profile.favorite_genres && profile.favorite_genres.length > 0 && (
          <div style={{
            backgroundColor: '#15151a',
            padding: '1.5rem',
            borderRadius: '12px',
            marginBottom: '2rem',
            border: '1px solid #26262f'
          }}>
            <h2 style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>Любимые жанры</h2>
            <div style={{ display: 'flex', gap: '0.8rem', flexWrap: 'wrap' }}>
              {profile.favorite_genres.map((item, index) => (
                <div
                  key={index}
                  style={{
                    background: '#1f1f27',
                    padding: '0.55rem 0.9rem',
                    borderRadius: '10px',
                    display: 'flex',
                    gap: '0.5rem',
                    alignItems: 'center',
                    border: '1px solid #2c2c36'
                  }}
                >
                  <span style={{ fontWeight: '600' }}>{item.genre}</span>
                  <span style={{ color: '#9aa0b5', fontSize: '0.9rem' }}>({item.count})</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Последние просмотренные фильмы */}
        {profile.recent_watched_movies && profile.recent_watched_movies.length > 0 && (
          <div style={{
            backgroundColor: '#15151a',
            padding: '1.5rem',
            borderRadius: '12px',
            marginBottom: '2rem',
            border: '1px solid #26262f'
          }}>
            <h2 style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>Последние просмотренные</h2>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
              gap: '1rem',
            }}>
              {profile.recent_watched_movies.map((movie) => (
                <Link
                  key={movie.id}
                  to={`/movie/${movie.id}`}
                  style={{
                    textDecoration: 'none',
                    color: 'inherit',
                  }}
                >
                  <div style={{
                    backgroundColor: '#1f1f27',
                    border: '1px solid #2c2c36',
                    borderRadius: '10px',
                    overflow: 'hidden',
                    transition: 'transform 0.2s ease, border-color 0.2s ease',
                    cursor: 'pointer',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-4px)';
                    e.currentTarget.style.borderColor = '#6ab4ff';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.borderColor = '#2c2c36';
                  }}
                  >
                    {movie.poster_url ? (
                      <img
                        src={movie.poster_url}
                        alt={movie.title}
                        style={{
                          width: '100%',
                          height: '230px',
                          objectFit: 'cover',
                        }}
                      />
                    ) : (
                      <div style={{
                        width: '100%',
                        height: '230px',
                        backgroundColor: '#2d2d35',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#aaa',
                        fontSize: '0.9rem'
                      }}>
                        Нет постера
                      </div>
                    )}
                    <div style={{ padding: '0.8rem' }}>
                      <h3 style={{
                        fontSize: '0.95rem',
                        marginBottom: '0.25rem',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}>
                        {movie.title}
                      </h3>
                      {movie.year_release && (
                        <p style={{ color: '#9aa0b5', fontSize: '0.85rem' }}>{movie.year_release}</p>
                      )}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Форма смены пароля */}
        <div style={{
          backgroundColor: '#15151a',
          padding: '1.5rem',
          borderRadius: '12px',
          border: '1px solid #26262f'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.2rem' }}>Смена пароля</h2>
            <button
              onClick={() => {
                setShowPasswordForm(!showPasswordForm);
                setPasswordError('');
                setPasswordSuccess('');
                setPasswordData({
                  old_password: '',
                  new_password: '',
                  confirm_password: '',
                });
              }}
              style={{
                padding: '0.55rem 1.1rem',
                backgroundColor: showPasswordForm ? '#2a2a33' : '#1f1f27',
                color: '#fff',
                borderRadius: '8px',
                cursor: 'pointer',
                border: '1px solid #2f2f3a',
              }}
            >
              {showPasswordForm ? 'Скрыть' : 'Изменить пароль'}
            </button>
          </div>

          {showPasswordForm && (
            <form onSubmit={handlePasswordChange}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.4rem', color: '#9aa0b5' }}>
                  Текущий пароль
                </label>
                <input
                  type="password"
                  value={passwordData.old_password}
                  onChange={(e) => setPasswordData({ ...passwordData, old_password: e.target.value })}
                  required
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    backgroundColor: '#1f1f27',
                    color: '#fff',
                    border: '1px solid #2c2c36',
                    borderRadius: '8px',
                    fontSize: '1rem',
                  }}
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.4rem', color: '#9aa0b5' }}>
                  Новый пароль
                </label>
                <input
                  type="password"
                  value={passwordData.new_password}
                  onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                  required
                  minLength={6}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    backgroundColor: '#1f1f27',
                    color: '#fff',
                    border: '1px solid #2c2c36',
                    borderRadius: '8px',
                    fontSize: '1rem',
                  }}
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.4rem', color: '#9aa0b5' }}>
                  Подтвердите новый пароль
                </label>
                <input
                  type="password"
                  value={passwordData.confirm_password}
                  onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                  required
                  minLength={6}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    backgroundColor: '#1f1f27',
                    color: '#fff',
                    border: '1px solid #2c2c36',
                    borderRadius: '8px',
                    fontSize: '1rem',
                  }}
                />
              </div>

              {passwordError && (
                <p style={{ color: '#ff6b6b', marginBottom: '1rem' }}>{passwordError}</p>
              )}

              {passwordSuccess && (
                <p style={{ color: '#51cf66', marginBottom: '1rem' }}>{passwordSuccess}</p>
              )}

              <button
                type="submit"
                disabled={passwordLoading}
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: '#6ab4ff',
                  color: '#0f0f10',
                  borderRadius: '10px',
                  cursor: passwordLoading ? 'not-allowed' : 'pointer',
                  opacity: passwordLoading ? 0.65 : 1,
                  fontSize: '1rem',
                  fontWeight: '600',
                  border: 'none'
                }}
              >
                {passwordLoading ? 'Сохранение...' : 'Сохранить'}
              </button>
            </form>
          )}
        </div>
      </div>
    </main>
  );
};

export default ProfilePage;
