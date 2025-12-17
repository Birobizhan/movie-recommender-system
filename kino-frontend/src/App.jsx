import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import MoviePage from './pages/MoviePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import ProfilePage from './pages/ProfilePage';
import ListsPage from './pages/ListsPage';
import ListDetailPage from './pages/ListDetailPage';
import MovieBotPage from './pages/MovieBotPage';
import './style.css'; // Не забудь положить сюда файл style.css из предыдущего ответа

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="movie/:id" element={<MoviePage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
          <Route path="forgot-password" element={<ForgotPasswordPage />} />
          <Route path="reset-password" element={<ResetPasswordPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="lists" element={<ListsPage />} />
          <Route path="lists/:id" element={<ListDetailPage />} />
          <Route path="movie-bot" element={<MovieBotPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;