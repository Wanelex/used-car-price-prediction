import React, { useState } from 'react';
import type { CrawlResult } from '../api/crawlerApi';

interface ResultDisplayProps {
  result: CrawlResult;
  onNewCrawl: () => void;
}

export const ResultDisplay: React.FC<ResultDisplayProps> = ({ result, onNewCrawl }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'text' | 'html' | 'metadata' | 'images' | 'links'>('overview');
  const [showMoreText, setShowMoreText] = useState(false);

  const crawlData = result.result;

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  const truncateText = (text: string, maxLength: number = 500): string => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const formatTime = (seconds?: number): string => {
    if (!seconds) return 'N/A';
    return `${seconds.toFixed(2)}s`;
  };

  return (
    <div className="result-display">
      <div className="result-header">
        <h2>Crawl Results</h2>
        <button className="new-crawl-button" onClick={onNewCrawl}>
          Start New Crawl
        </button>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab ${activeTab === 'text' ? 'active' : ''}`}
          onClick={() => setActiveTab('text')}
        >
          Text Content
        </button>
        <button
          className={`tab ${activeTab === 'html' ? 'active' : ''}`}
          onClick={() => setActiveTab('html')}
        >
          HTML
        </button>
        <button
          className={`tab ${activeTab === 'metadata' ? 'active' : ''}`}
          onClick={() => setActiveTab('metadata')}
        >
          Metadata
        </button>
        <button
          className={`tab ${activeTab === 'images' ? 'active' : ''}`}
          onClick={() => setActiveTab('images')}
        >
          Images ({crawlData?.images?.length || 0})
        </button>
        <button
          className={`tab ${activeTab === 'links' ? 'active' : ''}`}
          onClick={() => setActiveTab('links')}
        >
          Links ({crawlData?.links?.length || 0})
        </button>
      </div>

      <div className="tab-content">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="overview-section">
            <div className="info-grid">
              <div className="info-item">
                <label>URL</label>
                <p className="url-value" title={crawlData?.final_url || result.url}>
                  {crawlData?.final_url || result.url}
                </p>
              </div>
              <div className="info-item">
                <label>Title</label>
                <p>{crawlData?.title || 'No title found'}</p>
              </div>
              <div className="info-item">
                <label>Crawl Duration</label>
                <p>{formatTime(crawlData?.crawl_duration)}</p>
              </div>
              <div className="info-item">
                <label>Method</label>
                <p>{crawlData?.method || 'N/A'}</p>
              </div>
              <div className="info-item">
                <label>CAPTCHA Solved</label>
                <p>{crawlData?.captcha_solved ? '✓ Yes' : '✗ No'}</p>
              </div>
              <div className="info-item">
                <label>Response Time</label>
                <p>{crawlData?.response_time ? `${crawlData.response_time.toFixed(2)}s` : 'N/A'}</p>
              </div>
            </div>
          </div>
        )}

        {/* Text Content Tab */}
        {activeTab === 'text' && (
          <div className="text-section">
            <div className="content-box">
              <p>
                {showMoreText || !crawlData?.text
                  ? crawlData?.text || 'No text content found'
                  : truncateText(crawlData.text)}
              </p>
              {crawlData?.text && crawlData.text.length > 500 && (
                <button
                  className="show-more-button"
                  onClick={() => setShowMoreText(!showMoreText)}
                >
                  {showMoreText ? 'Show Less' : 'Show More'}
                </button>
              )}
            </div>
          </div>
        )}

        {/* HTML Tab */}
        {activeTab === 'html' && (
          <div className="html-section">
            <button
              className="copy-button"
              onClick={() => copyToClipboard(crawlData?.html || '')}
            >
              Copy HTML
            </button>
            <pre className="html-content">
              <code>{truncateText(crawlData?.html || 'No HTML found', 2000)}</code>
            </pre>
          </div>
        )}

        {/* Metadata Tab */}
        {activeTab === 'metadata' && (
          <div className="metadata-section">
            {crawlData?.metadata ? (
              <div className="metadata-grid">
                {Object.entries(crawlData.metadata).map(([key, value]) =>
                  value ? (
                    <div key={key} className="metadata-item">
                      <label>{key}</label>
                      <p>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</p>
                    </div>
                  ) : null
                )}
              </div>
            ) : (
              <p>No metadata found</p>
            )}
          </div>
        )}

        {/* Images Tab */}
        {activeTab === 'images' && (
          <div className="images-section">
            {crawlData?.images && crawlData.images.length > 0 ? (
              <div className="images-grid">
                {crawlData.images.slice(0, 12).map((img, idx) => (
                  <div key={idx} className="image-item">
                    <img src={img} alt={`Image ${idx}`} onError={(e) => (e.currentTarget.style.display = 'none')} />
                    <p className="image-url" title={img}>
                      {img.length > 50 ? img.substring(0, 50) + '...' : img}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p>No images found</p>
            )}
            {crawlData?.images && crawlData.images.length > 12 && (
              <p className="image-count">And {crawlData.images.length - 12} more images...</p>
            )}
          </div>
        )}

        {/* Links Tab */}
        {activeTab === 'links' && (
          <div className="links-section">
            {crawlData?.links && crawlData.links.length > 0 ? (
              <>
                <p className="links-count">Found {crawlData.links.length} links</p>
                <ul className="links-list">
                  {crawlData.links.slice(0, 20).map((link, idx) => (
                    <li key={idx}>
                      <a href={link} target="_blank" rel="noopener noreferrer" title={link}>
                        {link.length > 80 ? link.substring(0, 80) + '...' : link}
                      </a>
                    </li>
                  ))}
                </ul>
                {crawlData.links.length > 20 && (
                  <p className="links-more">And {crawlData.links.length - 20} more links...</p>
                )}
              </>
            ) : (
              <p>No links found</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultDisplay;
