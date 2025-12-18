import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import MoviePage from '../pages/MoviePage';

const mockedApi = vi.hoisted(() => ({
  getMovieById: vi.fn(),
  getMovieReviews: vi.fn(),
  getCurrentUser: vi.fn(),
  getUserLists: vi.fn(),
  ensureWatchlist: vi.fn(),
  getListById: vi.fn(),
  removeMoviesFromList: vi.fn(),
  addMoviesToList: vi.fn(),
  createReview: vi.fn(),
  getSimilarMovies: vi.fn(),
}));

vi.mock('../api', () => mockedApi);

describe('MoviePage', () => {
  beforeEach(() => {
    Object.values(mockedApi).forEach((fn) => fn.mockReset());
    mockedApi.getMovieById.mockResolvedValue({
      data: {
        id: 1,
        kp_id: 72811,
        title: 'Крестный отец 2',
        poster_url: '',
        year_release: 1974,
        genres: ['драма'],
        kp_rating: 9,
        imdb_rating: 9,
        critics_rating: 9,
        sum_votes: 500000,
        movie_length: 202,
        budget: '$ 13000000',
        fees_world: '$ 47000000',
        persons: ['Аль Пачино'],
        director: 'Фрэнсис Форд Коппола',
      },
    });
    mockedApi.getMovieReviews.mockResolvedValue({ data: [] });
    mockedApi.getCurrentUser.mockRejectedValue(new Error('no auth'));
    mockedApi.getUserLists.mockResolvedValue({ data: [] });
    mockedApi.ensureWatchlist.mockResolvedValue({ id: 0 });
    mockedApi.getListById.mockResolvedValue({ data: { movies: [] } });
    mockedApi.getSimilarMovies.mockResolvedValue({ data: [] });
  });

  it('renders movie title and formatted money', async () => {
    render(
      <MemoryRouter initialEntries={['/movie/1']}>
        <Routes>
          <Route path="/movie/:id" element={<MoviePage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Крестный отец 2/i)).toBeInTheDocument();
      expect(screen.getByText(/13 000 000/)).toBeInTheDocument();
      expect(screen.getByText(/47 000 000/)).toBeInTheDocument();
    });
  });
});
