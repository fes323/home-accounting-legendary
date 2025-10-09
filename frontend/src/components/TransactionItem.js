import React from 'react';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { Edit, Trash2 } from 'lucide-react';

const TransactionItem = ({ transaction, onEdit, onDelete }) => {
  const formatAmount = (amount, type) => {
    const formattedAmount = new Intl.NumberFormat('ru-RU', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);

    return (
      <span className={`transaction-amount ${type.toLowerCase()}`}>
        {type === 'INCOME' ? '+' : '-'}{formattedAmount}
      </span>
    );
  };

  const formatDate = (date) => {
    return format(new Date(date), 'dd.MM.yyyy', { locale: ru });
  };

  return (
    <div className="transaction-item">
      <div className="transaction-info">
        <div>{transaction.description || 'Без описания'}</div>
        <div className="transaction-date">
          {formatDate(transaction.date)}
          {transaction.category && ` • ${transaction.category.title}`}
        </div>
      </div>
      <div className="transaction-amount">
        {formatAmount(transaction.amount, transaction.t_type)}
      </div>
      <div style={{ display: 'flex', gap: '8px', marginLeft: '12px' }}>
        <button
          onClick={() => onEdit(transaction)}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: '4px',
            color: 'var(--tg-theme-hint-color, #666)',
          }}
        >
          <Edit size={16} />
        </button>
        <button
          onClick={() => onDelete(transaction.uuid)}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: '4px',
            color: '#dc3545',
          }}
        >
          <Trash2 size={16} />
        </button>
      </div>
    </div>
  );
};

export default TransactionItem;
