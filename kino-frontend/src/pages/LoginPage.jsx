import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { login, setAuthToken } from '../api';
import '../auth.css';

const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const from = location.state?.from || '/';

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
            <Link to="#">Забыли пароль?</Link>
            <Link to="/register">Еще нет аккаунта? Регистрация</Link>
          </div>

          {error && <p style={{ color: 'red', marginBottom: 12 }}>{error}</p>}

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Отправка...' : 'Отправить'}
          </button>
        </form>

        <div className="social-login">
          <button className="social-btn google" type="button">
            <span className="icon">G</span>
            Продолжить с Google
          </button>
          <button className="social-btn yandex" type="button">
            <span className="icon">Y</span>
            Продолжить с Yandex
          </button>
        </div>
      </div>
    </main>
  );
};

export default LoginPage;
