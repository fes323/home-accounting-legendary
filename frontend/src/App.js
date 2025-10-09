import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { TelegramWebApp } from '@twa-dev/sdk';
import AuthContext from './contexts/AuthContext';
import TransactionsPage from './pages/TransactionsPage';
import CategoriesPage from './pages/CategoriesPage';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';
import { authAPI } from './services/api';

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Инициализация Telegram WebApp
    TelegramWebApp.ready();
    TelegramWebApp.expand();

    // Получение данных пользователя из Telegram
    const initUser = async () => {
      try {
        const tgUser = TelegramWebApp.initDataUnsafe?.user;
        const initData = TelegramWebApp.initData;
        
        if (!tgUser) {
          throw new Error('Пользователь не авторизован');
        }

        // Авторизация через backend
        const authData = {
          id: tgUser.id,
          username: tgUser.username,
          first_name: tgUser.first_name,
          last_name: tgUser.last_name,
          photo_url: tgUser.photo_url,
          auth_date: TelegramWebApp.initDataUnsafe?.auth_date,
          hash: TelegramWebApp.initDataUnsafe?.hash,
        };

        const response = await authAPI.login(authData);
        
        // Сохраняем токен
        localStorage.setItem('auth_token', response.token);
        
        setUser(response.user);
        setIsLoading(false);
      } catch (err) {
        console.error('Ошибка авторизации:', err);
        setError('Ошибка авторизации через Telegram');
        setIsLoading(false);
      }
    };

    initUser();
  }, []);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  if (!user) {
    return <ErrorMessage message="Ошибка авторизации" />;
  }

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      <Router>
        <div className="container">
          <Routes>
            <Route path="/" element={<TransactionsPage />} />
            <Route path="/categories" element={<CategoriesPage />} />
          </Routes>
        </div>
      </Router>
    </AuthContext.Provider>
  );
}

export default App;
