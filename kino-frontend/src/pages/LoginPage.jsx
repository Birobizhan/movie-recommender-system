import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { login, setAuthToken } from '../api';
import '../auth.css';

const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState(location.state?.message || '');

  const from = location.state?.from || '/';

  // Обработка OAuth callback
  useEffect(() => {
    const token = searchParams.get('token');
    const success = searchParams.get('success');
    const oauthError = searchParams.get('error');

    console.log('[OAuth] Callback params:', { token: token ? 'present' : 'missing', success, oauthError });

    if (token && success === 'true') {
      console.log('[OAuth] Setting auth token and redirecting');
      setAuthToken(token);
      // Полная перезагрузка страницы, чтобы Header подхватил токен
      const redirectUrl = from === '/' ? '/' : from;
      window.location.href = redirectUrl;
      return;
    } else if (oauthError) {
      const errorMessages = {
        'oauth_cancelled': 'Авторизация через Yandex была отменена',
        'no_code': 'Не получен код авторизации от Yandex',
        'oauth_failed': 'Не удалось получить данные от Yandex',
        'oauth_error': 'Ошибка при авторизации через Yandex',
      };
      setError(errorMessages[oauthError] || 'Ошибка авторизации');
      // Очищаем URL параметры
      window.history.replaceState({}, '', '/login');
    }
  }, [searchParams, navigate, from]);

  const handleYandexLogin = () => {
    const apiUrl = import.meta.env.VITE_API_URL || '/api';
    window.location.href = `${apiUrl}/auth/yandex`;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const { data } = await login({ email, password });
      setAuthToken(data.access_token);
      navigate(from, { replace: true });
    } catch (err) {
      const msg = err.response?.data?.detail || 'Не удалось войти. Проверьте email и пароль.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main>
      <div className="login-container">
        <h2>Вход в аккаунт</h2>

        <form onSubmit={handleSubmit}>
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

          <div className="form-links">
            <Link to="/forgot-password">Забыли пароль?</Link>
            <Link to="/register">Еще нет аккаунта? Регистрация</Link>
          </div>

          {successMessage && (
            <p style={{ color: '#51cf66', marginBottom: 12, padding: '10px', backgroundColor: '#1a3a1a', borderRadius: '4px' }}>
              {successMessage}
            </p>
          )}
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

export default LoginPage;
