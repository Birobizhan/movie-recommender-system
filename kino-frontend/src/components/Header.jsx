import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { getCurrentUser, setAuthToken } from '../api';

const Header = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const [query, setQuery] = useState(params.get('q') || '');
  const [me, setMe] = useState(null);
  const [profileOpen, setProfileOpen] = useState(false);

  useEffect(() => {
    setQuery(params.get('q') || '');
  }, [location.search]);

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    if (!token) {
      setMe(null);
      return;
    }
    getCurrentUser()
      .then((resp) => setMe(resp.data))
      .catch(() => setMe(null));
  }, [location.pathname]);

  const onSearchSubmit = (e) => {
    e.preventDefault();
    const search = query.trim();
    const next = search ? `/?q=${encodeURIComponent(search)}` : '/';
    navigate(next);
  };

  const logout = () => {
    setAuthToken(null);
    setMe(null);
    navigate('/login');
  };

  return (
    <header>
      <Link to="/" className="logo">MovieHub</Link>
      <form className="search-container" onSubmit={onSearchSubmit}>
        <input
          type="text"
          placeholder="Поиск по названию"
          value={query}
          onChange={(e)=>setQuery(e.target.value)}
        />
        <button type="submit">🔍</button>
      </form>
      <nav>
        <Link to="/">Фильмы</Link>
        <Link to="/lists">Списки</Link>
        <div className="profile-link">
          {me ? (
            <div className="profile-container">
              <button className="profile-icon-btn" onClick={()=>setProfileOpen((v)=>!v)}>
                <span className="profile-icon" />
              </button>
              <span className="profile-name">{me.username || me.email}</span>
              {profileOpen && (
                <div className="profile-dropdown">
                  <button onClick={logout} className="link-button">
                    Выйти
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="auth-links">
              <Link to="/login">Войти</Link>
              <Link to="/register">Регистрация</Link>
            </div>
          )}
        </div>
      </nav>
    </header>
  );
};

export default Header;