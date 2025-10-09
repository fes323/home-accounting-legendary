import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Добавление токена авторизации к запросам
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Обработка ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  // Авторизация через Telegram
  login: async (telegramData) => {
    const response = await api.post('/auth/telegram/', telegramData);
    return response.data;
  },
};

export const transactionsAPI = {
  // Получение списка транзакций
  getTransactions: async (params = {}) => {
    const response = await api.get('/transactions/', { params });
    return response.data;
  },

  // Создание новой транзакции
  createTransaction: async (transactionData) => {
    const response = await api.post('/transactions/', transactionData);
    return response.data;
  },

  // Обновление транзакции
  updateTransaction: async (id, transactionData) => {
    const response = await api.put(`/transactions/${id}/`, transactionData);
    return response.data;
  },

  // Удаление транзакции
  deleteTransaction: async (id) => {
    const response = await api.delete(`/transactions/${id}/`);
    return response.data;
  },
};

export const categoriesAPI = {
  // Получение списка категорий
  getCategories: async () => {
    const response = await api.get('/categories/');
    return response.data;
  },

  // Создание новой категории
  createCategory: async (categoryData) => {
    const response = await api.post('/categories/', categoryData);
    return response.data;
  },

  // Обновление категории
  updateCategory: async (id, categoryData) => {
    const response = await api.put(`/categories/${id}/`, categoryData);
    return response.data;
  },

  // Удаление категории
  deleteCategory: async (id) => {
    const response = await api.delete(`/categories/${id}/`);
    return response.data;
  },
};

export const walletsAPI = {
  // Получение списка кошельков
  getWallets: async () => {
    const response = await api.get('/wallets/');
    return response.data;
  },
};

export default api;
