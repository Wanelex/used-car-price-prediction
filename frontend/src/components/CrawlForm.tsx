import React, { useState } from 'react';
import type { CrawlRequest } from '../api/crawlerApi';
import { useLanguage } from '../i18n';

interface CrawlFormProps {
  onSubmit: (request: CrawlRequest) => void;
  isLoading?: boolean;
}

export const CrawlForm: React.FC<CrawlFormProps> = ({ onSubmit, isLoading = false }) => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const { t } = useLanguage();

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
      setError(t.crawlForm.errors.required);
      return;
    }

    if (!validateUrl(url)) {
      setError(t.crawlForm.errors.invalid);
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
      <h1>{t.crawlForm.urlAnalyzer}</h1>
      <p className="subtitle">{t.crawlForm.enterUrl}</p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="url">{t.crawlForm.urlToAnalyze}</label>
          <input
            id="url"
            type="text"
            placeholder={t.crawlForm.placeholder}
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={isLoading}
            className="url-input"
          />
          {error && <div className="error-message">{error}</div>}
        </div>

        <button type="submit" disabled={isLoading} className="submit-button">
          {isLoading ? t.crawlForm.analyzing : t.crawlForm.startAnalysis}
        </button>
      </form>
    </div>
  );
};

export default CrawlForm;
