import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { register, setAuthToken } from '../api';
import '../auth.css';

const RegisterPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Обработка OAuth callback
  useEffect(() => {
    const token = searchParams.get('token');
    const success = searchParams.get('success');
    const oauthError = searchParams.get('error');

    if (token && success === 'true') {
      setAuthToken(token);
      navigate('/', { replace: true });
    } else if (oauthError) {
      const errorMessages = {
        'oauth_cancelled': 'Авторизация через Yandex была отменена',
        'no_code': 'Не получен код авторизации от Yandex',
        'oauth_failed': 'Не удалось получить данные от Yandex',
        'oauth_error': 'Ошибка при авторизации через Yandex',
      };
      setError(errorMessages[oauthError] || 'Ошибка авторизации');
    }
  }, [searchParams, navigate]);

  const handleYandexLogin = () => {
    const apiUrl = import.meta.env.VITE_API_URL || '/api';
    window.location.href = `${apiUrl}/auth/yandex`;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await register({ username, email, password });
      navigate('/login');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Не удалось зарегистрироваться.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main>
      <div className="login-container">
        <h2>Регистрация</h2>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Имя пользователя</label>
            <input
              id="username"
              type="text"
              placeholder="Введите имя пользователя"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              placeholder="Введите email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Пароль</label>
            <input
              id="password"
              type="password"
              placeholder="Введите пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Повтор пароля</label>
            <input
              id="confirmPassword"
              type="password"
              placeholder="Введите пароль"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>

          <div className="form-links">
            <span>Уже есть аккаунт? <Link to="/login">Войти</Link></span>
          </div>

          {error && <p style={{ color: 'red', marginBottom: 12 }}>{error}</p>}

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Отправка...' : 'Отправить'}
          </button>
        </form>

        <div className="social-login">
          <button className="social-btn yandex" type="button" onClick={handleYandexLogin}>
            <span className="icon">Y</span>
            Продолжить с Yandex
          </button>
        </div>
      </div>
    </main>
  );
};

export default RegisterPage;
