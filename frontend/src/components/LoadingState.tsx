import React from 'react';

interface LoadingStateProps {
  url: string;
  progress: number;
  statusMessage: string;
  elapsedSeconds: number;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  url,
  progress,
  statusMessage,
  elapsedSeconds,
}) => {
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="loading-state">
      <div className="spinner"></div>
      <h2>Crawling in Progress</h2>

      <div className="crawl-url">
        <p className="url-label">Crawling:</p>
        <p className="url-text" title={url}>
          {url}
        </p>
      </div>

      <div className="progress-container">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }}></div>
        </div>
        <p className="progress-text">{Math.round(progress)}%</p>
      </div>

      <div className="status-info">
        <p className="status-message">{statusMessage}</p>
        <p className="elapsed-time">Elapsed: {formatTime(elapsedSeconds)}</p>
      </div>

      <div className="loading-tips">
        <p>This may take a few seconds depending on the website...</p>
      </div>
    </div>
  );
};

export default LoadingState;
