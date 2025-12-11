import React from 'react';
import './App.css';
import { useCrawler } from './hooks/useCrawler';
import type { CrawlRequest } from './api/crawlerApi';
import CrawlForm from './components/CrawlForm';
import LoadingState from './components/LoadingState';
import ResultDisplay from './components/ResultDisplay';
import ErrorDisplay from './components/ErrorDisplay';

function App() {
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
        <h1>CarVisor</h1>
        <p>See Beyond the Listing</p>
      </header>

      <main className="app-main">
        {/* Idle State - Show Form */}
        {crawler.state === 'idle' && <CrawlForm onSubmit={handleStartCrawl} />}

        {/* Loading State */}
        {crawler.state === 'loading' && crawler.jobId && (
          <LoadingState
            url={crawler.result?.url || 'Processing...'}
            progress={crawler.progress}
            statusMessage={crawler.statusMessage}
            elapsedSeconds={crawler.elapsedSeconds}
          />
        )}

        {/* Success State */}
        {crawler.state === 'completed' && crawler.result && (
          <ResultDisplay result={crawler.result} onNewCrawl={handleReset} />
        )}

        {/* Error State */}
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

export default App;
