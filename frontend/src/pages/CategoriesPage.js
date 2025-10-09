import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Plus } from 'lucide-react';
import CategoryTree from '../components/CategoryTree';
import CategoryForm from '../components/CategoryForm';
import { categoriesAPI } from '../services/api';

const CategoriesPage = () => {
  const [categories, setCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [parentCategory, setParentCategory] = useState(null);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      setIsLoading(true);
      const data = await categoriesAPI.getCategories();
      
      // Преобразуем плоский список в дерево
      const categoryMap = new Map();
      const rootCategories = [];

      // Сначала создаем карту всех категорий
      data.forEach(category => {
        categoryMap.set(category.uuid, { ...category, children: [] });
      });

      // Затем строим дерево
      data.forEach(category => {
        const categoryNode = categoryMap.get(category.uuid);
        if (category.parent) {
          const parent = categoryMap.get(category.parent);
          if (parent) {
            parent.children.push(categoryNode);
          }
        } else {
          rootCategories.push(categoryNode);
        }
      });

      setCategories(rootCategories);
      setError(null);
    } catch (err) {
      setError('Ошибка загрузки категорий');
      console.error('Ошибка загрузки категорий:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveCategory = async (categoryData) => {
    try {
      if (editingCategory) {
        await categoriesAPI.updateCategory(editingCategory.uuid, categoryData);
      } else {
        await categoriesAPI.createCategory(categoryData);
      }
      
      setShowForm(false);
      setEditingCategory(null);
      setParentCategory(null);
      loadCategories();
    } catch (err) {
      console.error('Ошибка сохранения категории:', err);
      throw err;
    }
  };

  const handleEditCategory = (category) => {
    setEditingCategory(category);
    setParentCategory(null);
    setShowForm(true);
  };

  const handleDeleteCategory = async (categoryId) => {
    if (window.confirm('Вы уверены, что хотите удалить эту категорию? Все подкатегории также будут удалены.')) {
      try {
        await categoriesAPI.deleteCategory(categoryId);
        loadCategories();
      } catch (err) {
        console.error('Ошибка удаления категории:', err);
        setError('Ошибка удаления категории');
      }
    }
  };

  const handleAddChildCategory = (parent) => {
    setEditingCategory(null);
    setParentCategory(parent);
    setShowForm(true);
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingCategory(null);
    setParentCategory(null);
  };

  const handleAddRootCategory = () => {
    setEditingCategory(null);
    setParentCategory(null);
    setShowForm(true);
  };

  if (isLoading) {
    return (
      <div className="loading">
        <div>Загрузка категорий...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="header">
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
          <Link 
            to="/" 
            style={{ 
              marginRight: '12px', 
              color: 'var(--tg-theme-button-color, #007bff)',
              textDecoration: 'none'
            }}
          >
            <ArrowLeft size={20} />
          </Link>
          <h1>Категории</h1>
        </div>
        <p>Управление категориями транзакций</p>
      </div>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {/* Кнопка добавления корневой категории */}
      <div style={{ marginBottom: '16px' }}>
        <button
          className="btn"
          onClick={handleAddRootCategory}
        >
          <Plus size={20} style={{ marginRight: '8px' }} />
          Добавить категорию
        </button>
      </div>

      {/* Дерево категорий */}
      <div className="card">
        {categories.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '20px', color: 'var(--tg-theme-hint-color, #666)' }}>
            Нет категорий. Добавьте первую категорию.
          </div>
        ) : (
          <CategoryTree
            categories={categories}
            onEdit={handleEditCategory}
            onDelete={handleDeleteCategory}
            onAddChild={handleAddChildCategory}
          />
        )}
      </div>

      {/* Модальное окно формы */}
      {showForm && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h2 className="modal-title">
                {editingCategory 
                  ? 'Редактировать категорию' 
                  : parentCategory 
                    ? `Новая подкатегория для "${parentCategory.title}"`
                    : 'Новая категория'
                }
              </h2>
              <button className="close-btn" onClick={handleCancelForm}>
                ×
              </button>
            </div>
            <CategoryForm
              category={editingCategory}
              parentCategory={parentCategory}
              onSave={handleSaveCategory}
              onCancel={handleCancelForm}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default CategoriesPage;
