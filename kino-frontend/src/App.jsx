import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import MoviePage from './pages/MoviePage';
import './style.css'; // Не забудь положить сюда файл style.css из предыдущего ответа

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="movie/:id" element={<MoviePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;