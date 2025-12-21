import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';

import { useCrawler } from './hooks/useCrawler';
import type { CrawlRequest } from './api/crawlerApi';

import CrawlForm from './components/CrawlForm';
import LoadingState from './components/LoadingState';
import ResultDisplay from './components/ResultDisplay';
import ErrorDisplay from './components/ErrorDisplay';

// LOGIN PAGE
import Login from './pages/Login';

function CrawlerPage() {
  const crawler = useCrawler();

  const handleStartCrawl = async (request: CrawlRequest) => {
    await crawler.startCrawl(request);
  };

  const handleReset = () => {
    crawler.reset();
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <img src="/sitelogo.png" alt="CarVisor Logo" className="header-logo" />
          <div className="header-text">
            <h1>CarVisor</h1>
            <p>See Beyond the Listing</p>
          </div>
        </div>
      </header>

      <main className="app-main">
        {crawler.state === 'idle' && <CrawlForm onSubmit={handleStartCrawl} />}

        {crawler.state === 'loading' && crawler.jobId && (
          <LoadingState
            url={crawler.result?.url || 'Processing...'}
            progress={crawler.progress}
            statusMessage={crawler.statusMessage}
            elapsedSeconds={crawler.elapsedSeconds}
          />
        )}

        {crawler.state === 'completed' && crawler.result && (
          <ResultDisplay result={crawler.result} onNewCrawl={handleReset} />
        )}

        {crawler.state === 'failed' && crawler.error && (
          <ErrorDisplay error={crawler.error} onRetry={handleReset} />
        )}
      </main>

      <footer className="app-footer">
        <p>Built with React + FastAPI</p>
      </footer>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<CrawlerPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
