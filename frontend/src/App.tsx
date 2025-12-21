import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import './App.css';

import { useCrawler } from './hooks/useCrawler';
import type { CrawlRequest } from './api/crawlerApi';
import { logoutUser } from '../services/authService';

import CrawlForm from './components/CrawlForm';
import LoadingState from './components/LoadingState';
import ResultDisplay from './components/ResultDisplay';
import ErrorDisplay from './components/ErrorDisplay';

// LOGIN PAGE
import Login from './pages/Login';

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
  }, []);

  if (isAuthenticated === null) {
    return <div>Loading...</div>;
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

function CrawlerPage() {
  const crawler = useCrawler();
  const navigate = useNavigate();

  const handleStartCrawl = async (request: CrawlRequest) => {
    await crawler.startCrawl(request);
  };

  const handleReset = () => {
    crawler.reset();
  };

  const handleLogout = async () => {
    await logoutUser();
    navigate('/login');
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
        <button className="logout-button" onClick={handleLogout} title="Logout">
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
        </button>
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
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <CrawlerPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
