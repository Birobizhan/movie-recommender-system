
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getMovies } from '../api'; // Импортируем нашу функцию запроса

const HomePage = () => {
  const [movies, setMovies] = useState([]);

  useEffect(() => {
    getMovies()
      .then((response) => {
        setMovies(response.data); // Axios кладет ответ сервера в .data
      })
      .catch((error) => console.error("Ошибка:", error));
  }, []);

  return (
    <main>
      <div className="page-container">
        <div className="main-content">
          <h1>Топ фильмов</h1>
          <ul className="movie-list">
            {movies.map((movie) => (
              <li className="movie-item" key={movie.id}>
                <span className="rank">{movie.rank || movie.id}</span>
                <div className="poster-placeholder"></div>
                <div className="details">
                  {/* Ссылка на страницу фильма */}
                  <h4>
                    <Link to={`/movie/${movie.id}`}>{movie.title}</Link>
                  </h4>
                  <div className="meta">{movie.year}</div>
                  <div className="crew">{movie.director}</div>
                </div>
                <div className="rating">
                    <span className="rating-value">{movie.rating}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </main>
  );
};

export default HomePage;