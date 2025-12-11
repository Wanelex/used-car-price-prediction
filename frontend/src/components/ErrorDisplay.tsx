import React from 'react';

interface ErrorDisplayProps {
  error: string;
  onRetry: () => void;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, onRetry }) => {
  return (
    <div className="error-display">
      <div className="error-icon">⚠️</div>
      <h2>Crawl Failed</h2>
      <p className="error-message">{error}</p>
      <button className="retry-button" onClick={onRetry}>
        Try Again
      </button>
    </div>
  );
};

export default ErrorDisplay;
