import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { recommendMovies } from '../api';

const FIRST_GENRES = [
  'Драма', 'Комедия', 'Боевик (Экшен)', 'Фантастика', 'Триллер', 'Фэнтези', 
  'Мелодрама', 'Ужасы', 'Детектив', 'Приключения', 'Исторический', 'Криминал', 
  'Военный', 'Семейный', 'Биографический'
];

const THIRD_QUESTION_DICT = {
  'Комедия': {
    question: 'Выбери, что тебя смешит:',
    options: ['Романтическая', 'Чёрная комедия', 'Пародия/Мемы', 'Семейная', 'Абсурд/Сюр', 'Другое']
  },
  'Драма': {
    question: 'Какое настроение ты ищешь?',
    options: ['Грустное/Трагическое', 'Вдохновляющее', 'Философское', 'Нейтральное', 'Другое']
  },
  'Боевик (Экшен)': {
    question: 'Выбери, что тебя по душе:',
    options: ['Криминальный', 'Военный', 'Супергеройский', 'Фантастический', 'Шпионский', 'Другое']
  },
  'Фантастика': {
    question: 'Что тебя увлекает больше?',
    options: ['Космическая', 'Киберпанк', 'Постапокалипсис', 'Альтернативная реальность', 'Другое']
  },
  'Триллер': {
    question: 'Какая атмосфера цепляет?',
    options: ['Психологический', 'Технотриллер', 'Научно-фантастический', 'Постапокалиптический', 'Другое']
  },
  'Фэнтези': {
    question: 'Какой мир тебя манит?',
    options: ['Эпическое', 'Темное', 'Городское', 'Мифологическое', 'Другое']
  },
  'Мелодрама': {
    question: 'Какие эмоции важнее?',
    options: ['Романтическая страсть', 'Семейная драма', 'Историческая любовь', 'Трагический выбор', 'Другое']
  },
  'Ужасы': {
    question: 'Что пугает больше всего?',
    options: ['Психологические', 'Кровавые слэшеры', 'Оккультные', 'Другое']
  },
  'Детектив': {
    question: 'Какая загадка интереснее?',
    options: ['Классический', 'Криминальный', 'Психологический', 'Исторический', 'Другое']
  },
  'Приключения': {
    question: 'Что вдохновляет?',
    options: ['Экзотические путешествия', 'Исторические квесты', 'Поиски сокровищ', 'Экстремальное выживание', 'Другое']
  },
  'Исторический': {
    question: 'Какая тема тебе ближе?',
    options: ['Военные события', 'Эпические саги', 'Культурные драмы', 'Другое']
  },
  'Криминал': {
    question: 'Какой аспект преступного мира интересен?',
    options: ['Гангстерский', 'Полицейский', 'Финансовые махинации', 'Тюремные драмы', 'Другое']
  },
  'Военный': {
    question: 'Какой аспект войны важен?',
    options: ['Боевые действия', 'Исторические реконструкции', 'Партизанские движения', 'Личные драмы солдат', 'Другое']
  },
  'Семейный': {
    question: 'Какие темы важны?',
    options: ['Детские приключения', 'Семейные комедии', 'Истории с животными', 'Межпоколенческие драмы', 'Другое']
  },
  'Биографический': {
    question: 'Чья история вдохновляет?',
    options: ['Исторические личности', 'Творческие гении', 'Ученые и изобретатели', 'Спортивные легенды', 'Другое']
  }
};

const FOURTH_QUESTION_OPTIONS = [
  'Классика (до 2000 года)',
  'Современное кино (2000–2020)',
  'Новинки (2020–2025)',
  'Неважно, хочу сюрприз!'
];

const MovieBotPage = () => {
  const [step, setStep] = useState(1);
  const [choices, setChoices] = useState({
    mainGenre: '',
    subgenre: '',
    subgenreDetail: '',
    timePeriod: ''
  });
  const [recommendedMovies, setRecommendedMovies] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const getSecondGenres = () => {
    const genres = [...FIRST_GENRES, 'Другое'];
    return genres.filter(g => g !== choices.mainGenre);
  };

  const handleChoice1 = (genre) => {
    setChoices({ ...choices, mainGenre: genre });
    setStep(2);
  };

  const handleChoice2 = (subgenre) => {
    setChoices({ ...choices, subgenre });
    setStep(3);
  };

  const handleChoice3 = (detail) => {
    setChoices({ ...choices, subgenreDetail: detail });
    setStep(4);
  };

  const handleChoice4 = async (timePeriod) => {
    const updatedChoices = { ...choices, timePeriod };
    setChoices(updatedChoices);
    setIsLoading(true);
    setError(null);

    try {
      const response = await recommendMovies({
        main_genre: updatedChoices.mainGenre,
        subgenre: updatedChoices.subgenre,
        subgenre_detail: updatedChoices.subgenreDetail,
        time_period: timePeriod,
        limit: 20
      });
      setRecommendedMovies(response.data || []);
      setStep(5);
    } catch (err) {
      console.error('Ошибка при получении рекомендаций:', err);
      setError('Не удалось получить рекомендации. Попробуйте еще раз.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartOver = () => {
    setStep(1);
    setChoices({
      mainGenre: '',
      subgenre: '',
      subgenreDetail: '',
      timePeriod: ''
    });
    setRecommendedMovies([]);
    setError(null);
  };

  const renderStep1 = () => (
    <div className="bot-step">
      <h2>Выберите основной жанр:</h2>
      <div className="bot-options">
        {FIRST_GENRES.map(genre => (
          <button
            key={genre}
            className="bot-option-btn"
            onClick={() => handleChoice1(genre)}
          >
            {genre}
          </button>
        ))}
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="bot-step">
      <h2>Выберите поджанр:</h2>
      <div className="bot-options">
        {getSecondGenres().map(genre => (
          <button
            key={genre}
            className="bot-option-btn"
            onClick={() => handleChoice2(genre)}
          >
            {genre}
          </button>
        ))}
      </div>
    </div>
  );

  const renderStep3 = () => {
    const questionData = THIRD_QUESTION_DICT[choices.mainGenre];
    if (!questionData) return null;

    return (
      <div className="bot-step">
        <h2>{questionData.question}</h2>
        <div className="bot-options">
          {questionData.options.map(option => (
            <button
              key={option}
              className="bot-option-btn"
              onClick={() => handleChoice3(option)}
            >
              {option}
            </button>
          ))}
        </div>
      </div>
    );
  };

  const renderStep4 = () => (
    <div className="bot-step">
      <h2>Временной период:</h2>
      <div className="bot-options">
        {FOURTH_QUESTION_OPTIONS.map(option => (
          <button
            key={option}
            className="bot-option-btn"
            onClick={() => handleChoice4(option)}
            disabled={isLoading}
          >
            {option}
          </button>
        ))}
      </div>
      {isLoading && <p className="loading-text">Ищем подходящие фильмы...</p>}
    </div>
  );

  const renderStep5 = () => (
    <div className="bot-step">
      <h2>Спасибо! Вот фильмы, которые вам подойдут:</h2>
      {error && <p className="error-text">{error}</p>}
      {recommendedMovies.length > 0 ? (
        <div className="recommended-movies">
          <ul className="movie-list">
            {recommendedMovies.map((movie, index) => (
              <li key={movie.id} className="movie-item">
                <span className="rank">{index + 1}</span>
                {movie.poster_url ? (
                  <img
                    src={movie.poster_url}
                    alt={movie.title}
                    className="poster-placeholder"
                    style={{ width: '60px', height: '90px', objectFit: 'cover' }}
                    onError={(e) => { e.target.onerror = null; e.target.style.display = 'none'; }}
                  />
                ) : (
                  <div className="poster-placeholder" style={{ width: '60px', height: '90px' }}></div>
                )}
                <div className="details">
                  <h4>
                    <Link to={`/movie/${movie.id}`}>
                      {movie.title || movie.english_title || 'Название неизвестно'}
                    </Link>
                  </h4>
                  <div className="meta">
                    {movie.year_release || 'N/A'}, {movie.movie_length ? `${movie.movie_length} мин.` : 'N/A'}
                  </div>
                  <div className="crew">
                    {Array.isArray(movie.genres) ? movie.genres.join(', ') : (movie.genres || '—')}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="no-results">К сожалению, не удалось найти подходящие фильмы. Попробуйте изменить критерии поиска.</p>
      )}
      <div className="bot-actions">
        <button className="bot-option-btn" onClick={handleStartOver}>
          Начать заново
        </button>
      </div>
    </div>
  );

  return (
    <main>
      <div className="page-container">
        <div className="main-content">
          <h1>Подбор фильма</h1>
          <p className="subtitle">Ответьте на несколько вопросов, и мы подберем вам идеальный фильм!</p>
          
          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}
          {step === 4 && renderStep4()}
          {step === 5 && renderStep5()}
        </div>
      </div>
    </main>
  );
};

export default MovieBotPage;
