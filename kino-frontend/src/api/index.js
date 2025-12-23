import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
    baseURL,
});

const storedToken = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
if (storedToken) {
    api.defaults.headers.common.Authorization = `Bearer ${storedToken}`;
}

export const getMovies = (params = {}) => api.get('/movies', { params });

export const getMovieById = (id) => api.get(`/movies/${id}/`);

export const getSimilarMovies = (movieId, limit = 10) => api.get(`/movies/${movieId}/similar`, { params: { limit } });

export const login = (credentials) => api.post('/users/login', credentials);

export const register = (payload) => api.post('/users/register', payload);

export const getCurrentUser = () => api.get('/users/me');

export const getUserProfile = () => api.get('/users/me/profile');

export const updatePassword = (payload) => api.put('/users/me/password', payload);

export const forgotPassword = (payload) => api.post('/users/forgot-password', payload);

export const resetPassword = (payload) => api.post('/users/reset-password', payload);

export const getMovieReviews = (movieId) => api.get(`/reviews/movie/${movieId}`);

export const createReview = (payload) => api.post('/reviews/', payload);

export const deleteReview = (reviewId) => api.delete(`/reviews/${reviewId}`);

export const updateReview = (reviewId, payload) => api.put(`/reviews/${reviewId}`, payload);

export const getUserReviews = (userId) => api.get(`/reviews/user/${userId}`);

export const getUserLists = (userId) => api.get(`/lists/user/${userId}`);

export const getListById = (listId) => api.get(`/lists/${listId}`);

export const createList = (payload) => api.post('/lists/', payload);

export const addMoviesToList = (listId, movieIds) =>
    api.post(`/lists/${listId}/movies`, { movie_ids: movieIds });

export const removeMoviesFromList = (listId, movieIds) =>
    api.delete(`/lists/${listId}/movies`, { data: { movie_ids: movieIds } });

export const updateList = (listId, payload) => api.put(`/lists/${listId}`, payload);

export const deleteList = (listId) => api.delete(`/lists/${listId}`);

export const ensureWatchlist = async (userId) => {
    const listsResp = await getUserLists(userId);
    
    const existing = (listsResp.data || []).find((l) => l.title === 'Буду смотреть');
    
    if (existing) return existing;
        const created = await createList({ title: 'Буду смотреть', description: 'Отложенные фильмы' });
    return created.data;
};

export const setAuthToken = (token) => {
    if (token) {
        // Сохраняем токен в localStorage (хранилище браузера)
        localStorage.setItem('access_token', token);
        
        api.defaults.headers.common.Authorization = `Bearer ${token}`;
    } else {
        // Удаляем токен из localStorage
        localStorage.removeItem('access_token');
        
        // Удаляем токен из заголовков axios
        delete api.defaults.headers.common.Authorization;
    }
};

export const recommendMovies = (payload) => api.post('/movies/recommend', payload);
export default api;