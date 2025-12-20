import React, { useState } from 'react';
import type { CrawlRequest } from '../api/crawlerApi';

interface CrawlFormProps {
  onSubmit: (request: CrawlRequest) => void;
  isLoading?: boolean;
}

export const CrawlForm: React.FC<CrawlFormProps> = ({ onSubmit, isLoading = false }) => {
  const [url, setUrl] = useState('');
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
      use_stealth: true,
      solve_captcha: true,
      max_retries: 3,
      wait_time: 0,
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

        <button type="submit" disabled={isLoading} className="submit-button">
          {isLoading ? 'Crawling...' : 'Start Crawl'}
        </button>
      </form>
    </div>
  );
};

export default CrawlForm;
