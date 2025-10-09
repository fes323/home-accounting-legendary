import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { transactionsAPI, categoriesAPI, walletsAPI } from '../services/api';

const TransactionForm = ({ transaction, onSave, onCancel }) => {
  const [categories, setCategories] = useState([]);
  const [wallets, setWallets] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm({
    defaultValues: transaction || {
      t_type: 'EX',
      amount: '',
      description: '',
      date: new Date().toISOString().split('T')[0],
    },
  });

  useEffect(() => {
    const loadData = async () => {
      try {
        const [categoriesData, walletsData] = await Promise.all([
          categoriesAPI.getCategories(),
          walletsAPI.getWallets(),
        ]);
        setCategories(categoriesData);
        setWallets(walletsData);
      } catch (error) {
        console.error('Ошибка загрузки данных:', error);
      }
    };

    loadData();
  }, []);

  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      await onSave(data);
      reset();
    } catch (error) {
      console.error('Ошибка сохранения:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div className="form-group">
        <label className="label">Тип транзакции</label>
        <select
          className="select"
          {...register('t_type', { required: 'Выберите тип транзакции' })}
        >
          <option value="EX">Расход</option>
          <option value="IN">Доход</option>
        </select>
        {errors.t_type && (
          <div style={{ color: '#dc3545', fontSize: '12px', marginTop: '4px' }}>
            {errors.t_type.message}
          </div>
        )}
      </div>

      <div className="form-group">
        <label className="label">Сумма</label>
        <input
          type="number"
          step="0.01"
          className="input"
          {...register('amount', {
            required: 'Введите сумму',
            min: { value: 0.01, message: 'Сумма должна быть больше 0' },
          })}
        />
        {errors.amount && (
          <div style={{ color: '#dc3545', fontSize: '12px', marginTop: '4px' }}>
            {errors.amount.message}
          </div>
        )}
      </div>

      <div className="form-group">
        <label className="label">Описание</label>
        <input
          type="text"
          className="input"
          {...register('description')}
          placeholder="Описание транзакции"
        />
      </div>

      <div className="form-group">
        <label className="label">Дата</label>
        <input
          type="date"
          className="input"
          {...register('date', { required: 'Выберите дату' })}
        />
        {errors.date && (
          <div style={{ color: '#dc3545', fontSize: '12px', marginTop: '4px' }}>
            {errors.date.message}
          </div>
        )}
      </div>

      <div className="form-group">
        <label className="label">Категория</label>
        <select className="select" {...register('category')}>
          <option value="">Без категории</option>
          {categories.map((category) => (
            <option key={category.uuid} value={category.uuid}>
              {category.title}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label className="label">Кошелек</label>
        <select
          className="select"
          {...register('wallet', { required: 'Выберите кошелек' })}
        >
          <option value="">Выберите кошелек</option>
          {wallets.map((wallet) => (
            <option key={wallet.uuid} value={wallet.uuid}>
              {wallet.name}
            </option>
          ))}
        </select>
        {errors.wallet && (
          <div style={{ color: '#dc3545', fontSize: '12px', marginTop: '4px' }}>
            {errors.wallet.message}
          </div>
        )}
      </div>

      <div style={{ display: 'flex', gap: '12px' }}>
        <button
          type="submit"
          className="btn"
          disabled={isLoading}
        >
          {isLoading ? 'Сохранение...' : 'Сохранить'}
        </button>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={onCancel}
        >
          Отмена
        </button>
      </div>
    </form>
  );
};

export default TransactionForm;
