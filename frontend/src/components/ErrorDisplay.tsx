import React from 'react';
import { useLanguage } from '../i18n';

interface ErrorDisplayProps {
  error: string;
  onRetry: () => void;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, onRetry }) => {
  const { t } = useLanguage();

  return (
    <div className="error-display">
      <div className="error-icon">⚠️</div>
      <h2>{t.errorDisplay.analysisFailed}</h2>
      <p className="error-message">{error}</p>
      <button className="retry-button" onClick={onRetry}>
        {t.common.tryAgain}
      </button>
    </div>
  );
};

export default ErrorDisplay;
