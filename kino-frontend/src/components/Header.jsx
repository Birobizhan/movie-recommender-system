import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';

const Header = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const [query, setQuery] = useState(params.get('q') || '');

  useEffect(() => {
    setQuery(params.get('q') || '');
  }, [location.search]);

  const onSearchSubmit = (e) => {
    e.preventDefault();
    const search = query.trim();
    const next = search ? `/?q=${encodeURIComponent(search)}` : '/';
    navigate(next);
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
                <span className="profile-icon"></span>
                <div style={{display: 'flex', gap: '12px'}}>
                    <Link to="/login">Войти</Link>
                    <Link to="/register">Регистрация</Link>
                </div>
            </div>
        </nav>
    </header>
  );
};

export default Header;