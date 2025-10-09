import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Filter, Calendar } from 'lucide-react';
import TransactionItem from '../components/TransactionItem';
import TransactionForm from '../components/TransactionForm';
import { transactionsAPI } from '../services/api';
import AuthContext from '../contexts/AuthContext';

const TransactionsPage = () => {
  const { user } = React.useContext(AuthContext);
  const [transactions, setTransactions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState(null);
  const [filter, setFilter] = useState('all'); // all, income, expense
  const [dateFilter, setDateFilter] = useState('');

  useEffect(() => {
    loadTransactions();
  }, [filter, dateFilter]);

  const loadTransactions = async () => {
    try {
      setIsLoading(true);
      const params = {};
      
      if (filter !== 'all') {
        params.t_type = filter === 'income' ? 'IN' : 'EX';
      }
      
      if (dateFilter) {
        params.date = dateFilter;
      }

      const data = await transactionsAPI.getTransactions(params);
      setTransactions(data.results || data);
      setError(null);
    } catch (err) {
      setError('Ошибка загрузки транзакций');
      console.error('Ошибка загрузки транзакций:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveTransaction = async (transactionData) => {
    try {
      if (editingTransaction) {
        await transactionsAPI.updateTransaction(editingTransaction.uuid, transactionData);
      } else {
        await transactionsAPI.createTransaction(transactionData);
      }
      
      setShowForm(false);
      setEditingTransaction(null);
      loadTransactions();
    } catch (err) {
      console.error('Ошибка сохранения транзакции:', err);
      throw err;
    }
  };

  const handleEditTransaction = (transaction) => {
    setEditingTransaction(transaction);
    setShowForm(true);
  };

  const handleDeleteTransaction = async (transactionId) => {
    if (window.confirm('Вы уверены, что хотите удалить эту транзакцию?')) {
      try {
        await transactionsAPI.deleteTransaction(transactionId);
        loadTransactions();
      } catch (err) {
        console.error('Ошибка удаления транзакции:', err);
        setError('Ошибка удаления транзакции');
      }
    }
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingTransaction(null);
  };

  const formatAmount = (amount, type) => {
    return new Intl.NumberFormat('ru-RU', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  const calculateTotal = (type) => {
    return transactions
      .filter(t => t.t_type === type)
      .reduce((sum, t) => sum + parseFloat(t.amount), 0);
  };

  const totalIncome = calculateTotal('IN');
  const totalExpense = calculateTotal('EX');
  const balance = totalIncome - totalExpense;

  if (isLoading) {
    return (
      <div className="loading">
        <div>Загрузка транзакций...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="header">
        <h1>Транзакции</h1>
        <p>Управление доходами и расходами</p>
      </div>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {/* Статистика */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#28a745' }}>
              +{formatAmount(totalIncome)}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color, #666)' }}>
              Доходы
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#dc3545' }}>
              -{formatAmount(totalExpense)}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color, #666)' }}>
              Расходы
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ 
              fontSize: '18px', 
              fontWeight: 'bold', 
              color: balance >= 0 ? '#28a745' : '#dc3545'
            }}>
              {balance >= 0 ? '+' : ''}{formatAmount(balance)}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color, #666)' }}>
              Баланс
            </div>
          </div>
        </div>
      </div>

      {/* Фильтры */}
      <div className="card">
        <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
          <select
            className="select"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            style={{ flex: 1 }}
          >
            <option value="all">Все транзакции</option>
            <option value="income">Только доходы</option>
            <option value="expense">Только расходы</option>
          </select>
          <input
            type="date"
            className="input"
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            style={{ flex: 1 }}
          />
        </div>
      </div>

      {/* Кнопки действий */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
        <button
          className="btn"
          onClick={() => setShowForm(true)}
        >
          <Plus size={20} style={{ marginRight: '8px' }} />
          Добавить транзакцию
        </button>
        <Link to="/categories" className="btn btn-secondary" style={{ textDecoration: 'none' }}>
          Управление категориями
        </Link>
      </div>

      {/* Список транзакций */}
      <div className="card">
        {transactions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '20px', color: 'var(--tg-theme-hint-color, #666)' }}>
            Нет транзакций
          </div>
        ) : (
          transactions.map((transaction) => (
            <TransactionItem
              key={transaction.uuid}
              transaction={transaction}
              onEdit={handleEditTransaction}
              onDelete={handleDeleteTransaction}
            />
          ))
        )}
      </div>

      {/* Модальное окно формы */}
      {showForm && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h2 className="modal-title">
                {editingTransaction ? 'Редактировать транзакцию' : 'Новая транзакция'}
              </h2>
              <button className="close-btn" onClick={handleCancelForm}>
                ×
              </button>
            </div>
            <TransactionForm
              transaction={editingTransaction}
              onSave={handleSaveTransaction}
              onCancel={handleCancelForm}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default TransactionsPage;
