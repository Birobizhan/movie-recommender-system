import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header>
        <Link to="/" className="logo">КиноКлон</Link>
        <div className="search-container">
            <input type="text" placeholder="Поиск..." />
            <button>🔍</button>
        </div>
        <nav>
            <Link to="/">Фильмы</Link>
            <a href="#">Списки</a>
            <div className="profile-link logged-in">
                <span className="profile-icon"></span>
                User
            </div>
        </nav>
    </header>
  );
};

export default Header;