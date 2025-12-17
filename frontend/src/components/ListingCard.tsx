import React, { useMemo } from 'react';
import { CarListing } from '../api/listingsApi';
import '../styles/ListingCard.css';

interface ListingCardProps {
  listing: CarListing;
  onClick: () => void;
}

// Feature weights for health score calculation (same as model)
const FEATURE_WEIGHTS = {
  age: 0.25,
  km_per_year: 0.25,
  total_km: 0.20,
  model_year: 0.10,
  hp: 0.10,
  ccm: 0.10,
};

const CURRENT_YEAR = 2025;

// Extract numeric value from string (e.g., "231 hp" -> 231)
function extractNumeric(text: string | undefined): number | null {
  if (!text) return null;
  const match = text.match(/\d+/);
  return match ? parseInt(match[0], 10) : null;
}

// Calculate health score (same logic as model)
function calculateHealthScore(listing: CarListing): number | null {
  const year = listing.year;
  const km = listing.mileage;

  if (!year || !km) return null;

  const carAge = Math.max(CURRENT_YEAR - year, 1);
  const kmPerYear = km / carAge;

  // Parse HP and CCM from strings
  const hp = extractNumeric(listing.engine_power) || 100; // Default 100 HP
  const ccm = extractNumeric(listing.engine_volume) || 1500; // Default 1500 cc

  // Calculate individual scores (0-1 range)
  const ageScore = Math.max(0, Math.min(1, 1 - carAge / 20));
  const kmPerYearScore = Math.max(0, Math.min(1, 1 - kmPerYear / 30000));
  const kmScore = Math.max(0, Math.min(1, 1 - km / 400000));
  const yearScore = Math.max(0, Math.min(1, (year - 1959) / (CURRENT_YEAR - 1959)));
  const hpScore = Math.max(0, Math.min(1, (hp - 50) / 200));
  const ccmScore = Math.max(0, Math.min(1, 1 - Math.abs(ccm - 1450) / 1000));

  // Composite weighted score
  const healthScore =
    FEATURE_WEIGHTS.age * ageScore +
    FEATURE_WEIGHTS.km_per_year * kmPerYearScore +
    FEATURE_WEIGHTS.total_km * kmScore +
    FEATURE_WEIGHTS.model_year * yearScore +
    FEATURE_WEIGHTS.hp * hpScore +
    FEATURE_WEIGHTS.ccm * ccmScore;

  return Math.round(healthScore * 100);
}

// Get risk level class based on score
function getRiskLevelClass(score: number): string {
  if (score >= 71) return 'risk-low';
  if (score >= 51) return 'risk-moderate';
  return 'risk-high';
}

export default function ListingCard({ listing, onClick }: ListingCardProps) {
  // Calculate risk score using memoization
  const riskScore = useMemo(() => calculateHealthScore(listing), [listing]);
  // Format price
  const formattedPrice = new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(listing.price);

  // Format mileage
  const formattedMileage = new Intl.NumberFormat('tr-TR').format(listing.mileage || 0);

  // Build title from brand, series, model
  const title = `${listing.brand || ''} ${listing.series || ''} ${listing.model || ''}`.trim() || 'Bilinmeyen Araç';

  // Get first image URL if available
  const imageUrl = listing.images && listing.images.length > 0
    ? `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/data/images/${listing.images[0].path}`
    : null;

  return (
    <div className="listing-card" onClick={onClick}>
      <div className="listing-image">
        {imageUrl ? (
          <img src={imageUrl} alt={title} />
        ) : (
          <span>Görsel Yok</span>
        )}
        {/* Risk Score Badge */}
        {riskScore !== null && (
          <div className={`risk-badge ${getRiskLevelClass(riskScore)}`}>
            <span className="risk-score">{riskScore}</span>
            <span className="risk-label">Risk</span>
          </div>
        )}
      </div>
      <div className="listing-content">
        <div className="listing-title">{title}</div>
        <div className="listing-price">{formattedPrice}</div>
        <div className="listing-info">
          <div className="info-item">
            <span className="info-label">Yıl:</span> {listing.year || '-'}
          </div>
          <div className="info-item">
            <span className="info-label">KM:</span> {formattedMileage}
          </div>
          <div className="info-item">
            <span className="info-label">Yakıt:</span> {listing.fuel_type || '-'}
          </div>
          <div className="info-item">
            <span className="info-label">Vites:</span> {listing.transmission || '-'}
          </div>
        </div>
        {listing.location && (
          <div className="listing-location">{listing.location}</div>
        )}
      </div>
    </div>
  );
}
