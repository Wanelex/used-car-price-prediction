import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import './App.css';

import { useCrawler } from './hooks/useCrawler';
import type { CrawlRequest, CarListing } from './api/crawlerApi';
import { logoutUser } from './services/authService';
import { useLanguage } from './i18n';

import CrawlForm from './components/CrawlForm';
import LoadingState from './components/LoadingState';
import ResultDisplay, { type TabType } from './components/ResultDisplay';
import ErrorDisplay from './components/ErrorDisplay';
import LanguageToggle from './components/LanguageToggle';

// PAGES
import Login from './pages/login';
import HomePage from './pages/HomePage';
import ProfilePage from './pages/ProfilePage';

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
  const location = useLocation();
  const [activeTab, setActiveTab] = useState<TabType>('analysis');
  const { t } = useLanguage();

  // Check if we have a listing from navigation state (from HomePage)
  useEffect(() => {
    const state = location.state as { listing?: CarListing } | null;
    if (state?.listing) {
      crawler.loadStoredListing(state.listing);
      // Clear the navigation state to prevent reloading on refresh
      window.history.replaceState({}, document.title);
    }
  }, []);

  const handleStartCrawl = async (request: CrawlRequest) => {
    await crawler.startCrawl(request);
  };

  const handleReset = () => {
    crawler.reset();
    setActiveTab('analysis');
  };

  const handleLogout = async () => {
    await logoutUser();
    navigate('/login');
  };

  const handleGoHome = () => {
    navigate('/');
  };

  const showNavTabs = crawler.state === 'completed' && crawler.result;

  return (
    <div className="app-container">
      <header className={`app-header ${showNavTabs ? 'with-wings' : ''}`}>
        {/* Left Wing - Navigation */}
        {showNavTabs && (
          <div className="header-wing left-wing">
            <button
              className={`wing-nav-btn ${activeTab === 'analysis' ? 'active' : ''}`}
              onClick={() => setActiveTab('analysis')}
            >
              {t.tabs.analysis}
            </button>
            <button
              className={`wing-nav-btn ${activeTab === 'listing' ? 'active' : ''}`}
              onClick={() => setActiveTab('listing')}
            >
              {t.tabs.listing}
            </button>
          </div>
        )}

        {/* Center - Logo & Brand */}
        <div className="header-center">
          <div className="header-content">
            <img src="/sitelogo.png" alt="CarVisor Logo" className="header-logo" />
            <div className="header-text">
              <h1>CarVisor</h1>
              <p>{t.brand.tagline}</p>
            </div>
          </div>
          <div className="header-actions">
            <LanguageToggle />
            <button className="header-action-button" onClick={handleGoHome} title={t.nav.home}>
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
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                <polyline points="9 22 9 12 15 12 15 22" />
              </svg>
              <span className="action-text">{t.nav.home}</span>
            </button>
            {crawler.state !== 'idle' && (
              <button className="header-action-button" onClick={handleReset} title={t.nav.startNewAnalysis}>
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
                  <line x1="12" y1="5" x2="12" y2="19" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                <span className="action-text">{t.nav.startNewAnalysis}</span>
              </button>
            )}
            <button className="header-action-button" onClick={handleLogout} title={t.nav.logout}>
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
              <span className="action-text">{t.nav.logout}</span>
            </button>
          </div>
        </div>

        {/* Right Wing - Navigation */}
        {showNavTabs && (
          <div className="header-wing right-wing">
            <button
              className={`wing-nav-btn ${activeTab === 'specs' ? 'active' : ''}`}
              onClick={() => setActiveTab('specs')}
            >
              {t.tabs.specs}
            </button>
            <button
              className={`wing-nav-btn ${activeTab === 'parts' ? 'active' : ''}`}
              onClick={() => setActiveTab('parts')}
            >
              {t.tabs.parts}
            </button>
          </div>
        )}
      </header>

      <main className="app-main">
        {crawler.state === 'idle' && <CrawlForm onSubmit={handleStartCrawl} />}

        {crawler.state === 'loading' && crawler.jobId && (
          <LoadingState
            url={crawler.result?.url || 'Processing...'}
            statusMessage={crawler.statusMessage}
            elapsedSeconds={crawler.elapsedSeconds}
          />
        )}

        {crawler.state === 'completed' && crawler.result && (
          <ResultDisplay
            result={crawler.result}
            activeTab={activeTab}
          />
        )}

        {crawler.state === 'failed' && crawler.error && (
          <ErrorDisplay error={crawler.error} onRetry={handleReset} />
        )}
      </main>

      <footer className="app-footer">
        <p>{t.nav.builtWith}</p>
        {showNavTabs && (
          <button
            className={`footer-metadata-btn ${activeTab === 'html' ? 'active' : ''}`}
            onClick={() => setActiveTab('html')}
            title={t.tabs.htmlMetadata}
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="16 18 22 12 16 6" />
              <polyline points="8 6 2 12 8 18" />
            </svg>
            <span>{t.tabs.htmlMetadata}</span>
          </button>
        )}
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
              <HomePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/crawl"
          element={
            <ProtectedRoute>
              <CrawlerPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
