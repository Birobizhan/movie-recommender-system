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
    getCurrentUser()
      .then((resp) => setMe(resp.data))
      .catch(() => setMe(null));
  }, []);

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
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', position:'relative' }}>
                  <button className="profile-icon-btn" onClick={()=>setProfileOpen((v)=>!v)}>
                    <span className="profile-icon" />
                  </button>
                  <span className="profile-name">{me.username || me.email}</span>
                  {profileOpen && (
                    <div className="profile-dropdown" style={{minWidth:'160px'}}>
                      <button onClick={logout} className="link-button" style={{width:'100%', color:'#fff', fontSize:'15px', padding:'10px 12px', textAlign:'left'}}>
                        Выйти
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div style={{display: 'flex', gap: '12px'}}>
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