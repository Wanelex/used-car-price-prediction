import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { onAuthStateChanged } from "firebase/auth";
import type { User } from "firebase/auth";
import { auth } from "../../lib/firebase";
import {
  logoutUser,
  deleteUserAccount,
  getUserProvider,
} from "../../services/authService";
import { useLanguage } from "../i18n";
import LanguageToggle from "../components/LanguageToggle";
import "./ProfilePage.css";

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { t } = useLanguage();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const handleLogout = async () => {
    await logoutUser();
    navigate("/login");
  };

  const handleGoHome = () => {
    navigate("/");
  };

  const handleNewCrawl = () => {
    navigate("/crawl");
  };

  const handleDeleteAccount = async () => {
    setError(null);
    setDeleting(true);

    try {
      const provider = getUserProvider();
      if (provider === "password" && !password) {
        setError("Please enter your password to confirm deletion");
        setDeleting(false);
        return;
      }

      await deleteUserAccount(provider === "password" ? password : undefined);
      navigate("/login");
    } catch (err: any) {
      setError(err.message || "Failed to delete account");
      setDeleting(false);
    }
  };

  const formatDate = (dateStr?: string | null) => {
    if (!dateStr) return t.common.na;
    const date = new Date(dateStr);
    return date.toLocaleDateString("tr-TR", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  };

  const getProviderName = () => {
    const provider = getUserProvider();
    if (provider === "google.com") return t.profile.providers.google;
    if (provider === "password") return t.profile.providers.emailPassword;
    return t.profile.providers.unknown;
  };

  const isGoogleUser = getUserProvider() === "google.com";

  if (loading) {
    return (
      <div className="profile-container">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>{t.profile.loadingProfile}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      {/* Header with Wings */}
      <header className="profile-header">
        {/* Left Wing - History */}
        <div className="header-wing left-wing">
          <button className="wing-nav-btn" onClick={handleGoHome}>
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
            {t.nav.history}
          </button>
        </div>

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
            <button className="header-action-button" onClick={handleNewCrawl} title={t.nav.startNewAnalysis}>
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

        {/* Right Wing - Profile (Active) */}
        <div className="header-wing right-wing">
          <button className="wing-nav-btn active">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            {t.nav.profile}
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="profile-main">
        <div className="profile-card">
          {/* Avatar Section */}
          <div className="profile-avatar-section">
            {user?.photoURL ? (
              <img src={user.photoURL} alt="Profile" className="profile-avatar" />
            ) : (
              <div className="profile-avatar-placeholder">
                <svg
                  width="48"
                  height="48"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                >
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </div>
            )}
            <h2 className="profile-name">{user?.displayName || t.profile.user}</h2>
            <p className="profile-email">{user?.email}</p>
          </div>

          {/* Profile Info */}
          <div className="profile-info-section">
            <div className="info-row">
              <div className="info-label">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                  <line x1="16" y1="2" x2="16" y2="6" />
                  <line x1="8" y1="2" x2="8" y2="6" />
                  <line x1="3" y1="10" x2="21" y2="10" />
                </svg>
                {t.profile.accountCreated}
              </div>
              <div className="info-value">{formatDate(user?.metadata.creationTime)}</div>
            </div>

            <div className="info-row">
              <div className="info-label">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <circle cx="12" cy="12" r="10" />
                  <polyline points="12 6 12 12 16 14" />
                </svg>
                {t.profile.lastSignIn}
              </div>
              <div className="info-value">{formatDate(user?.metadata.lastSignInTime)}</div>
            </div>

            <div className="info-row">
              <div className="info-label">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                </svg>
                {t.profile.signInMethod}
              </div>
              <div className="info-value provider-badge">
                {isGoogleUser && (
                  <svg width="16" height="16" viewBox="0 0 24 24">
                    <path
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      fill="#4285F4"
                    />
                    <path
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      fill="#34A853"
                    />
                    <path
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      fill="#FBBC05"
                    />
                    <path
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      fill="#EA4335"
                    />
                  </svg>
                )}
                {getProviderName()}
              </div>
            </div>

            <div className="info-row">
              <div className="info-label">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
                {t.profile.emailVerified}
              </div>
              <div className={`info-value ${user?.emailVerified ? "verified" : "not-verified"}`}>
                {user?.emailVerified ? t.common.yes : t.common.no}
              </div>
            </div>
          </div>

          {/* Danger Zone */}
          <div className="danger-zone">
            <h3>{t.profile.dangerZone}</h3>
            <p>{t.profile.deleteWarning}</p>
            <button
              className="delete-account-btn"
              onClick={() => setShowDeleteModal(true)}
            >
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <polyline points="3 6 5 6 21 6" />
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                <line x1="10" y1="11" x2="10" y2="17" />
                <line x1="14" y1="11" x2="14" y2="17" />
              </svg>
              {t.profile.deleteAccount}
            </button>
          </div>
        </div>
      </main>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="modal-overlay" onClick={() => setShowDeleteModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-icon">
                <svg
                  width="32"
                  height="32"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
              </div>
              <h3>{t.profile.deleteAccount}</h3>
              <p>{t.profile.deleteConfirm}</p>
            </div>

            {!isGoogleUser && (
              <div className="modal-input-group">
                <label>{t.profile.enterPassword}</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={t.profile.yourPassword}
                  disabled={deleting}
                />
              </div>
            )}

            {isGoogleUser && (
              <p className="modal-note">
                {t.profile.googleDeleteNote}
              </p>
            )}

            {error && <div className="modal-error">{error}</div>}

            <div className="modal-actions">
              <button
                className="modal-cancel-btn"
                onClick={() => {
                  setShowDeleteModal(false);
                  setPassword("");
                  setError(null);
                }}
                disabled={deleting}
              >
                {t.common.cancel}
              </button>
              <button
                className="modal-delete-btn"
                onClick={handleDeleteAccount}
                disabled={deleting}
              >
                {deleting ? t.profile.deleting : t.profile.deleteAccount}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="profile-footer">
        <p>{t.nav.builtWith}</p>
      </footer>
    </div>
  );
}
