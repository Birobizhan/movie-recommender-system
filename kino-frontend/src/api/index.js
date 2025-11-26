import axios from 'axios';

// Создаем базовую настройку
const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api', // Адрес твоего FastAPI
});

// Функция для получения всех фильмов
export const getMovies = () => api.get('/movies/');

// Функция для получения одного фильма по ID
export const getMovieById = (id) => api.get(`/movies/${id}/`);

export default api;