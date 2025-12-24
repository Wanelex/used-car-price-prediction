import React from 'react';
import { useLanguage } from '../i18n';

interface LoadingStateProps {
  url: string;
  statusMessage: string;
  elapsedSeconds: number;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  url,
  statusMessage,
  elapsedSeconds,
}) => {
  const { t } = useLanguage();

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="loading-state">
      <div className="spinner"></div>
      <h2>{t.loadingState.analysisInProgress}</h2>

      <div className="crawl-url">
        <p className="url-label">{t.loadingState.analyzing}</p>
        <p className="url-text" title={url}>
          {url}
        </p>
      </div>

      <div className="status-info">
        <p className="status-message">{statusMessage}</p>
        <p className="elapsed-time">{t.loadingState.elapsed.replace('{time}', formatTime(elapsedSeconds))}</p>
      </div>

      <div className="loading-tips">
        <p>{t.loadingState.tip}</p>
      </div>
    </div>
  );
};

export default LoadingState;
