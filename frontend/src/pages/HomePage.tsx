import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "../../lib/firebase";
import { getListings, deleteListing, type CarListing } from "../api/crawlerApi";
import { logoutUser } from "../../services/authService";
import "./HomePage.css";

export default function HomePage() {
  const [listings, setListings] = useState<CarListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [authReady, setAuthReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const navigate = useNavigate();

  // Wait for Firebase Auth to be ready
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setAuthReady(true);
      if (user) {
        fetchListings();
      } else {
        setLoading(false);
        setError("Please log in to view your listings");
      }
    });

    return () => unsubscribe();
  }, []);

  const fetchListings = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getListings(50, 0);
      setListings(response.data || []);
    } catch (err: any) {
      setError(err.message || "Failed to load listings");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (listingId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this listing?")) return;

    try {
      setDeletingId(listingId);
      await deleteListing(listingId);
      setListings(listings.filter((l) => l.listing_id !== listingId));
    } catch (err: any) {
      alert(err.message || "Failed to delete listing");
    } finally {
      setDeletingId(null);
    }
  };

  const handleLogout = async () => {
    await logoutUser();
    navigate("/login");
  };

  const handleNewCrawl = () => {
    navigate("/crawl");
  };

  const formatPrice = (price?: number) => {
    if (!price) return "N/A";
    return new Intl.NumberFormat("tr-TR", {
      style: "currency",
      currency: "TRY",
      maximumFractionDigits: 0,
    }).format(price);
  };

  const formatMileage = (mileage?: number) => {
    if (!mileage) return "N/A";
    return new Intl.NumberFormat("tr-TR").format(mileage) + " km";
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return "N/A";
    const date = new Date(dateStr);
    return date.toLocaleDateString("tr-TR", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  };

  const getCarTitle = (listing: CarListing) => {
    const parts = [listing.brand, listing.series, listing.model].filter(Boolean);
    return parts.length > 0 ? parts.join(" ") : listing.title || "Unknown Vehicle";
  };

  const handleGoProfile = () => {
    navigate("/profile");
  };

  const handleCardClick = (listing: CarListing) => {
    navigate("/crawl", { state: { listing } });
  };

  return (
    <div className="home-container">
      {/* Header with Wings */}
      <header className="home-header with-wings">
        {/* Left Wing - History (Active) */}
        <div className="header-wing left-wing">
          <button className="wing-nav-btn active">
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
            History
          </button>
        </div>

        {/* Center - Logo & Brand */}
        <div className="header-center">
          <div className="header-content">
            <img src="/sitelogo.png" alt="CarVisor Logo" className="header-logo" />
            <div className="header-text">
              <h1>CarVisor</h1>
              <p>See Beyond the Listing</p>
            </div>
          </div>
          <div className="header-actions">
            <button className="header-action-button" onClick={handleNewCrawl} title="Start New Crawl">
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
              <span className="action-text">Start New Crawl</span>
            </button>
            <button className="header-action-button" onClick={handleLogout} title="Logout">
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
              <span className="action-text">Logout</span>
            </button>
          </div>
        </div>

        {/* Right Wing - Profile */}
        <div className="header-wing right-wing">
          <button className="wing-nav-btn" onClick={handleGoProfile}>
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
            Profile
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="home-main">
        <div className="home-title-section">
          <h2>Analysis History</h2>
          <p className="subtitle">Your previously analyzed car listings</p>
        </div>

        {loading ? (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Loading your listings...</p>
          </div>
        ) : error ? (
          <div className="error-container">
            <div className="error-icon">!</div>
            <h3>Error Loading Listings</h3>
            <p>{error}</p>
            <button onClick={fetchListings} className="retry-button">
              Try Again
            </button>
          </div>
        ) : listings.length === 0 ? (
          <div className="empty-container">
            <div className="empty-icon">
              <svg
                width="64"
                height="64"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <line x1="12" y1="8" x2="12" y2="16" />
                <line x1="8" y1="12" x2="16" y2="12" />
              </svg>
            </div>
            <h3>No Listings Yet</h3>
            <p>Start analyzing car listings to see them here</p>
            <button onClick={handleNewCrawl} className="start-button">
              Start New Crawl
            </button>
          </div>
        ) : (
          <div className="listings-grid">
            {listings.map((listing) => (
              <div
                key={listing.listing_id}
                className="listing-card clickable"
                onClick={() => handleCardClick(listing)}
              >
                <div className="listing-image">
                  {listing.images && listing.images.length > 0 ? (
                    <img
                      src={typeof listing.images[0] === 'string' ? listing.images[0] : listing.images[0].url}
                      alt={getCarTitle(listing)}
                    />
                  ) : (
                    <div className="no-image">No Image</div>
                  )}
                  {listing.data_quality_score && (
                    <div
                      className={`quality-badge ${
                        listing.data_quality_score >= 0.7
                          ? "quality-high"
                          : listing.data_quality_score >= 0.4
                          ? "quality-medium"
                          : "quality-low"
                      }`}
                    >
                      <span className="quality-score">
                        {Math.round(listing.data_quality_score * 100)}
                      </span>
                      <span className="quality-label">Score</span>
                    </div>
                  )}
                </div>
                <div className="listing-content">
                  <h3 className="listing-title">{getCarTitle(listing)}</h3>
                  <div className="listing-price">{formatPrice(listing.price)}</div>
                  <div className="listing-info">
                    <div className="info-item">
                      <span className="info-label">Year:</span> {listing.year || "N/A"}
                    </div>
                    <div className="info-item">
                      <span className="info-label">KM:</span> {formatMileage(listing.mileage)}
                    </div>
                    <div className="info-item">
                      <span className="info-label">Fuel:</span> {listing.fuel_type || "N/A"}
                    </div>
                    <div className="info-item">
                      <span className="info-label">Trans:</span> {listing.transmission || "N/A"}
                    </div>
                  </div>
                  <div className="listing-footer">
                    <span className="listing-date">
                      <svg
                        width="14"
                        height="14"
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
                      {formatDate(listing.crawled_at)}
                    </span>
                    <button
                      className="delete-button"
                      onClick={(e) => handleDelete(listing.listing_id, e)}
                      disabled={deletingId === listing.listing_id}
                      title="Delete listing"
                    >
                      {deletingId === listing.listing_id ? (
                        <div className="mini-spinner"></div>
                      ) : (
                        <svg
                          width="16"
                          height="16"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                        >
                          <polyline points="3 6 5 6 21 6" />
                          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                        </svg>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="home-footer">
        <p>Built with React + FastAPI</p>
      </footer>
    </div>
  );
}
