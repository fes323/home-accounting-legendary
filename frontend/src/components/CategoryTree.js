import React, { useState } from 'react';
import { ChevronRight, ChevronDown, Edit, Trash2, Plus } from 'lucide-react';

const CategoryTree = ({ categories, onEdit, onDelete, onAddChild }) => {
  const [expandedNodes, setExpandedNodes] = useState(new Set());

  const toggleExpanded = (nodeId) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
  };

  const renderCategory = (category, level = 0) => {
    const hasChildren = category.children && category.children.length > 0;
    const isExpanded = expandedNodes.has(category.uuid);

    return (
      <div key={category.uuid}>
        <div
          className="category-item"
          style={{ paddingLeft: `${level * 16}px` }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
              {hasChildren ? (
                <button
                  onClick={() => toggleExpanded(category.uuid)}
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    padding: '4px',
                    marginRight: '8px',
                    color: 'var(--tg-theme-hint-color, #666)',
                  }}
                >
                  {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                </button>
              ) : (
                <div style={{ width: '24px' }} />
              )}
              <span>{category.title}</span>
              {category.description && (
                <span style={{ 
                  fontSize: '12px', 
                  color: 'var(--tg-theme-hint-color, #666)',
                  marginLeft: '8px'
                }}>
                  ({category.description})
                </span>
              )}
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={() => onAddChild(category)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '4px',
                  color: 'var(--tg-theme-button-color, #007bff)',
                }}
                title="Добавить подкатегорию"
              >
                <Plus size={16} />
              </button>
              <button
                onClick={() => onEdit(category)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '4px',
                  color: 'var(--tg-theme-hint-color, #666)',
                }}
                title="Редактировать"
              >
                <Edit size={16} />
              </button>
              <button
                onClick={() => onDelete(category.uuid)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '4px',
                  color: '#dc3545',
                }}
                title="Удалить"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        </div>
        {hasChildren && isExpanded && (
          <div className="category-tree">
            {category.children.map((child) => renderCategory(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  // Сортировка категорий по уровню вложенности
  const sortedCategories = categories.sort((a, b) => {
    if (a.parent === null && b.parent === null) {
      return a.title.localeCompare(b.title);
    }
    if (a.parent === null) return -1;
    if (b.parent === null) return 1;
    return 0;
  });

  return (
    <div>
      {sortedCategories.map((category) => renderCategory(category))}
    </div>
  );
};

export default CategoryTree;
