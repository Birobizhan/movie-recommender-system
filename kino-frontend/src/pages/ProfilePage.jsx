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

  return (
    <main style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>Профиль</h1>
        
        {/* Информация о пользователе */}
        <div style={{
          backgroundColor: '#1f1f1f',
          padding: '1.5rem',
          borderRadius: '8px',
          marginBottom: '2rem',
        }}>
          <div style={{ marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{profile.username}</h2>
            <p style={{ color: '#aaa' }}>{profile.email}</p>
          </div>
          
          <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
            <div>
              <span style={{ color: '#aaa' }}>Отзывов: </span>
              <span style={{ fontWeight: 'bold' }}>{profile.reviews_count || 0}</span>
            </div>
            <div>
              <span style={{ color: '#aaa' }}>Списков: </span>
              <span style={{ fontWeight: 'bold' }}>{profile.lists_count || 0}</span>
            </div>
            {profile.average_rating && (
              <div>
                <span style={{ color: '#aaa' }}>Средняя оценка: </span>
                <span style={{ fontWeight: 'bold' }}>{profile.average_rating.toFixed(1)}</span>
              </div>
            )}
          </div>
        </div>

        {/* Любимые жанры */}
        {profile.favorite_genres && profile.favorite_genres.length > 0 && (
          <div style={{
            backgroundColor: '#1f1f1f',
            padding: '1.5rem',
            borderRadius: '8px',
            marginBottom: '2rem',
          }}>
            <h2 style={{ fontSize: '1.3rem', marginBottom: '1rem' }}>Любимые жанры</h2>
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              {profile.favorite_genres.map((item, index) => (
                <div
                  key={index}
                  style={{
                    backgroundColor: '#2b2b2e',
                    padding: '0.5rem 1rem',
                    borderRadius: '6px',
                    display: 'flex',
                    gap: '0.5rem',
                    alignItems: 'center',
                  }}
                >
                  <span style={{ fontWeight: '500' }}>{item.genre}</span>
                  <span style={{ color: '#aaa', fontSize: '0.9rem' }}>({item.count})</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Последние просмотренные фильмы */}
        {profile.recent_watched_movies && profile.recent_watched_movies.length > 0 && (
          <div style={{
            backgroundColor: '#1f1f1f',
            padding: '1.5rem',
            borderRadius: '8px',
            marginBottom: '2rem',
          }}>
            <h2 style={{ fontSize: '1.3rem', marginBottom: '1rem' }}>Последние просмотренные</h2>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
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
                    backgroundColor: '#2b2b2e',
                    borderRadius: '8px',
                    overflow: 'hidden',
                    transition: 'transform 0.2s ease',
                    cursor: 'pointer',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                  onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                  >
                    {movie.poster_url ? (
                      <img
                        src={movie.poster_url}
                        alt={movie.title}
                        style={{
                          width: '100%',
                          height: '225px',
                          objectFit: 'cover',
                        }}
                      />
                    ) : (
                      <div style={{
                        width: '100%',
                        height: '225px',
                        backgroundColor: '#333',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#aaa',
                      }}>
                        Нет постера
                      </div>
                    )}
                    <div style={{ padding: '0.75rem' }}>
                      <h3 style={{
                        fontSize: '0.9rem',
                        marginBottom: '0.25rem',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}>
                        {movie.title}
                      </h3>
                      {movie.year_release && (
                        <p style={{ color: '#aaa', fontSize: '0.8rem' }}>{movie.year_release}</p>
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
          backgroundColor: '#1f1f1f',
          padding: '1.5rem',
          borderRadius: '8px',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.3rem' }}>Смена пароля</h2>
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
                padding: '0.5rem 1rem',
                backgroundColor: showPasswordForm ? '#444' : '#2b2b2e',
                color: '#fff',
                borderRadius: '6px',
                cursor: 'pointer',
                border: '1px solid #555',
              }}
            >
              {showPasswordForm ? 'Скрыть' : 'Изменить пароль'}
            </button>
          </div>

          {showPasswordForm && (
            <form onSubmit={handlePasswordChange}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: '#aaa' }}>
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
                    backgroundColor: '#2b2b2e',
                    color: '#fff',
                    border: '1px solid #444',
                    borderRadius: '6px',
                    fontSize: '1rem',
                  }}
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: '#aaa' }}>
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
                    backgroundColor: '#2b2b2e',
                    color: '#fff',
                    border: '1px solid #444',
                    borderRadius: '6px',
                    fontSize: '1rem',
                  }}
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: '#aaa' }}>
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
                    backgroundColor: '#2b2b2e',
                    color: '#fff',
                    border: '1px solid #444',
                    borderRadius: '6px',
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
                  color: '#fff',
                  borderRadius: '6px',
                  cursor: passwordLoading ? 'not-allowed' : 'pointer',
                  opacity: passwordLoading ? 0.6 : 1,
                  fontSize: '1rem',
                  fontWeight: '500',
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

