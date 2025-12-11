import axios from 'axios';

// Создаем базовую настройку
const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api', // Адрес твоего FastAPI
});

// Подхватываем токен, если уже лежит в localStorage
const storedToken = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
if (storedToken) {
    api.defaults.headers.common.Authorization = `Bearer ${storedToken}`;
}

// Функция для получения всех фильмов (с фильтрами/поиском/сортировкой)
export const getMovies = (params = {}) => api.get('/movies/top', { params });

// Функция для получения одного фильма по ID
export const getMovieById = (id) => api.get(`/movies/${id}/`);

// Поиск
export const searchMovies = (query) => api.get('/movies', { params: { q: query } });

// Аутентификация
export const login = (credentials) => api.post('/users/login', credentials);
export const register = (payload) => api.post('/users/register', payload);
export const getCurrentUser = () => api.get('/users/me');

// Отзывы
export const getMovieReviews = (movieId) => api.get(`/reviews/movie/${movieId}`);
export const createReview = (payload) => api.post('/reviews/', payload);
export const deleteReview = (reviewId) => api.delete(`/reviews/${reviewId}`);
export const updateReview = (reviewId, payload) => api.put(`/reviews/${reviewId}`, payload);

// Списки
export const getUserLists = (userId) => api.get(`/lists/user/${userId}`);
export const getListById = (listId) => api.get(`/lists/${listId}`);
export const createList = (payload) => api.post('/lists/', payload);
export const addMoviesToList = (listId, movieIds) =>
    api.post(`/lists/${listId}/movies`, { movie_ids: movieIds });
export const removeMoviesFromList = (listId, movieIds) =>
    api.delete(`/lists/${listId}/movies`, { data: { movie_ids: movieIds } });

// Watchlist helper
export const ensureWatchlist = async (userId) => {
    const listsResp = await getUserLists(userId);
    const existing = (listsResp.data || []).find((l) => l.title === 'Буду смотреть');
    if (existing) return existing;
    const created = await createList({ title: 'Буду смотреть', description: 'Отложенные фильмы' });
    return created.data;
};

// Утилита для обновления заголовка при логине
export const setAuthToken = (token) => {
    if (token) {
        localStorage.setItem('access_token', token);
        api.defaults.headers.common.Authorization = `Bearer ${token}`;
    } else {
        localStorage.removeItem('access_token');
        delete api.defaults.headers.common.Authorization;
    }
};

export default api;