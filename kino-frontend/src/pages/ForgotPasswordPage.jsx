import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { forgotPassword } from '../api';
import '../auth.css';

const ForgotPasswordPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [resetToken, setResetToken] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const { data } = await forgotPassword({ email });
      setSuccess(true);
      // В демо-версии токен возвращается в ответе
      if (data.reset_token) {
        setResetToken(data.reset_token);
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Не удалось отправить запрос на сброс пароля.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <main>
        <div className="login-container">
          <h2>Запрос отправлен</h2>
          <p style={{ marginBottom: 20, color: '#666' }}>
            Если аккаунт с таким email существует, вам будет отправлена ссылка для сброса пароля.
          </p>
          {resetToken && (
            <div style={{ 
              background: '#f5f5f5', 
              padding: '16px', 
              borderRadius: '8px', 
              marginBottom: '20px',
              wordBreak: 'break-all'
            }}>
              <p style={{ marginBottom: '8px', fontSize: '0.9rem', fontWeight: 600 }}>
                Токен для сброса пароля (для демонстрации):
              </p>
              <code style={{ fontSize: '0.85rem', color: '#333' }}>{resetToken}</code>
              <p style={{ marginTop: '12px', fontSize: '0.85rem', color: '#666' }}>
                Скопируйте этот токен и перейдите на страницу сброса пароля.
              </p>
            </div>
          )}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {resetToken && (
              <Link 
                to={`/reset-password?token=${encodeURIComponent(resetToken)}`}
                className="submit-btn"
                style={{ textAlign: 'center', textDecoration: 'none', display: 'block' }}
              >
                Перейти к сбросу пароля
              </Link>
            )}
            <Link to="/login" style={{ textAlign: 'center', color: '#666' }}>
              Вернуться к входу
            </Link>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main>
      <div className="login-container">
        <h2>Восстановление пароля</h2>
        <p style={{ marginBottom: 20, color: '#666', fontSize: '0.95rem' }}>
          Введите email, связанный с вашим аккаунтом, и мы отправим вам инструкции по восстановлению пароля.
        </p>

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

          {error && <p style={{ color: 'red', marginBottom: 12 }}>{error}</p>}

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Отправка...' : 'Отправить'}
          </button>
        </form>

        <div className="form-links" style={{ marginTop: 20 }}>
          <Link to="/login">Вернуться к входу</Link>
          <Link to="/register">Еще нет аккаунта? Регистрация</Link>
        </div>
      </div>
    </main>
  );
};

export default ForgotPasswordPage;

