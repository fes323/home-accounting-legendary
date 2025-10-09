import React from 'react';

const ErrorMessage = ({ message }) => {
  return (
    <div className="error">
      <strong>Ошибка:</strong> {message}
    </div>
  );
};

export default ErrorMessage;
