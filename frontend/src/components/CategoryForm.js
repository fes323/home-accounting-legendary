import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { categoriesAPI } from '../services/api';

const CategoryForm = ({ category, parentCategory, onSave, onCancel }) => {
  const [categories, setCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm({
    defaultValues: category || {
      title: '',
      description: '',
      parent: parentCategory?.uuid || '',
    },
  });

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const categoriesData = await categoriesAPI.getCategories();
        setCategories(categoriesData);
      } catch (error) {
        console.error('Ошибка загрузки категорий:', error);
      }
    };

    loadCategories();
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
        <label className="label">Название категории</label>
        <input
          type="text"
          className="input"
          {...register('title', { required: 'Введите название категории' })}
          placeholder="Название категории"
        />
        {errors.title && (
          <div style={{ color: '#dc3545', fontSize: '12px', marginTop: '4px' }}>
            {errors.title.message}
          </div>
        )}
      </div>

      <div className="form-group">
        <label className="label">Описание</label>
        <input
          type="text"
          className="input"
          {...register('description')}
          placeholder="Описание категории"
        />
      </div>

      {!parentCategory && (
        <div className="form-group">
          <label className="label">Родительская категория</label>
          <select className="select" {...register('parent')}>
            <option value="">Корневая категория</option>
            {categories
              .filter((cat) => !cat.parent)
              .map((cat) => (
                <option key={cat.uuid} value={cat.uuid}>
                  {cat.title}
                </option>
              ))}
          </select>
        </div>
      )}

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

export default CategoryForm;
