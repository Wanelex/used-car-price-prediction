import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "../lib/firebase";
import { getListings, deleteListing, type CarListing } from "../api/crawlerApi";
import { logoutUser } from "../services/authService";
import { useLanguage } from "../i18n";
import LanguageToggle from "../components/LanguageToggle";
import "./HomePage.css";

export default function HomePage() {
  const [listings, setListings] = useState<CarListing[]>([]);
  const [filteredListings, setFilteredListings] = useState<CarListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [_authReady, setAuthReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  // Filter states
  const [filterBrand, setFilterBrand] = useState<string>('');
  const [filterMinPrice, setFilterMinPrice] = useState<number | null>(null);
  const [filterMaxPrice, setFilterMaxPrice] = useState<number | null>(null);
  const [filterMinYear, setFilterMinYear] = useState<number | null>(null);
  const [filterMaxYear, setFilterMaxYear] = useState<number | null>(null);
  const [filterMinScore, setFilterMinScore] = useState<number | null>(null);

  // Sort state
  const [sortBy, setSortBy] = useState<string>('date-desc'); // date-desc, price-asc, price-desc, year-asc, year-desc, mileage-asc, mileage-desc, score-asc, score-desc

  const navigate = useNavigate();
  const { t } = useLanguage();

  // Wait for Firebase Auth to be ready
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setAuthReady(true);
      if (user) {
        fetchListings();
      } else {
        setLoading(false);
        setError(t.home.pleaseLogin);
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

  // Apply filters and sorting whenever listings or filter states change
  useEffect(() => {
    let filtered = [...listings];

    // Apply filters
    if (filterBrand) {
      filtered = filtered.filter((l) =>
        (l.brand || "").toLowerCase().includes(filterBrand.toLowerCase())
      );
    }

    if (filterMinPrice !== null) {
      filtered = filtered.filter((l) => (l.price || 0) >= filterMinPrice);
    }

    if (filterMaxPrice !== null) {
      filtered = filtered.filter((l) => (l.price || 0) <= filterMaxPrice);
    }

    if (filterMinYear !== null) {
      filtered = filtered.filter((l) => (l.year || 0) >= filterMinYear);
    }

    if (filterMaxYear !== null) {
      filtered = filtered.filter((l) => (l.year || 0) <= filterMaxYear);
    }

    if (filterMinScore !== null) {
      filtered = filtered.filter((l) => {
        const score = (l as any).buyability_score?.score || 0;
        return score >= filterMinScore;
      });
    }

    // Apply sorting
    const sorted = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case "price-asc":
          return (a.price || 0) - (b.price || 0);
        case "price-desc":
          return (b.price || 0) - (a.price || 0);
        case "year-asc":
          return (a.year || 0) - (b.year || 0);
        case "year-desc":
          return (b.year || 0) - (a.year || 0);
        case "mileage-asc":
          return (a.mileage || 0) - (b.mileage || 0);
        case "mileage-desc":
          return (b.mileage || 0) - (a.mileage || 0);
        case "score-asc":
          return (
            ((a as any).buyability_score?.score || 0) -
            ((b as any).buyability_score?.score || 0)
          );
        case "score-desc":
          return (
            ((b as any).buyability_score?.score || 0) -
            ((a as any).buyability_score?.score || 0)
          );
        case "date-desc":
        default:
          return new Date(b.crawled_at || "").getTime() - new Date(a.crawled_at || "").getTime();
      }
    });

    setFilteredListings(sorted);
  }, [listings, filterBrand, filterMinPrice, filterMaxPrice, filterMinYear, filterMaxYear, filterMinScore, sortBy]);

  const formatPrice = (price?: number) => {
    if (!price) return t.common.na;
    return new Intl.NumberFormat("tr-TR", {
      style: "currency",
      currency: "TRY",
      maximumFractionDigits: 0,
    }).format(price);
  };

  const formatMileage = (mileage?: number) => {
    if (!mileage) return t.common.na;
    return new Intl.NumberFormat("tr-TR").format(mileage) + " km";
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return t.common.na;
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
            {t.nav.profile}
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="home-main">
        <div className="home-title-section">
          <h2>{t.home.analysisHistory}</h2>
          <p className="subtitle">{t.home.previouslyAnalyzed}</p>
        </div>

        {loading ? (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>{t.home.loadingListings}</p>
          </div>
        ) : error ? (
          <div className="error-container">
            <div className="error-icon">!</div>
            <h3>{t.home.errorLoading}</h3>
            <p>{error}</p>
            <button onClick={fetchListings} className="retry-button">
              {t.common.tryAgain}
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
            <h3>{t.home.noListingsYet}</h3>
            <p>{t.home.startAnalyzing}</p>
            <button onClick={handleNewCrawl} className="start-button">
              {t.nav.startNewAnalysis}
            </button>
          </div>
        ) : (
          <>
            {/* Filter and Sort Controls */}
            <div className="filter-sort-container">
              <button
                className="filter-toggle-btn"
                onClick={() => setShowFilters(!showFilters)}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="4" y1="6" x2="20" y2="6" />
                  <line x1="4" y1="12" x2="20" y2="12" />
                  <line x1="4" y1="18" x2="20" y2="18" />
                </svg>
                {t.home.filtersSort}
              </button>

              {/* Sort Control */}
              <select
                className="sort-select"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="date-desc">{t.home.sortOptions.newestFirst}</option>
                <option value="date-asc">{t.home.sortOptions.oldestFirst}</option>
                <option value="price-asc">{t.home.sortOptions.priceLowHigh}</option>
                <option value="price-desc">{t.home.sortOptions.priceHighLow}</option>
                <option value="year-desc">{t.home.sortOptions.yearNewest}</option>
                <option value="year-asc">{t.home.sortOptions.yearOldest}</option>
                <option value="mileage-asc">{t.home.sortOptions.mileageLowHigh}</option>
                <option value="mileage-desc">{t.home.sortOptions.mileageHighLow}</option>
                <option value="score-desc">{t.home.sortOptions.scoreHighLow}</option>
                <option value="score-asc">{t.home.sortOptions.scoreLowHigh}</option>
              </select>
            </div>

            {/* Filter Panel */}
            {showFilters && (
              <div className="filter-panel">
                <div className="filter-group">
                  <label>{t.home.filters.brand}</label>
                  <input
                    type="text"
                    placeholder={t.home.filters.brandPlaceholder}
                    value={filterBrand}
                    onChange={(e) => setFilterBrand(e.target.value)}
                  />
                </div>

                <div className="filter-row">
                  <div className="filter-group">
                    <label>{t.home.filters.minPrice}</label>
                    <input
                      type="number"
                      placeholder="Min"
                      value={filterMinPrice ?? ""}
                      onChange={(e) => setFilterMinPrice(e.target.value ? parseFloat(e.target.value) : null)}
                    />
                  </div>
                  <div className="filter-group">
                    <label>{t.home.filters.maxPrice}</label>
                    <input
                      type="number"
                      placeholder="Max"
                      value={filterMaxPrice ?? ""}
                      onChange={(e) => setFilterMaxPrice(e.target.value ? parseFloat(e.target.value) : null)}
                    />
                  </div>
                </div>

                <div className="filter-row">
                  <div className="filter-group">
                    <label>{t.home.filters.minYear}</label>
                    <input
                      type="number"
                      placeholder="Min"
                      value={filterMinYear ?? ""}
                      onChange={(e) => setFilterMinYear(e.target.value ? parseInt(e.target.value) : null)}
                    />
                  </div>
                  <div className="filter-group">
                    <label>{t.home.filters.maxYear}</label>
                    <input
                      type="number"
                      placeholder="Max"
                      value={filterMaxYear ?? ""}
                      onChange={(e) => setFilterMaxYear(e.target.value ? parseInt(e.target.value) : null)}
                    />
                  </div>
                </div>

                <div className="filter-group">
                  <label>{t.home.filters.minScore}</label>
                  <input
                    type="number"
                    placeholder={t.home.filters.scorePlaceholder}
                    min="0"
                    max="100"
                    value={filterMinScore ?? ""}
                    onChange={(e) => setFilterMinScore(e.target.value ? parseFloat(e.target.value) : null)}
                  />
                </div>

                <button
                  className="clear-filters-btn"
                  onClick={() => {
                    setFilterBrand("");
                    setFilterMinPrice(null);
                    setFilterMaxPrice(null);
                    setFilterMinYear(null);
                    setFilterMaxYear(null);
                    setFilterMinScore(null);
                  }}
                >
                  {t.home.filters.clearAll}
                </button>
              </div>
            )}

            {/* Results Count and Listings Grid */}
            {filteredListings.length === 0 ? (
              <div className="no-results">
                <p>{t.home.noMatch}</p>
              </div>
            ) : (
              <>
                <div className="results-info">
                  {t.home.showing.replace('{count}', String(filteredListings.length)).replace('{total}', String(listings.length))}
                </div>
                <div className="listings-grid">
                  {filteredListings.map((listing) => (
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
                  {/* Final Score Badge - Top Right */}
                  {(listing as any).buyability_score && (listing as any).buyability_score.score !== undefined ? (
                    <div
                      className={`quality-badge ${
                        (listing as any).buyability_score.score >= 70
                          ? "quality-high"
                          : (listing as any).buyability_score.score >= 50
                          ? "quality-medium"
                          : "quality-low"
                      }`}
                    >
                      <span className="quality-score">
                        {Math.round((listing as any).buyability_score.score)}
                      </span>
                      <span className="quality-label">{t.home.labels.final}</span>
                    </div>
                  ) : listing.data_quality_score ? (
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
                      <span className="quality-label">{t.home.labels.quality}</span>
                    </div>
                  ) : null}

                  {/* Final Score Badge - Top Left (Combined Score from 3 Approaches) */}
                  {(() => {
                    const bs = (listing as any).buyability_score;

                    // Try multiple ways to extract the score
                    let score: number | null = null;

                    if (typeof bs === 'number') {
                      score = bs;
                    } else if (bs && typeof bs === 'object') {
                      // Try different possible field names and structures
                      if (bs.score !== undefined && bs.score !== null) {
                        score = Number(bs.score);
                      } else if (bs.scores?.buyability_score !== undefined) {
                        score = Number(bs.scores.buyability_score);
                      } else if (bs.final_score !== undefined) {
                        score = Number(bs.final_score);
                      } else if (bs.buyability_score !== undefined) {
                        score = Number(bs.buyability_score);
                      }
                    }

                    // Validate score is a valid number
                    if (score !== null && !isNaN(score) && score >= 0 && score <= 100) {
                      return (
                        <div
                          className={`final-score-badge ${
                            score >= 70
                              ? "score-high"
                              : score >= 50
                              ? "score-medium"
                              : "score-low"
                          }`}
                          title={`Final Score: Combines Statistical (${(listing as any).statistical_analysis?.risk_score ? Math.round((listing as any).statistical_analysis.risk_score) : '?'}%), Mechanical (${(listing as any).llm_analysis?.scores?.mechanical_score ? Math.round((listing as any).llm_analysis.scores.mechanical_score) : '?'}%), & Crash Analysis (${(listing as any).crash_score_analysis?.score ? Math.round((listing as any).crash_score_analysis.score) : '?'}%)`}
                        >
                          <span className="score-number">{Math.round(score)}</span>
                          <span className="score-label">{t.home.labels.final}</span>
                        </div>
                      );
                    }

                    return (
                      <div className="final-score-badge score-pending" title="Analysis pending - Click to analyze">
                        <span className="score-number">—</span>
                        <span className="score-label">{t.home.labels.final}</span>
                      </div>
                    );
                  })()}
                </div>
                <div className="listing-content">
                  <h3 className="listing-title">{getCarTitle(listing)}</h3>
                  <div className="listing-price">{formatPrice(listing.price)}</div>
                  <div className="listing-info">
                    <div className="info-item">
                      <span className="info-label">{t.home.labels.year}</span> {listing.year || t.common.na}
                    </div>
                    <div className="info-item">
                      <span className="info-label">{t.home.labels.km}</span> {formatMileage(listing.mileage)}
                    </div>
                    <div className="info-item">
                      <span className="info-label">{t.home.labels.fuel}</span> {listing.fuel_type || t.common.na}
                    </div>
                    <div className="info-item">
                      <span className="info-label">{t.home.labels.trans}</span> {listing.transmission || t.common.na}
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
              </>
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="home-footer">
        <p>{t.nav.builtWith}</p>
      </footer>
    </div>
  );
}
