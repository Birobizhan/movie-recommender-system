import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMovieById } from '../api';

const MoviePage = () => {
  const { id } = useParams(); // Берем ID из URL
  const [movie, setMovie] = useState(null);

  useEffect(() => {
    getMovieById(id)
      .then((response) => setMovie(response.data))
      .catch((error) => console.error("Ошибка:", error));
  }, [id]);

  if (!movie) return <div style={{color: "white", padding: 20}}>Загрузка...</div>;

  return (
    <main>
        <div className="page-container">
            <Link to="/" style={{color: "#888", marginBottom: "20px", display: "block"}}>← Назад к списку</Link>
            
            <div style={{display: "flex", gap: "30px"}}>
                <div style={{width: "300px", height: "450px", background: "#333", borderRadius: "10px"}}></div>
                <div>
                    <h1 style={{fontSize: "3rem"}}>{movie.title}</h1>
                    <p style={{fontSize: "1.2rem", color: "#ccc", margin: "10px 0"}}>{movie.year}</p>
                    <div style={{background: "#2e7d32", display: "inline-block", padding: "5px 10px", borderRadius: "5px", fontWeight: "bold"}}>
                        {movie.rating}
                    </div>
                    <p style={{marginTop: "20px", lineHeight: "1.6", color: "#ddd"}}>
                        {movie.description || "Описание фильма отсутствует..."}
                    </p>
                </div>
            </div>
        </div>
    </main>
  );
};

export default MoviePage;