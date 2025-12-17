import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import HomePage from '../pages/HomePage';

const mockedApi = vi.hoisted(() => ({
  getMovies: vi.fn(),
  getCurrentUser: vi.fn(),
  ensureWatchlist: vi.fn(),
  getListById: vi.fn(),
  getUserReviews: vi.fn(),
  getUserLists: vi.fn(),
  addMoviesToList: vi.fn(),
  removeMoviesFromList: vi.fn(),
  createReview: vi.fn(),
  getMovieById: vi.fn(),
}));

vi.mock('../api', () => mockedApi);

describe('HomePage', () => {
  beforeEach(() => {
    Object.values(mockedApi).forEach((fn) => fn.mockReset());
    mockedApi.getMovies.mockResolvedValue({
      data: [
        {
          id: 1,
          title: 'Тестовый фильм',
          poster_url: '',
          year_release: 2024,
          movie_length: 120,
          genres: ['Драма'],
          director: 'Режиссер',
          persons: ['Актер'],
          kp_rating: 8,
          imdb_rating: 8,
          critics_rating: 8,
          sum_votes: 1000,
          reviews: [],
        },
      ],
    });
    mockedApi.getCurrentUser.mockRejectedValue(new Error('no auth'));
    mockedApi.getUserReviews.mockResolvedValue({ data: [] });
    mockedApi.getUserLists.mockResolvedValue({ data: [] });
    mockedApi.ensureWatchlist.mockResolvedValue({ id: 1 });
    mockedApi.getListById.mockResolvedValue({ data: { movies: [] } });
    mockedApi.addMoviesToList.mockResolvedValue({});
    mockedApi.removeMoviesFromList.mockResolvedValue({});
  });

  it('renders movie list item', async () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <HomePage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Тестовый фильм/i)).toBeInTheDocument();
    });
  });
});
