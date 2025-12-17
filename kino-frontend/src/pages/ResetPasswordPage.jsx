import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { resetPassword } from '../api';
import '../auth.css';

const ResetPasswordPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [token, setToken] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const tokenFromUrl = searchParams.get('token');
    if (tokenFromUrl) {
      setToken(tokenFromUrl);
    }
  }, [searchParams]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (password !== confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }

    if (password.length < 6) {
      setError('Пароль должен содержать минимум 6 символов');
      return;
    }

    if (!token) {
      setError('Токен сброса пароля не найден');
      return;
    }

    setLoading(true);
    try {
      await resetPassword({ token, new_password: password });
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Не удалось сбросить пароль. Токен может быть недействительным или истекшим.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <main>
        <div className="login-container">
          <h2>Пароль успешно изменен</h2>
          <p style={{ marginBottom: 20, color: '#666' }}>
            Ваш пароль был успешно изменен. Вы будете перенаправлены на страницу входа через несколько секунд.
          </p>
          <Link to="/login" className="submit-btn" style={{ textAlign: 'center', textDecoration: 'none', display: 'block' }}>
            Перейти к входу
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main>
      <div className="login-container">
        <h2>Установка нового пароля</h2>
        <p style={{ marginBottom: 20, color: '#666', fontSize: '0.95rem' }}>
          Введите новый пароль для вашего аккаунта.
        </p>

        <form onSubmit={handleSubmit}>
          {!token && (
            <div className="form-group">
              <label htmlFor="token">Токен сброса пароля</label>
              <input
                id="token"
                type="text"
                placeholder="Вставьте токен из письма"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                required
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="password">Новый пароль</label>
            <input
              id="password"
              type="password"
              placeholder="Введите новый пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Подтвердите пароль</label>
            <input
              id="confirmPassword"
              type="password"
              placeholder="Повторите новый пароль"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>

          {error && <p style={{ color: 'red', marginBottom: 12 }}>{error}</p>}

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Сброс пароля...' : 'Сбросить пароль'}
          </button>
        </form>

        <div className="form-links" style={{ marginTop: 20 }}>
          <Link to="/login">Вернуться к входу</Link>
          <Link to="/forgot-password">Запросить новый токен</Link>
        </div>
      </div>
    </main>
  );
};

export default ResetPasswordPage;

