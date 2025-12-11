import React, { useState } from 'react';
import type { CrawlRequest } from '../api/crawlerApi';

interface CrawlFormProps {
  onSubmit: (request: CrawlRequest) => void;
  isLoading?: boolean;
}

export const CrawlForm: React.FC<CrawlFormProps> = ({ onSubmit, isLoading = false }) => {
  const [url, setUrl] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [useStealth, setUseStealth] = useState(true);
  const [solveCaptcha, setSolveCaptcha] = useState(true);
  const [maxRetries, setMaxRetries] = useState(3);
  const [waitTime, setWaitTime] = useState(0);
  const [error, setError] = useState('');

  const validateUrl = (urlString: string): boolean => {
    try {
      new URL(urlString);
      return true;
    } catch {
      return false;
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!url.trim()) {
      setError('URL is required');
      return;
    }

    if (!validateUrl(url)) {
      setError('Invalid URL. Please enter a valid URL starting with http:// or https://');
      return;
    }

    const request: CrawlRequest = {
      url: url.trim(),
      use_stealth: useStealth,
      solve_captcha: solveCaptcha,
      max_retries: maxRetries,
      wait_time: waitTime,
      extract_images: true,
      extract_links: true,
    };

    onSubmit(request);
  };

  return (
    <div className="crawl-form">
      <h1>Web Crawler</h1>
      <p className="subtitle">Enter a URL to crawl and extract its content</p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="url">URL to Crawl</label>
          <input
            id="url"
            type="text"
            placeholder="https://example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={isLoading}
            className="url-input"
          />
          {error && <div className="error-message">{error}</div>}
        </div>

        <button
          type="button"
          className="toggle-advanced"
          onClick={() => setShowAdvanced(!showAdvanced)}
          disabled={isLoading}
        >
          {showAdvanced ? '▼ Hide Advanced Settings' : '▶ Show Advanced Settings'}
        </button>

        {showAdvanced && (
          <div className="advanced-settings">
            <div className="form-group checkbox">
              <input
                id="stealth"
                type="checkbox"
                checked={useStealth}
                onChange={(e) => setUseStealth(e.target.checked)}
                disabled={isLoading}
              />
              <label htmlFor="stealth">Stealth Mode</label>
              <span className="help-text">Avoid detection by websites</span>
            </div>

            <div className="form-group checkbox">
              <input
                id="captcha"
                type="checkbox"
                checked={solveCaptcha}
                onChange={(e) => setSolveCaptcha(e.target.checked)}
                disabled={isLoading}
              />
              <label htmlFor="captcha">Solve CAPTCHA</label>
              <span className="help-text">Auto-solve CAPTCHA challenges</span>
            </div>

            <div className="form-group">
              <label htmlFor="retries">Max Retries: {maxRetries}</label>
              <input
                id="retries"
                type="range"
                min="0"
                max="10"
                value={maxRetries}
                onChange={(e) => setMaxRetries(parseInt(e.target.value))}
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="waitTime">Wait Time after Load: {waitTime}s</label>
              <input
                id="waitTime"
                type="range"
                min="0"
                max="30"
                value={waitTime}
                onChange={(e) => setWaitTime(parseInt(e.target.value))}
                disabled={isLoading}
              />
            </div>
          </div>
        )}

        <button type="submit" disabled={isLoading} className="submit-button">
          {isLoading ? 'Crawling...' : 'Start Crawl'}
        </button>
      </form>
    </div>
  );
};

export default CrawlForm;
