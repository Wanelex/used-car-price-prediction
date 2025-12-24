import { useState } from 'react';
import { type CarListing } from '../api/crawlerApi';
import ListingCard from './ListingCard';
import ListingDetail from './ListingDetail';
import '../styles/Dashboard.css';

interface DashboardProps {
  listings: CarListing[];
  stats: {
    total_listings: number;
    avg_price: number;
    avg_quality_score: number;
  } | null;
  loading: boolean;
  error: string | null;
  onStartCrawl: () => void;
  onLogout: () => void;
  onDeleteListing: (listingId: string) => Promise<boolean>;
  userEmail: string;
}

export default function Dashboard({
  listings,
  stats,
  loading,
  error,
  onStartCrawl,
  onLogout,
  onDeleteListing,
  userEmail,
}: DashboardProps) {
  const [selectedListing, setSelectedListing] = useState<CarListing | null>(null);

  if (error) {
    return (
      <div className="dashboard-error">
        <h2>Error Loading Listings</h2>
        <p>{error}</p>
      </div>
    );
  }

  const userInitial = userEmail.charAt(0).toUpperCase();
  const avgPrice = stats?.avg_price || 0;
  const avgQuality = stats?.avg_quality_score || 0;
  const totalListings = stats?.total_listings || 0;

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-top">
          <div className="header-user">
            <div className="user-avatar">{userInitial}</div>
            <div className="user-info">
              <h2>Welcome back!</h2>
              <p>{userEmail}</p>
            </div>
          </div>

          <div className="header-buttons">
            <button className="btn btn-primary" onClick={onStartCrawl}>
              📍 Start New Analysis
            </button>
            <button className="btn btn-logout" onClick={onLogout}>
              🚪 Logout
            </button>
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="stats-container">
            <div className="stat-card">
              <div className="stat-value">{totalListings}</div>
              <div className="stat-label">Total Listings</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">
                {new Intl.NumberFormat('tr-TR', {
                  style: 'currency',
                  currency: 'TRY',
                  minimumFractionDigits: 0,
                  maximumFractionDigits: 0,
                }).format(avgPrice)}
              </div>
              <div className="stat-label">Average Price</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{(avgQuality * 100).toFixed(0)}%</div>
              <div className="stat-label">Average Quality</div>
            </div>
          </div>
        )}
      </header>

      {/* Empty State */}
      {listings.length === 0 && !loading && (
        <div className="empty-state">
          <div className="empty-state-icon">🚗</div>
          <h2>No Listings Yet</h2>
          <p>You haven't analyzed any car listings yet. Start your first analysis!</p>
          <button className="btn btn-primary" onClick={onStartCrawl}>
            Start Your First Analysis
          </button>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading your listings...</p>
        </div>
      )}

      {/* Listings Grid */}
      {listings.length > 0 && !loading && (
        <div className="listings-container">
          <div className="listings-grid">
            {listings.map(listing => (
              <ListingCard
                key={listing.id}
                listing={listing}
                onClick={() => setSelectedListing(listing)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {selectedListing && (
        <ListingDetail
          listing={selectedListing}
          onClose={() => setSelectedListing(null)}
          onDelete={async () => {
            const success = await onDeleteListing(selectedListing.id || selectedListing.listing_id);
            if (success) {
              setSelectedListing(null);
            }
          }}
        />
      )}
    </div>
  );
}
